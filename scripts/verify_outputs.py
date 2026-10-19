"""Verify the real demo artifacts and record versions, without claiming accuracy."""
import json
import platform
import sys
from html.parser import HTMLParser
from pathlib import Path

import numpy
import PIL
from jsonschema import validate

from viralforecast.media import binary, run

ROOT=Path(__file__).resolve().parents[1]


class ReportParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside=False
        self.data=[]
    def handle_starttag(self, tag, attrs):
        if tag=='pre':
            self.inside=True
    def handle_endtag(self,tag):
        if tag=='pre':
            self.inside=False
    def handle_data(self,data):
        if self.inside:
            self.data.append(data)


def main():
    schema=json.loads((ROOT/'schemas/output.schema.json').read_text())
    records=[]
    for folder,kind in [('mode-a','analysis'),('mode-b','prediction'),('downgrade','prediction'),('backtest','backtest'),('compare','comparison'),('rendered','prediction')]:
        base=ROOT/'outputs/demo'/folder
        data=json.loads((base/f'{kind}.json').read_text(encoding='utf-8-sig'))
        validate(data,schema)
        parser=ReportParser()
        parser.feed((base/f'{kind}.html').read_text(encoding='utf-8'))
        assert json.loads(''.join(parser.data))==data
        md=(base/f'{kind}.md').read_text(encoding='utf-8')
        assert json.loads(md.split('```json\n',1)[1].rsplit('\n```',1)[0])==data
        records.append({'folder':folder,'kind':kind,'json_schema':'passed','html_json_equivalence':'passed','markdown_json_equivalence':'passed'})
    a=json.loads((ROOT/'outputs/demo/mode-a/analysis.json').read_text())
    b=json.loads((ROOT/'outputs/demo/mode-b/prediction.json').read_text())
    d=json.loads((ROOT/'outputs/demo/downgrade/prediction.json').read_text())
    bt=json.loads((ROOT/'outputs/demo/backtest/backtest.json').read_text())
    assert a['mode']=='A' and 'forecasts' not in a
    assert b['mode']=='B' and b['data_source']=='synthetic'
    assert d['mode']=='A' and d['forecasts'] is None
    assert bt['metrics']['views_7d']['n']==28
    ffmpeg,ffprobe=binary('ffmpeg'),binary('ffprobe')
    info={'python':sys.version,'os':platform.platform(),'numpy':numpy.__version__,'pillow':PIL.__version__,
          'ffmpeg':run([ffmpeg,'-version']).stdout.splitlines()[0],
          'ffprobe':run([ffprobe,'-version']).stdout.splitlines()[0],
          'report_sets':len(records),'report_files':3*len(records),'records':records,
          'synthetic_backtest_metrics':bt['metrics'],'synthetic_probability_metrics':bt['probability_metrics'],
          'synthetic_forecasts':b['forecasts'],
          'interpretation':'Synthetic execution evidence only; no commercial accuracy claim.'}
    (ROOT/'validation/artifact-verification.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'passed','report_sets':len(records),'report_files':len(records)*3,'oos_cases_per_horizon':bt['metrics']['views_7d']['n']}))


if __name__=='__main__':
    main()
