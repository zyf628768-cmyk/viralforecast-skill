"""Small, inspectable temporal model; calibration and evaluation remain separate."""
import math
from datetime import timedelta

import numpy as np

from .common import ForecastError, date, envelope, number
from .history import COUNTS, FEATURES, TARGETS, eligible, provenance

MIN_ROWS = 120
ALPHA = 0.10


def matrix(rows):
    return np.asarray([[number(r.get(k), k, .001 if k == "duration_seconds" else 0) for k in FEATURES] for r in rows], dtype=float)


def fit_ridge(rows, key):
    x = matrix(rows)
    mean, scale = x.mean(axis=0), x.std(axis=0)
    scale[scale < 1e-8] = 1
    z = np.column_stack([np.ones(len(x)), (x - mean) / scale])
    penalty = np.eye(z.shape[1]) * 10
    penalty[0, 0] = 0
    weights = np.linalg.solve(z.T @ z + penalty, z.T @ np.log1p([r[key] for r in rows]))
    return lambda rs: np.clip(np.column_stack([np.ones(len(rs)), (matrix(rs) - mean) / scale]) @ weights, 0, 30)


def quantile(scores, alpha=ALPHA):
    # Split conformal finite-sample order statistic; no interpolation.
    s = sorted(float(x) for x in scores)
    rank = math.ceil((len(s) + 1) * (1 - alpha))
    return s[min(rank, len(s)) - 1]


def temporal_blocks(rows):
    a, b = int(len(rows) * .5), int(len(rows) * .75)
    selection, calibration = rows[a:b], rows[b:]
    train = eligible(rows[:a], selection[0]["published_at"])
    selection = eligible(selection, calibration[0]["published_at"])
    if min(len(train), len(selection), len(calibration)) < 20:
        raise ForecastError("Temporal blocks too small after seven-day embargo")
    return train, selection, calibration


def build(rows, key):
    train, selection, calibration = temporal_blocks(rows)
    baseline = float(np.median([r[key] for r in train]))
    base_log = math.log1p(baseline)
    ridge = fit_ridge(train, key)
    ysel = np.asarray([r[key] for r in selection])
    ridge_mae = float(np.mean(abs(np.expm1(ridge(selection)) - ysel)))
    baseline_mae = float(np.mean(abs(baseline - ysel)))
    chosen = "ridge_log1p" if ridge_mae < baseline_mae else "historical_median"
    infer = ridge if chosen == "ridge_log1p" else lambda rs: np.full(len(rs), base_log)
    residuals = np.log1p(ysel) - infer(selection)
    cal_log = infer(calibration)
    ycal = np.asarray([r[key] for r in calibration])
    q = quantile(abs(np.log1p(ycal) - cal_log))

    def raw_probability(logpoint, threshold):
        return float((np.sum(residuals > math.log1p(threshold) - logpoint) + 1) / (len(residuals) + 2))

    events = {}
    for multiple in (3, 5):
        # Calibrate the same rolling-median event used at inference. For each
        # calibration label its reference median uses only already mature posts.
        threshold = float(np.median([r[key] for r in rows])) * multiple
        cal_thresholds = [float(np.median([r[key] for r in eligible(rows, c["published_at"])])) * multiple for c in calibration]
        labels = ycal > np.asarray(cal_thresholds)
        raw = np.asarray([raw_probability(v, t) for v,t in zip(cal_log, cal_thresholds)])
        # Fixed bins; smoothing toward a training-only event-frequency prior.
        prior = (sum(r[key] > baseline * multiple for r in train) + 1) / (len(train) + 2)
        bins = []
        for lo, hi in ((0, 1/3), (1/3, 2/3), (2/3, 1.000001)):
            mask = (raw >= lo) & (raw < hi)
            count = int(mask.sum())
            bins.append({"lower": lo, "upper": min(hi, 1), "n": count,
                         "probability": float((labels[mask].sum() + 5 * prior) / (count + 5))})
        events[multiple] = {"threshold": threshold, "prior": prior, "bins": bins,
                            "positive_count": int(labels.sum()), "negative_count": int((~labels).sum())}

    def predict(features):
        point_log = float(infer([features])[0])
        event_results = {}
        for mult, event in events.items():
            raw = raw_probability(point_log, event["threshold"])
            b = event["bins"][min(2, int(raw * 3))]
            supported = event["positive_count"] >= 5 and event["negative_count"] >= 5 and b["n"] >= 10
            event_results[f"over_{mult}x_median"] = {
                "threshold_views": event["threshold"], "probability": b["probability"] if supported else None,
                "raw_probability_diagnostic": raw, "baseline_probability": event["prior"],
                "status": "binned_calibrated_estimate" if supported else "insufficient_calibration_events_or_bin_support",
                "calibration_positives": event["positive_count"], "calibration_negatives": event["negative_count"],
                "bin_samples": b["n"]}
        return {"point": float(np.expm1(point_log)),
                "interval": [float(np.expm1(max(0, point_log - q))), float(np.expm1(min(30, point_log + q)))],
                "nominal_coverage": 1 - ALPHA, "historical_median_baseline": baseline, "events": event_results}
    audit = {"model": chosen, "selection_mae": {"ridge": ridge_mae, "median": baseline_mae},
             "split_counts": [len(train), len(selection), len(calibration)],
             "train_latest": train[-1]["published_at"].isoformat(),
             "selection_earliest": selection[0]["published_at"].isoformat(),
             "selection_latest": selection[-1]["published_at"].isoformat(),
             "calibration_earliest": calibration[0]["published_at"].isoformat(),
             "calibration_latest": calibration[-1]["published_at"].isoformat(),
             "event_reference_median": float(np.median([r[key] for r in rows])),
             "calibration_bins": {str(k): v for k, v in events.items()}}
    return predict, audit


