from viralforecast.model import backtest, coherent_horizons, forecast
from viralforecast.history import FEATURES


def test_horizon_adjustment():
    pair={"views_24h":{"point":200,"interval":[10,300]}, "views_7d":{"point":100,"interval":[20,150]}}
    assert coherent_horizons(pair)
    assert pair["views_7d"]["point"]==200 and pair["views_7d"]["interval"][1]==200


def test_backtest_matches_prediction_serving(rows):
    result=backtest(rows,step=200)
    target=rows[120]
    a={"kind":"analysis","platform":"tiktok","features":{k:target[k] for k in FEATURES}}
    pred=forecast(rows,a,target["published_at"].isoformat(),"demo")
    for key in ("views_24h","views_7d"):
        test=result["predictions"][key][0]
        assert test["prediction"]==pred["forecasts"][key]["point"]
        assert test["interval"]==pred["forecasts"][key]["interval"]


def test_event_threshold_is_mature_account_median(rows):
    import numpy as np
    a={"kind":"analysis","platform":"tiktok","features":{k:rows[0][k] for k in FEATURES}}
    p=forecast(rows,a,"2026-10-19","demo")
    for key in ("views_24h","views_7d"):
        assert p["forecasts"][key]["events"]["over_3x_median"]["threshold_views"]==3*np.median([r[key] for r in rows])


def test_dense_dates_downgrade_after_embargo(rows):
    import copy
    changed=copy.deepcopy(rows)
    for r in changed:
        r["published_at"]=rows[0]["published_at"]
    a={"kind":"analysis","platform":"tiktok","features":{k:rows[0][k] for k in FEATURES}}
    p=forecast(changed,a,"2026-10-19","demo")
    assert p["mode"]=="A" and p["status"]=="insufficient_temporal_separation"
    assert p["forecasts"] is None
