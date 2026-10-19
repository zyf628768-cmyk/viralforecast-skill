import importlib.util
import json
from pathlib import Path
import zipfile

import pytest


def builder(tmp_path):
    source=Path(__file__).parents[1]/"scripts/build_public_release.py"
    spec=importlib.util.spec_from_file_location("public_builder",source)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT=tmp_path
    needed=['viralforecast/trends.py','viralforecast/understanding.py','viralforecast/speech.py','docs/QUICKSTART.zh-CN.md']
    for name in needed:
        p=tmp_path/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('public source',encoding='utf-8')
    p=tmp_path/'examples/data/synthetic_trends.csv'
    p.parent.mkdir(parents=True)
    p.write_text('data_source,views\nsynthetic,10\n')
    return module


def test_public_archive_excludes_private_records_and_weights(tmp_path):
    module=builder(tmp_path)
    p=tmp_path/'validation/private.log'
    p.parent.mkdir()
    p.write_text('private local validation record')
    (tmp_path/'viralforecast/private-model.bin').write_bytes(b'weight')
    module.main()
    with zipfile.ZipFile(tmp_path/'dist/viralforecast-skill-0.2.0.zip') as z:
        assert z.testzip() is None
        assert not any('private' in n for n in z.namelist())
        manifest=json.loads(z.read('viralforecast-skill/RELEASE_MANIFEST.json'))
        assert 'docs/QUICKSTART.zh-CN.md' in manifest['files']


def test_public_archive_rejects_real_example_csv(tmp_path):
    module=builder(tmp_path)
    (tmp_path/'examples/data/synthetic_trends.csv').write_text('data_source,views\nreal,10\n')
    with pytest.raises(RuntimeError,match='not explicitly synthetic'):
        module.main()
