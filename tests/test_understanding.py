import json
import os
from pathlib import Path

import pytest

from viralforecast.common import ForecastError
from viralforecast.models import digest, require
from viralforecast.speech import transcribe
from viralforecast.understanding import ranking


def test_no_audio_abstains_without_model():
    assert transcribe(None,"missing")["status"]=="no_audio"


def test_integrity_and_traversal(tmp_path):
    p=tmp_path/"model.bin"
    p.write_bytes(b"test")
    manifest={"models":{"speech":{"path":".","files":{"model.bin":digest(p)}}}}
    (tmp_path/"manifest.json").write_text(json.dumps(manifest))
    assert require(tmp_path,"speech")[0]==tmp_path
    p.write_bytes(b"changed")
    with pytest.raises(ForecastError,match="modified"):
        require(tmp_path,"speech")
    manifest["models"]["speech"]["files"]={"../outside.bin":"wrong"}
    (tmp_path/"manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ForecastError):
        require(tmp_path,"speech")


def test_missing_model_manifest(tmp_path):
    with pytest.raises(ForecastError):
        require(tmp_path,"objects")


def test_uncertain_scores_and_ordering():
    out=ranking([.2,.35,.3,.15],["a","b","c","d"])
    assert out["status"]=="uncertain"
    assert [x["label"] for x in out["candidates"]]==["b","c","a"]
    with pytest.raises(ForecastError):
        ranking([float("nan")],["a"])


def test_asr_conflict_before_media(tmp_path):
    from viralforecast.analysis import analyze
    with pytest.raises(ForecastError,match="multiple"):
        analyze("missing.mp4",asr=True,transcript_path="x.json")


def test_vision_integration_dispatch(fixtures,tmp_path,monkeypatch):
    from viralforecast.analysis import analyze
    import viralforecast.understanding as module
    def fake(*args):
        return {"status":"test_double_only","objects":[],"actions":[]}
    monkeypatch.setattr(module,"understand",fake)
    result=analyze(fixtures/"demo.mp4",output=tmp_path,understand=True)
    assert result["media"]["visual_semantics"]=="local_models"
    from jsonschema import validate
    validate(result,json.loads((Path(__file__).parents[1]/"schemas/output.schema.json").read_text()))


@pytest.mark.skipif(not os.environ.get("VIRALFORECAST_MODELS"),reason="large local model weights not requested")
def test_real_model_inference(fixtures,tmp_path):
    from viralforecast.analysis import analyze
    result=analyze(fixtures/"demo.mp4",title="an abstract color video",output=tmp_path,
                   understand=True,asr=True,models_dir=os.environ["VIRALFORECAST_MODELS"])
    m=result["media"]
    assert m["understanding"]["status"]=="completed_local_models"
    assert m["understanding"]["objects"] and m["understanding"]["actions"]
    assert m["understanding"]["scene_semantics"]
    assert m["understanding"]["expressions"]["status"]=="no_face_detected"
    assert m["transcript"]["status"]=="built_in_local_asr"
    assert m["transcript"]["segments"]==[]  # sine wave is not speech
