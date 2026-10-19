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
    p.add_argument("--version", action="version", version="0.1.0")
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
                           args.transcript, args.transcriber, args.cover)
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
