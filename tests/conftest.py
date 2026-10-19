import importlib.util
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixtures(tmp_path_factory):
    spec = importlib.util.spec_from_file_location("example_generator", Path(__file__).parents[1] / "examples/generate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    root = tmp_path_factory.mktemp("demo")
    module.generate(root)
    return root


@pytest.fixture(scope="session")
def rows(fixtures):
    from viralforecast.history import load_history
    return load_history(fixtures / "synthetic_history.csv", "demo", "tiktok")
