import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from jsonschema import validate

from viralforecast.analysis import analyze, rules
from viralforecast.common import ForecastError
from viralforecast.media import binary, inspect_video, transcript
from viralforecast.reporting import write_reports


def cli(*args, ok=True, env=None):
    p=subprocess.run([sys.executable,"-m","viralforecast",*map(str,args)],capture_output=True,text=True,env=env)
    assert p.returncode == (0 if ok else 2), p.stderr
    return json.loads(p.stdout if ok else p.stderr)


def schema(data):
    path=Path(__file__).parents[1]/"schemas/output.schema.json"
    validate(data,json.loads(path.read_text()))


@pytest.mark.parametrize("platform",["tiktok","youtube-shorts","instagram-reels","douyin","kuaishou","xiaohongshu","bilibili"])
def test_platforms(platform):
    assert rules(platform)["ideal_duration"] > 0


def test_rule_override(tmp_path):
    p=tmp_path/"rules.json"
    p.write_text('{"ideal_duration": 15}')
    assert rules("tiktok",p)["ideal_duration"]==15
    p.write_text('{"cut_target": 0}')
    with pytest.raises(ForecastError):
        rules("tiktok",p)


def test_video_metadata_and_no_semantics(fixtures,tmp_path):
    m=inspect_video(fixtures/"demo.mp4",tmp_path,fixtures/"transcript.json",cover=fixtures/"cover.png")
    assert 5.9<m["duration_seconds"]<6.2
    assert m["width"]==180 and m["height"]==320
    assert any(2.9<t<3.2 for t in m["scene_times"])
    assert len(m["keyframes"])>=3
    assert all(Path(f["path"]).stat().st_size>0 for f in m["keyframes"])
    assert Path(m["audio_path"]).stat().st_size>100
    assert m["visual_semantics"]=="not_implemented"
    assert m["transcript"]["status"]=="imported"


def test_missing_dependencies(monkeypatch):
    monkeypatch.setenv("FFPROBE",str(Path("definitely-missing.exe").resolve()))
    with pytest.raises(ForecastError,match="missing executable"):
        binary("ffprobe")
    monkeypatch.setenv("FFMPEG",str(Path("definitely-missing.exe").resolve()))
    with pytest.raises(ForecastError):
        binary("ffmpeg")


def test_empty_video(tmp_path):
    p=tmp_path/"empty.mp4"
    p.touch()
    with pytest.raises(ForecastError,match="empty"):
        inspect_video(p,tmp_path/"out")


def test_corrupt_video(tmp_path):
    p=tmp_path/"corrupt.mp4"
    p.write_bytes(b"not a media file")
    with pytest.raises(ForecastError,match="failed"):
        inspect_video(p,tmp_path/"out")


def test_transcript_validation(tmp_path):
    p=tmp_path/"t.json"
    p.write_text('{"segments":[{"start":2,"end":1,"text":"x"}]}')
    with pytest.raises(ForecastError):
        transcript(p)
    with pytest.raises(ForecastError,match="adapter failed"):
        transcript(adapter="does_not_exist:transcribe",audio="x.wav")


def test_local_transcriber(tmp_path,monkeypatch):
    (tmp_path/"local_asr.py").write_text('def transcribe(audio):\n return {"segments":[{"start":0,"end":1,"text":"local test"}]}\n')
    monkeypatch.syspath_prepend(str(tmp_path))
    assert transcript(adapter="local_asr:transcribe",audio="test.wav",duration=2)["status"]=="local_adapter"


def test_html_injection(tmp_path):
    data={"schema_version":"1.0","kind":"analysis","title":"<script>alert(1)</script>```"}
    p=write_reports(data,tmp_path)
    html=Path(p["html"]).read_text(encoding="utf-8")
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert Path(p["md"]).read_text(encoding="utf-8").count("```")==2


def test_cli_end_to_end(fixtures,tmp_path):
    a=tmp_path/"a"
    cli("analyze","--video",fixtures/"demo.mp4","--title","How? <script>","--caption","Try #demo", "--transcript", fixtures/"transcript.json","--cover",fixtures/"cover.png","--out",a)
    data=json.loads((a/"analysis.json").read_text(encoding="utf-8"))
    schema(data)
    assert data["mode"]=="A" and "forecasts" not in data
    b=tmp_path/"b"
    cli("predict","--analysis",a/"analysis.json","--history",fixtures/"synthetic_history.csv","--account","demo","--platform","tiktok","--as-of","2026-10-19","--out",b)
    pred=json.loads((b/"prediction.json").read_text(encoding="utf-8"))
    schema(pred)
    assert pred["mode"]=="B"
    c=tmp_path/"c"
    cli("compare","--prediction",b/"prediction.json","--actual",fixtures/"actual.json","--out",c)
    d=tmp_path/"d"
    cli("backtest","--history",fixtures/"synthetic_history.csv","--account","demo","--platform","tiktok","--step","20","--out",d)
    e=tmp_path/"e"
    cli("report","--input",b/"prediction.json","--out",e)
    for folder,kind in ((a,"analysis"),(b,"prediction"),(c,"comparison"),(d,"backtest"),(e,"prediction")):
        for ext in ("json","md","html"):
            assert (folder/f"{kind}.{ext}").stat().st_size>50
        schema(json.loads((folder/f"{kind}.json").read_text(encoding="utf-8")))
    for file in ("invalid.csv","empty.csv"):
        result=cli("backtest","--history",fixtures/file,"--account","demo","--platform","tiktok","--out",tmp_path/"bad",ok=False)
        assert result["status"]=="error"
    env=dict(os.environ,FFPROBE=str(tmp_path/"missing.exe"))
    result=cli("analyze","--video",fixtures/"demo.mp4","--out",tmp_path/"missing",env=env,ok=False)
    assert "FFPROBE" in result["message"]
