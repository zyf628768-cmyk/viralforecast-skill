"""Build a whitelist-only source release; no virtualenv or downloaded binaries."""
import hashlib
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    from viralforecast import __version__
    target = ROOT / f'dist/viralforecast-skill-{__version__}.zip'
    target.parent.mkdir(exist_ok=True)
    allowed = ['viralforecast','tests','schemas','docs','scripts','.github','examples','validation']
    top = ['README.md','SKILL.md','LICENSE','pyproject.toml','.gitignore','CHANGELOG.md']
    files = [(ROOT / p, p) for p in top]
    for folder in allowed:
        files.extend((p,p.relative_to(ROOT).as_posix()) for p in (ROOT/folder).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.exe','.zip'))
    # Include only this project's explicitly synthetic demo, never arbitrary outputs.
    for p in (ROOT/'outputs/demo').rglob('*'):
        if p.is_file():
            files.append((p, 'reports/demo/' + p.relative_to(ROOT/'outputs/demo').as_posix()))
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for path, name in sorted(files,key=lambda x:x[1]):
            if path.is_file():
                z.write(path,'viralforecast-skill/' + name)
    with zipfile.ZipFile(target) as z:
        assert z.testzip() is None
        assert all('/.venv/' not in n and not n.endswith('.exe') for n in z.namelist())
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(f'{digest}  {target.name}\n',encoding='utf-8')
    out=ROOT/'outputs'
    out.mkdir(exist_ok=True)
    shutil.copy2(target,out/target.name)
    shutil.copy2(target.with_suffix('.zip.sha256'),out/target.with_suffix('.zip.sha256').name)
    print(f'{target}\nSHA256 {digest}\n{len(files)} files')


if __name__=='__main__':
    main()
