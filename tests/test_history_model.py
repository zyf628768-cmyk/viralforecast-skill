import copy
import csv
from datetime import timedelta

import pytest

from viralforecast.common import ForecastError
from viralforecast.history import FEATURES, eligible, load_history
from viralforecast.model import backtest, build, compare, forecast, quantile, temporal_blocks


def analysis(row):
    return {"kind":"analysis", "platform":"tiktok", "features":{k:row[k] for k in FEATURES}}


def test_embargo_strict(rows):
    r = rows[0]
    assert not eligible([r], r["published_at"] + timedelta(days=7))
    assert eligible([r], r["published_at"] + timedelta(days=7,seconds=1)) == [r]


def test_split_outcomes_mature(rows):
    a,b,c = temporal_blocks(rows)
    assert a[-1]["published_at"] + timedelta(days=7) < b[0]["published_at"]
    assert b[-1]["published_at"] + timedelta(days=7) < c[0]["published_at"]


def test_no_future_leakage(rows):
    cutoff = rows[180]["published_at"]
    first = forecast(rows, analysis(rows[180]), cutoff.isoformat(), "demo")
    changed = copy.deepcopy(rows)
    for r in changed[180:]:
        r["views_7d"] = 1e12
        r["views_24h"] = 1e11
    second = forecast(changed, analysis(rows[180]), cutoff.isoformat(), "demo")
    assert first["forecasts"] == second["forecasts"]
    assert first["audit"] == second["audit"]


def test_calibration_labels_not_used_for_point_fit(rows):
    f,a = build(rows, "views_7d")
    changed = copy.deepcopy(rows)
    for r in changed[int(len(rows)*.75):]:
        r["views_7d"] *= 100
    g,b = build(changed, "views_7d")
    assert f(rows[0])["point"] == g(rows[0])["point"]
    assert a["model"] == b["model"]
    assert f(rows[0])["interval"] != g(rows[0])["interval"]


def test_future_features_not_model_inputs(rows):
    infer, _ = build(rows, "views_7d")
    altered = dict(rows[0], views_7d=9e20, likes_7d=1e20)
    assert infer(rows[0]) == infer(altered)


def test_mode_a_no_unfounded_forecast(rows):
    out = forecast(rows[:20], analysis(rows[25]), "2026-10-19", "demo")
    assert out["mode"] == "A" and out["forecasts"] is None and out["probabilities"] is None


def test_probability_bounds_and_intervals(rows):
    out = forecast(rows, analysis(rows[-1]), "2026-10-19", "demo")
    assert out["mode"] == "B"
    assert out["data_source"] == "synthetic"
    for p in out["forecasts"].values():
        assert 0 <= p["interval"][0] <= p["point"] <= p["interval"][1]
        for e in p["events"].values():
            assert e["probability"] is None or 0 <= e["probability"] <= 1
    assert all(0<=v<=1 for v in out["rates"].values())


def test_rare_events_abstain(rows):
    changed = copy.deepcopy(rows)
    for r in changed:
        r["views_7d"] = 1000
    infer,_ = build(changed,"views_7d")
    assert infer(changed[0])["events"]["over_3x_median"]["probability"] is None


def test_baseline_wins_constant_data(rows):
    changed = copy.deepcopy(rows)
    for r in changed:
        r["views_7d"] = 0
    _,audit = build(changed,"views_7d")
    assert audit["model"] == "historical_median"


def test_quantile_finite_sample():
    assert quantile(range(20)) == 18


def test_backtest_untouched_future(rows):
    out = backtest(rows, step=20)
    assert out["status"] == "evaluated"
    assert out["metrics"]["views_7d"]["n"] == 7
    for p in out["predictions"]["views_7d"]:
        from viralforecast.common import date
        assert date(p["latest_history"]) + timedelta(days=7) < date(p["prediction_at"])
    assert "baseline_brier" in out["probability_metrics"]["views_7d"]["3"]


@pytest.mark.parametrize("step,start",[(0,120),(1,10),(-1,150)])
def test_invalid_backtest_config(rows,step,start):
    with pytest.raises(ForecastError):
        backtest(rows,step,start)


@pytest.mark.parametrize("file",["empty.csv","invalid.csv"])
def test_bad_csv(fixtures,file):
    with pytest.raises(ForecastError):
        load_history(fixtures/file,"demo","tiktok")


@pytest.mark.parametrize("column,value",[("views_7d","nan"),("duration_seconds","-1"),("published_at","bad"),("likes_7d","999999999")])
def test_invalid_values(fixtures,tmp_path,column,value):
    with open(fixtures / "synthetic_history.csv",newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        data = list(reader)
    data[0][column]=value
    p=tmp_path/"bad.csv"
    with p.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        w.writerows(data)
    with pytest.raises(ForecastError):
        load_history(p,"demo","tiktok")


def test_duplicate_id(fixtures,tmp_path):
    original = (fixtures/"synthetic_history.csv").read_text().splitlines()
    p=tmp_path/"duplicate.csv"
    p.write_text("\n".join(original+[original[1]]))
    with pytest.raises(ForecastError,match="duplicate"):
        load_history(p,"demo","tiktok")


def test_actual_maturity(rows):
    p=forecast(rows,analysis(rows[-1]),"2026-10-19","demo")
    actual={"account_id":"demo","platform":"tiktok","published_at":"2026-10-20","observed_at":"2026-10-21","views_24h":0,"views_7d":0}
    with pytest.raises(ForecastError,match="seven days"):
        compare(p,actual)
    actual["observed_at"]="2026-10-28"
    assert compare(p,actual)["errors"]["views_7d"]["absolute_percentage_error"] is None
