import copy
import csv
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import validate

from viralforecast.common import ForecastError
from viralforecast.trends import trends, similarity


@pytest.fixture
def trend_csv(tmp_path):
    source=Path(__file__).parents[1]/"examples/generate_trends.py"
    spec=importlib.util.spec_from_file_location("trend_example",source)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.generate(tmp_path/"trends.csv")


@pytest.fixture
def analysis():
    return {"kind":"analysis","platform":"tiktok","title":"视频开场技巧 video opening tips", "caption":"提升内容吸引力 how to improve an opening #video",
            "features":{"duration_seconds":60,"cut_rate":.05,"title_length":100},"scores":{"first_3_seconds":40}}


def rewrite(source,dest,transform):
    with open(source,newline="",encoding="utf-8") as f:
        r=csv.DictReader(f)
        fields=r.fieldnames
        rows=list(r)
    rows=transform(rows)
    with open(dest,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return dest


def test_similarity_chinese_and_english():
    values=similarity("视频开场 video opening",["视频开场技巧 video opening tips","猫咪日常 pets"])
    assert values[0]>.2 and values[1]==0


def test_measured_trends_and_actions(trend_csv,analysis):
    out=trends(trend_csv,analysis,"2026-10-19",7)
    assert out["status"]=="measured_sample" and out["data_source"]=="synthetic"
    assert out["coverage"]["similar_posts"]==24
    assert out["coverage"]["paired_windows"]==24
    assert out["heat"]["paired_window_momentum_ratio"]==pytest.approx(2)
    assert out["heat"]["internal_recommendation_exposure"] is None
    assert any(a.get("feature")=="duration_seconds" for a in out["improvements"])
    validate(out,json.loads((Path(__file__).parents[1]/"schemas/output.schema.json").read_text()))


def test_future_snapshots_do_not_change_estimates(trend_csv,analysis,tmp_path):
    base=trends(trend_csv,analysis,"2026-10-18",7)
    def change(rows):
        for r in rows:
            if r["observed_at"].startswith("2026-10-19"):
                r["views"]="99999999999"
                r["title"]="irrelevant future text"
        return rows
    altered=rewrite(trend_csv,tmp_path/"future.csv",change)
    other=trends(altered,analysis,"2026-10-18",7)
    assert base==other


def test_one_snapshot_never_means_recent_growth(trend_csv,analysis,tmp_path):
    p=rewrite(trend_csv,tmp_path/"single.csv",lambda rows:[r for r in rows if r["observed_at"].startswith("2026-10-19")])
    out=trends(p,analysis,"2026-10-19")
    assert out["status"]=="insufficient_velocity_samples"
    assert out["heat"]["relative_heat_ratio"] is None
    assert all(p["recent_velocity"] is None for p in out["similar_content"])


def test_account_filter_and_platform_isolation(trend_csv,analysis):
    out=trends(trend_csv,analysis,"2026-10-19",exclude_account="peer-0")
    assert all(p["account_id"]!="peer-0" for p in out["similar_content"])
    other=copy.deepcopy(analysis)
    other["platform"]="douyin"
    with pytest.raises(ForecastError,match="No eligible"):
        trends(trend_csv,other,"2026-10-19")


def test_bad_csv_and_duplicates(trend_csv,analysis,tmp_path):
    empty=tmp_path/"empty.csv"
    empty.touch()
    with pytest.raises(ForecastError):
        trends(empty,analysis,"2026-10-19")
    p=rewrite(trend_csv,tmp_path/"duplicates.csv",lambda rows:rows+[rows[0]])
    with pytest.raises(ForecastError,match="Duplicate"):
        trends(p,analysis,"2026-10-19")


def test_negative_counter_correction_abstains(trend_csv,analysis,tmp_path):
    def change(rows):
        for r in rows:
            if r["observed_at"].startswith("2026-10-19"):
                r["views"]="0"
        return rows
    p=rewrite(trend_csv,tmp_path/"corrected.csv",change)
    out=trends(p,analysis,"2026-10-19")
    assert out["heat"]["relative_heat_ratio"] is None
    assert out["coverage"]["similar_with_velocity"]==0


def test_cli_reports_and_analysis_attachment(trend_csv,fixtures,tmp_path):
    from test_media_cli import cli
    a=tmp_path/"a"
    cli("analyze","--video",fixtures/"demo.mp4","--title","视频开场技巧 video opening tips","--trends-csv",trend_csv,
        "--as-of","2026-10-19","--out",a)
    saved=json.loads((a/"analysis.json").read_text(encoding="utf-8"))
    assert saved["trend_context"]["coverage"]["similar_posts"]>=20
    out=tmp_path/"trends"
    cli("trends","--csv",trend_csv,"--analysis",a/"analysis.json","--as-of","2026-10-19","--out",out)
    for ext in ("json","md","html"):
        assert (out/f"trends.{ext}").stat().st_size>100
    cli("report","--input",out/"trends.json","--out",tmp_path/"rerender")
