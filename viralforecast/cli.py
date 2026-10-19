import argparse
import json
import sys
from pathlib import Path

from .analysis import analyze
from .common import ForecastError, read_json
from .history import load_history
from .model import backtest, compare, forecast
from .reporting import validate_report, write_reports


def parser():
    p = argparse.ArgumentParser(prog="viralforecast", description="Local content heuristics and experimental account forecasts")
    from . import __version__
    p.add_argument("--version", action="version", version=__version__)
    cmds = p.add_subparsers(dest="command", required=True)
    a = cmds.add_parser("analyze", help="Mode A: metadata/text heuristics, never view predictions")
    a.add_argument("--video", required=True)
    a.add_argument("--title", default="")
    a.add_argument("--caption", default="")
    a.add_argument("--platform", default="tiktok")
    a.add_argument("--cover")
    a.add_argument("--transcript", help="Local timestamped transcript JSON")
    a.add_argument("--transcriber", help="Trusted local Python module:function accepting a WAV path; opt-in")
    a.add_argument("--rules", help="Custom editorial rule JSON")
    a.add_argument("--understand", action="store_true", help="Run local object/action/scene/expression models")
    a.add_argument("--asr", action="store_true", help="Run built-in local Whisper transcription")
    a.add_argument("--models-dir", default="models", help="Previously downloaded model directory")
    a.add_argument("--language", help="ASR language code, e.g. zh or en; default automatic")
    a.add_argument("--semantic-labels", help="JSON array of English scene descriptions for CLIP")
    a.add_argument("--trends-csv", help="Platform-exported similar-content snapshots")
    a.add_argument("--as-of", help="Observation cutoff for imported trend context")
    a.add_argument("--trend-days", type=int, default=7)
    a.add_argument("--min-similarity", type=float, default=.15)
    a.add_argument("--exclude-account", help="Exclude own account from peer trends")
    t = cmds.add_parser("trends", help="Analyze recent peer traffic and evidence-based test suggestions from CSV")
    t.add_argument("--csv", required=True)
    t.add_argument("--analysis", required=True)
    t.add_argument("--as-of", required=True)
    t.add_argument("--days", type=int, default=7)
    t.add_argument("--min-similarity", type=float, default=.15)
    t.add_argument("--exclude-account")
    for name in ("predict", "backtest"):
        c = cmds.add_parser(name)
        c.add_argument("--history", required=True)
        c.add_argument("--account", required=True)
        c.add_argument("--platform", required=True)
        if name == "predict":
            c.add_argument("--analysis", required=True)
            c.add_argument("--as-of", required=True, help="Planned publication timestamp, ISO 8601")
        else:
            c.add_argument("--step", type=int, default=1)
            c.add_argument("--start", type=int, default=120)
    c = cmds.add_parser("compare", help="Compare a saved prediction with mature actual metrics")
    c.add_argument("--prediction", required=True)
    c.add_argument("--actual", required=True)
    c = cmds.add_parser("report", help="Render an existing result into JSON/Markdown/HTML")
    c.add_argument("--input", required=True)
    for c in cmds.choices.values():
        c.add_argument("--out", required=True, help="Output folder for JSON, Markdown and HTML")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "analyze":
            data = analyze(args.video, args.title, args.caption, args.platform, Path(args.out) / "media", args.rules,
                           args.transcript, args.transcriber, args.cover, args.understand, args.asr,
                           args.models_dir, args.language, read_json(args.semantic_labels) if args.semantic_labels else None,
                           args.trends_csv, args.as_of, args.trend_days, args.min_similarity, args.exclude_account)
        elif args.command == "trends":
            from .trends import trends
            data = trends(args.csv, read_json(args.analysis), args.as_of, args.days, args.min_similarity, args.exclude_account)
        elif args.command in ("predict", "backtest"):
            rows = load_history(args.history, args.account, args.platform)
            if args.command == "predict":
                analysis = read_json(args.analysis)
                if not isinstance(analysis, dict) or analysis.get("platform") != args.platform:
                    raise ForecastError("Analysis platform must match selected history platform")
                data = forecast(rows, analysis, args.as_of, args.account)
            else:
                data = backtest(rows, args.step, args.start)
        elif args.command == "compare":
            data = compare(read_json(args.prediction), read_json(args.actual))
        else:
            data = read_json(args.input)
            validate_report(data)
        paths = write_reports(data, args.out)
        print(json.dumps({"status": "ok", "kind": data["kind"], "reports": paths}, ensure_ascii=True))
        return 0
    except (ForecastError, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
