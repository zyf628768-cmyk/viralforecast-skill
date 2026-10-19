"""Import installed wheel ahead of editable source; assert package data works."""
from pathlib import Path
import sys

target=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(target))
import viralforecast
from viralforecast.analysis import rules
from viralforecast.cli import main

assert Path(viralforecast.__file__).is_relative_to(target), viralforecast.__file__
assert rules('bilibili')['ideal_duration']==120
assert callable(main)
print(f'Wheel import and packaged platform data passed: {viralforecast.__file__}')