def forecast(rows, analysis, as_of, account):
    if analysis.get("kind") != "analysis" or not isinstance(analysis.get("features"), dict):
        raise ForecastError("Prediction input must be an analysis JSON")
    matrix([analysis["features"]])
    cutoff = date(as_of)
    past = eligible(rows, cutoff)
    common = {"as_of": cutoff.isoformat(), "account_id": account, "platform": analysis["platform"],
              "eligible_rows": len(past), "excluded_immature_or_future_rows": len(rows) - len(past),
              "data_source": provenance(past), "analysis": analysis}
    if len(past) < MIN_ROWS:
        return envelope("prediction", mode="A", status="insufficient_history", minimum_rows=MIN_ROWS,
                        **common, forecasts=None, probabilities=None,
                        limitations=["No numeric views or event probabilities released with insufficient history."])
    try:
        temporal_blocks(past)
    except ForecastError as exc:
        return envelope("prediction", mode="A", status="insufficient_temporal_separation", **common,
                        forecasts=None, probabilities=None, limitations=[str(exc)])
    predictions, audits = {}, {}
    for key in TARGETS:
        predict, audit = build(past, key)
        predictions[key], audits[key] = predict(analysis["features"]), audit
    adjustment = coherent_horizons(predictions)
    out_of_range = [k for k in FEATURES if not min(r[k] for r in past) <= analysis["features"][k] <= max(r[k] for r in past)]
    rates = {}
    nonzero = [r for r in past if r["views_7d"] > 0]
    for k in COUNTS:
        rates[k.replace("_7d", "_rate_7d")] = float(np.mean([r[k] / r["views_7d"] for r in nonzero])) if nonzero else None
    return envelope("prediction", mode="B", status="experimental_statistical_estimate", **common,
                    forecasts=predictions, audit=audits, rates=rates, horizon_point_adjusted=adjustment,
                    features_outside_history_range=out_of_range,
                    limitations=["Intervals target 90% coverage under exchangeability; temporal drift can invalidate coverage.",
                                 "Binned calibration is sample-limited; null probabilities mean insufficient support.",
                                 "Rates are per-post historical means, not causal content-specific estimates.",
                                 "Out-of-range features can make estimates unreliable; inspect features_outside_history_range.",
                                 "Synthetic data demonstrates software behavior only, never commercial accuracy.",
                                 "Run backtest for untouched sample-outside-fit evaluation; calibration-set scores are not test scores."])


def coherent_horizons(predictions):
    """Apply identical horizon postprocessing in serving and temporal evaluation."""
    p24, p7 = predictions["views_24h"], predictions["views_7d"]
    adjusted = p7["point"] < p24["point"]
    if adjusted:
        p7["point"] = p24["point"]
        p7["interval"][1] = max(p7["interval"][1], p7["point"])
    return adjusted


def metrics(points):
    if not points:
        return None
    actual = np.asarray([p["actual"] for p in points])
    pred = np.asarray([p["prediction"] for p in points])
    base = np.asarray([p["baseline"] for p in points])
    error = pred - actual
    return {"n": len(points), "mae": float(abs(error).mean()), "rmse": float(np.sqrt((error ** 2).mean())),
            "wape": float(abs(error).sum() / actual.sum()) if actual.sum() else None,
            "median_baseline_mae": float(abs(base - actual).mean()),
            "beats_median_baseline_mae": bool(abs(error).mean() < abs(base - actual).mean()),
            "interval_coverage": float(np.mean([p["interval"][0] <= p["actual"] <= p["interval"][1] for p in points])),
            "mean_interval_width": float(np.mean([p["interval"][1] - p["interval"][0] for p in points]))}


