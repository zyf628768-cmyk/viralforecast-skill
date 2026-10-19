"""Self-contained, escaped reports. JSON is the canonical machine artifact."""
import html
import json
from pathlib import Path

from .common import ForecastError


def trend_summary(data):
    context=data if data.get("kind")=="trends" else data.get("trend_context")
    if not context:
        return "",""
    heat=context["heat"]
    coverage=context["coverage"]
    def value(x):
        return "样本不足 / 未提供" if x is None else f"{x:.2f}"
    facts=[f"截止时间：{context['as_of']}；窗口：{context['window_days']} 天",
           f"相似内容：{coverage['similar_posts']} 条；可测量近期增速：{coverage['similar_with_velocity']} 条",
           f"同类内容播放增速中位数：{value(heat['similar_median_views_per_hour'])} 次/小时",
           f"相对导入样本的热度比：{value(heat['relative_heat_ratio'])}",
           f"同批样本前后窗口增速比：{value(heat['paired_window_momentum_ratio'])}"]
    actions=[a["suggestion"] for a in context.get("improvements",[])]
    caution="样本相对热度不等于平台内部推流或全平台趋势；改进建议是待验证的实验。"
    md="\n## 同类内容近期流量\n\n"+"\n".join("- "+html.escape(s) for s in facts)+"\n\n### 值得测试的改进\n\n"+"\n".join("- "+html.escape(s) for s in actions)+"\n\n"+caution+"\n\n"
    body="<section><h2>同类内容近期流量</h2><ul>"+"".join("<li>"+html.escape(s)+"</li>" for s in facts)+"</ul><h3>值得测试的改进</h3><ul>"+"".join("<li>"+html.escape(s)+"</li>" for s in actions)+"</ul><p>"+caution+"</p></section>"
    return md,body


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
    summary_md,summary_html=trend_summary(data)
    md+=summary_md
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
{summary_html}<pre>{html.escape(raw)}</pre></body></html>"""
    paths = {}
    for ext, text in (("json", raw + "\n"), ("md", md), ("html", body)):
        p = dest / f"{kind}.{ext}"
        p.write_text(text, encoding="utf-8")
        paths[ext] = str(p.resolve())
    return paths


def validate_report(data):
    if not isinstance(data, dict) or data.get("schema_version") != "1.0" or data.get("kind") not in {"analysis", "prediction", "backtest", "comparison", "trends"}:
        raise ForecastError("Unsupported report JSON envelope")
