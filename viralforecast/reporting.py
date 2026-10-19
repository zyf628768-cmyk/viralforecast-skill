"""Self-contained, escaped reports. JSON is the canonical machine artifact."""
import html
import json
from pathlib import Path

from .common import ForecastError


def write_reports(data, output):
    dest = Path(output)
    dest.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
    kind = data.get("kind", "report")
    md = f"# ViralForecast — {kind}\n\n"
    md += "Heuristic scores are not calibrated predictions. Statistical estimates are experimental.\n\n"
    md += f"Mode: {data.get('mode', 'n/a')} | Status: {data.get('status', data.get('assessment_type', 'n/a'))}\n\n"
    if data.get("data_source") == "synthetic":
        md += "**SYNTHETIC DATA — software demonstration only; no commercial accuracy claim.**\n\n"
    for item in data.get("limitations", []):
        md += "- " + item.replace("\n", " ") + "\n"
    # Escape code-fence delimiters in arbitrary user content for Markdown readers.
    md += "\n## Full result\n\n```json\n" + raw.replace("```", "\\u0060\\u0060\\u0060") + "\n```\n"
    body = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>ViralForecast {html.escape(kind)}</title>
<style>body{{font:16px/1.6 system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;background:#f7f8fb;color:#17243a}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:24px;border:1px solid #cdd6e5}}.warning{{background:#fff1cd;padding:16px}}</style></head>
<body><h1>ViralForecast · {html.escape(kind)}</h1><p class="warning">Heuristic scores are not calibrated predictions. Statistical estimates are experimental.
Data source: {html.escape(str(data.get('data_source', 'not applicable')))}. Synthetic data demonstrates software behavior only.</p>
<pre>{html.escape(raw)}</pre></body></html>"""
    paths = {}
    for ext, text in (("json", raw + "\n"), ("md", md), ("html", body)):
        p = dest / f"{kind}.{ext}"
        p.write_text(text, encoding="utf-8")
        paths[ext] = str(p.resolve())
    return paths


def validate_report(data):
    if not isinstance(data, dict) or data.get("schema_version") != "1.0" or data.get("kind") not in {"analysis", "prediction", "backtest", "comparison"}:
        raise ForecastError("Unsupported report JSON envelope")
