"""Build public source assets from an allowlist, excluding private local records."""
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
VERSION="0.2.0"
TOP={"README.md","SKILL.md","LICENSE","pyproject.toml",".gitignore","CHANGELOG.md"}
FOLDERS={"viralforecast","tests","schemas","docs","scripts",".github","examples"}
BINARIES={"examples/data/demo.mp4","examples/data/cover.png"}


def main():
    files={}
    paths=[ROOT/name for name in TOP]
    for folder in FOLDERS:
        paths.extend((ROOT/folder).rglob('*'))
    for path in sorted(paths):
        rel=path.relative_to(ROOT).as_posix()
        if not path.is_file() or (rel not in TOP and path.relative_to(ROOT).parts[0] not in FOLDERS):
            continue
        if not path.resolve().is_relative_to(ROOT):
            raise RuntimeError(f"Source escapes project directory: {rel}")
        if any(part in {"__pycache__",".cache",".git",".venv","models"} for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix in {".pyc",".pth",".bin",".safetensors",".exe",".zip",".whl"}:
            continue
        content=path.read_bytes()
        if rel not in BINARIES:
            try:
                text=content.decode('utf-8-sig')
            except UnicodeDecodeError as exc:
                raise RuntimeError(f"Unexpected binary asset: {rel}") from exc
            # Public source must not expose the developer machine's paths.
            for prefix in [str(ROOT).replace('\\','\\\\'),str(ROOT),str(ROOT).replace('\\','/')]:
                text=text.replace(prefix,'<workspace>')
            local_markers=["C:"+chr(92)+"Users"+chr(92),"C:"+"/Users/","sandbox."+"{"]
            if any(marker in text for marker in local_markers):
                raise RuntimeError(f"Local environment metadata detected: {rel}")
            if rel.startswith('examples/data/') and path.suffix=='.csv' and path.name not in {'empty.csv','invalid.csv'}:
                rows=list(csv.DictReader(io.StringIO(text)))
                if not rows or any(r.get('data_source')!='synthetic' for r in rows):
                    raise RuntimeError(f"Public CSV is not explicitly synthetic: {rel}")
            content=text.encode('utf-8')
        files[rel]=content
    needed={'viralforecast/trends.py','viralforecast/understanding.py','viralforecast/speech.py','docs/QUICKSTART.zh-CN.md','examples/data/synthetic_trends.csv'}
    if needed-set(files):
        raise RuntimeError('Missing required source assets: '+str(needed-set(files)))
    sha=lambda b:hashlib.sha256(b).hexdigest()
    manifest={"version":VERSION,"files":{n:sha(b) for n,b in files.items()},
              "excluded":"virtualenvs, model weights, private outputs and raw local validation logs"}
    files['RELEASE_MANIFEST.json']=json.dumps(manifest,indent=2).encode()
    dest=ROOT/'dist'
    dest.mkdir(exist_ok=True)
    archive=dest/f'viralforecast-skill-{VERSION}.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name,content in files.items():
            z.writestr(f'viralforecast-skill/{name}',content)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise RuntimeError('Release ZIP CRC verification failed')
    archive.with_suffix('.zip.sha256').write_text(f'{sha(archive.read_bytes())}  {archive.name}\n',encoding='utf-8')
    print(json.dumps({"archive":archive.name,"files":len(files),"sha256":sha(archive.read_bytes())}))


if __name__=='__main__':
    main()