def probability_metrics(points, multiple):
    usable = [p["events"][f"over_{multiple}x_median"] | {"actual_views": p["actual"]} for p in points
              if p["events"][f"over_{multiple}x_median"]["probability"] is not None]
    if not usable:
        return {"n": 0, "status": "no_supported_probabilities", "brier": None, "reliability": []}
    y = np.asarray([p["actual_views"] > p["threshold_views"] for p in usable], dtype=float)
    pr = np.asarray([p["probability"] for p in usable])
    bp = np.asarray([p["baseline_probability"] for p in usable])
    bins, ece = [], 0.0
    for lo in np.arange(0, 1, .2):
        mask = (pr >= lo) & (pr < lo + .2 + (1e-9 if lo >= .8 else 0))
        if mask.any():
            delta = abs(pr[mask].mean() - y[mask].mean())
            ece += mask.sum() / len(y) * delta
            bins.append({"n": int(mask.sum()), "mean_probability": float(pr[mask].mean()), "observed_frequency": float(y[mask].mean())})
    return {"n": len(y), "coverage_of_test_cases": len(y) / len(points),
            "brier": float(np.mean((pr-y)**2)), "baseline_brier": float(np.mean((bp-y)**2)),
            "ece_5_bins": float(ece), "reliability": bins}


def backtest(rows, step=1, start=MIN_ROWS):
    if step < 1 or start < MIN_ROWS:
        raise ForecastError(f"step must be >=1 and start >= {MIN_ROWS}")
    results = {k: [] for k in TARGETS}
    skipped = 0
    for i in range(start, len(rows), step):
        target = rows[i]
        past = eligible(rows[:i], target["published_at"])
        if len(past) < MIN_ROWS:
            skipped += 1
            continue
        try:
            temporal_blocks(past)
        except ForecastError:
            skipped += 1
            continue
        pair, audits = {}, {}
        for key in TARGETS:
            infer, audit = build(past, key)
            pair[key], audits[key] = infer(target), audit
        adjusted = coherent_horizons(pair)
        for key in TARGETS:
            out, audit = pair[key], audits[key]
            results[key].append({"content_id": target["content_id"], "prediction_at": target["published_at"].isoformat(),
                                 "latest_history": past[-1]["published_at"].isoformat(), "actual": target[key],
                                 "prediction": out["point"], "baseline": out["historical_median_baseline"],
                                 "interval": out["interval"], "events": out["events"], "model": audit["model"],
                                 "horizon_point_adjusted": adjusted})
    return envelope("backtest", status="evaluated" if results["views_7d"] else "insufficient_history",
                    data_source=provenance(rows), step=step, skipped=skipped,
                    metrics={k: metrics(v) for k,v in results.items()},
                    probability_metrics={k: {str(m): probability_metrics(v,m) for m in (3,5)} for k,v in results.items()},
                    predictions=results, limitations=["Expanding-origin temporal test; repeated model fits use only mature earlier labels.",
                                                     "Event thresholds use mature historical medians and vary by origin; cases are not independent.",
                                                     "No synthetic benchmark establishes real-world predictive accuracy."])


def compare(prediction, actual):
    if prediction.get("mode") != "B" or not prediction.get("forecasts"):
        raise ForecastError("compare requires a mode B statistical prediction")
    if actual.get("account_id") != prediction["account_id"] or actual.get("platform") != prediction["platform"]:
        raise ForecastError("Actual account/platform must match prediction")
    published = date(actual.get("published_at"))
    if published < date(prediction["as_of"]):
        raise ForecastError("Actual publication precedes prediction as_of")
    if date(actual.get("observed_at")) < published + timedelta(days=7):
        raise ForecastError("Actual observations must be at least seven days after publication")
    changes = {}
    for key in TARGETS:
        y = number(actual.get(key), key)
        p = prediction["forecasts"][key]
        changes[key] = {"actual": y, "predicted": p["point"], "signed_error": p["point"]-y,
                        "absolute_error": abs(p["point"]-y), "absolute_percentage_error": abs(p["point"]-y)/y if y else None,
                        "within_interval": p["interval"][0] <= y <= p["interval"][1]}
    if changes["views_7d"]["actual"] < changes["views_24h"]["actual"]:
        raise ForecastError("Actual views_7d must be >= views_24h")
    rate_errors = {}
    for k in COUNTS:
        if k in actual:
            count = number(actual[k], k, upper=changes["views_7d"]["actual"])
            rate = count / changes["views_7d"]["actual"] if changes["views_7d"]["actual"] else None
            key = k.replace("_7d", "_rate_7d")
            pred = prediction.get("rates", {}).get(key)
            rate_errors[key] = {"actual": rate, "predicted": pred,
                                "absolute_error": abs(rate-pred) if rate is not None and pred is not None else None}
    return envelope("comparison", account_id=prediction["account_id"], platform=prediction["platform"], errors=changes,
                    rate_errors=rate_errors,
                    data_source="synthetic" if prediction.get("data_source") == "synthetic" or actual.get("data_source") == "synthetic" else "user_declared_unverified",
                    limitations=["One-post errors do not establish model quality; use temporal backtest across many posts."])
