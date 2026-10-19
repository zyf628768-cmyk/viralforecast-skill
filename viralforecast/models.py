"""Explicit download step; analysis never downloads weights or uploads media."""
import argparse
import hashlib
import json
from pathlib import Path

from .common import ForecastError, read_json

HF_MODELS = {"semantics": "openai/clip-vit-base-patch32", "expression": "trpakov/vit-face-expression",
             "speech": "Systran/faster-whisper-tiny"}


def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def require(directory, name):
    root=Path(directory).resolve()
    manifest=read_json(root/"manifest.json")
    entry=manifest.get("models",{}).get(name)
    if not entry:
        raise ForecastError(f"Missing local {name} model. Run python -m viralforecast.models --download --directory {directory}")
    target=(root/entry["path"]).resolve()
    if not target.is_relative_to(root) or not entry.get("files"):
        raise ForecastError(f"Invalid local {name} model manifest")
    for rel, expected in entry["files"].items():
        p=(root/rel).resolve()
        if not p.is_relative_to(root) or not p.is_file() or digest(p)!=expected:
            raise ForecastError(f"Missing or modified {name} model file: {rel}; download again")
    return target, entry


def download(directory):
    try:
        from huggingface_hub import HfApi, snapshot_download
        import torch
        from torchvision.models.detection import SSDLite320_MobileNet_V3_Large_Weights
        from torchvision.models.video import R3D_18_Weights
    except ImportError as exc:
        raise ForecastError('Install optional dependencies: pip install -e ".[understanding]"') from exc
    root=Path(directory).resolve()
    root.mkdir(parents=True,exist_ok=True)
    manifest={"models":{}}
    for name,weights in [("objects",SSDLite320_MobileNet_V3_Large_Weights.DEFAULT),("actions",R3D_18_Weights.KINETICS400_V1)]:
        print(f"Downloading {name}: {weights.url}",flush=True)
        state=torch.hub.load_state_dict_from_url(weights.url,model_dir=str(root/"torch-cache"),map_location="cpu",check_hash=True)
        target=root/f"{name}.pth"
        torch.save(state,target)
        manifest["models"][name]={"path":target.name,"source":weights.url,"files":{target.name:digest(target)}}
        (root/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    api=HfApi()
    for name,repo in HF_MODELS.items():
        info=api.model_info(repo)
        names={s.rfilename for s in info.siblings}
        if name=="speech":
            patterns=["config.json","model.bin","tokenizer.json","vocabulary.*","preprocessor_config.json"]
        else:
            weight="model.safetensors" if "model.safetensors" in names else "pytorch_model.bin"
            patterns=["*.json","*.txt",weight]
        print(f"Downloading {name}: {repo}@{info.sha}",flush=True)
        dest=root/name
        snapshot_download(repo,revision=info.sha,local_dir=str(dest),allow_patterns=patterns,max_workers=2)
        files={p.relative_to(root).as_posix():digest(p) for p in dest.rglob('*') if p.is_file() and '.cache' not in p.parts}
        manifest["models"][name]={"path":name,"source":repo,"revision":info.sha,"files":files}
        (root/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return manifest


def main():
    p=argparse.ArgumentParser(description="Explicitly download local open-source model weights; no media is sent")
    p.add_argument("--download",action="store_true",required=True)
    p.add_argument("--directory",default="models")
    args=p.parse_args()
    try:
        result=download(args.directory)
        print(json.dumps({"status":"ok","models":list(result["models"])}))
    except Exception as exc:
        p.exit(2,f"Model download failed: {exc}\n")


if __name__=="__main__":
    main()
