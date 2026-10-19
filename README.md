# ViralForecast Skill

[![tests](https://github.com/zyf628768-cmyk/viralforecast-skill/actions/workflows/test.yml/badge.svg)](https://github.com/zyf628768-cmyk/viralforecast-skill/actions/workflows/test.yml)

Local-first pre-publication video assessment and experimental account forecasting. MIT licensed. **No paid API or data upload is required.** This release is a Python CLI and reusable agent skill, not a hosted upload website.

## 中文说明

支持 TikTok、YouTube Shorts、Instagram Reels、抖音、快手、小红书和 B 站。平台参数可通过 JSON 修改，属于编辑性规则，不代表官方算法或平台政策。

- **模式 A，无历史数据**：视频 + 标题/文案即可运行；输出相对传播潜力、前 3 秒、完播潜力、互动、节奏、风险与建议。所有分数均为**未统计校准的启发式评分**，不输出具体播放量或爆款概率。
- **模式 B，有历史数据**：至少 120 条同账号、同平台且 7 天指标已成熟的真实记录；输出 24h/7d 播放量点估计与名义 90% 区间、互动率，以及超过历史播放量中位数 3/5 倍的概率估计。概率校准支持不足时返回 null；记录不足或时间划分不足时降级。模型必须先与简单历史中位数比较，并可在后续样本外回测中检查是否真的更好。
- 视频支持 FFprobe 信息、FFmpeg 关键帧/镜头切换/音轨、封面亮度对比度、转写导入与本地转写接口。**未实现对象、动作、情绪、视觉语义理解或自动内置语音识别。**
- JSON、Markdown、HTML 同时生成；`compare` 对照发布后成熟指标分析误差；`backtest` 输出时间顺序样本外结果与概率校准诊断。

示例数据均标记 `synthetic`，只验证软件流程。没有真实账号数据，不能据此证明商业准确率。

## English overview

Mode A uses explicit metadata/text heuristics, with no calibrated reach or success claims. Mode B trains an inspectable ridge model versus a historical median, separates temporal selection and calibration, abstains on weak event support, and supports expanding-origin evaluation. It estimates performance conditional on your own supplied history, with substantial drift and small-sample limitations. All runtime processing stays local.

## Install / 安装（Windows 优先）

Python 3.10+ and FFmpeg **including FFprobe** are required for media analysis. Both executables must be on PATH, or set `FFMPEG` / `FFPROBE` to their full executable paths. See the official [FFmpeg download page](https://ffmpeg.org/download.html) for platform builds. This project does not redistribute those binaries.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,media]"
# If FFmpeg/FFprobe are not on PATH:
$env:FFMPEG = 'C:\ffmpeg\bin\ffmpeg.exe'
$env:FFPROBE = 'C:\ffmpeg\bin\ffprobe.exe'
.\.venv\Scripts\viralforecast.exe --help
```

`media` optionally provides imageio-ffmpeg's FFmpeg executable fallback; it does **not** provide FFprobe. Core statistics/reporting need only NumPy and Pillow. If Windows temporary directory permissions break venv/pip, set `$env:TEMP` and `$env:TMP` to an existing project-owned temporary directory and retry. If the shell's Python is a Store placeholder, select an installed interpreter explicitly.

Linux/macOS: `python3 -m venv .venv`, `.venv/bin/python -m pip install -e '.[test,media]'`, install FFmpeg/FFprobe through your package manager, and use `.venv/bin/viralforecast` in equivalent commands below. Windows PowerShell activation is optional; direct executable paths avoid execution-policy issues.

## Run both modes / 双模式实跑

From the repository root, generate explicitly simulated history, a valid two-scene MP4 with synthetic audio, an illustrative supplied transcript, cover and synthetic actual metrics:

```powershell
.\.venv\Scripts\python.exe examples/generate.py --out examples/data
.\.venv\Scripts\viralforecast.exe analyze --video examples/data/demo.mp4 --title "How to make a clear opening?" --caption "Try one change #demo" --cover examples/data/cover.png --transcript examples/data/transcript.json --platform tiktok --out outputs/demo/mode-a
.\.venv\Scripts\viralforecast.exe predict --analysis outputs/demo/mode-a/analysis.json --history examples/data/synthetic_history.csv --account demo --platform tiktok --as-of 2026-10-19T00:00:00Z --out outputs/demo/mode-b
.\.venv\Scripts\viralforecast.exe backtest --history examples/data/synthetic_history.csv --account demo --platform tiktok --step 5 --out outputs/demo/backtest
.\.venv\Scripts\viralforecast.exe compare --prediction outputs/demo/mode-b/prediction.json --actual examples/data/actual.json --out outputs/demo/compare
.\.venv\Scripts\viralforecast.exe report --input outputs/demo/mode-b/prediction.json --out outputs/demo/rendered
```

Each command writes all three report formats. `analyze` also stores extracted stills and a WAV under its output folder. `scripts/run_demo.ps1` performs these commands, a small-history downgrade, and expected-error CLI checks with real logs. It uses the current project's locally downloaded FFprobe when present, otherwise normal executable discovery. No user data is uploaded.

Custom platform editorial rules: `--rules examples/rules.json`. Optional transcription: `--transcriber your_local_module:transcribe`; the function receives the generated mono WAV path and returns `{"segments":[{"start":0,"end":1,"text":"..."}]}`. Use only a trusted module; imported code has your Python process permissions. No model/API call occurs unless your chosen adapter implements it. Transcript import and adapter are mutually exclusive.

Historical CSV columns and exact feature definitions are in [docs/data.md](docs/data.md). Use `data_source=real` only for your own real records; this declaration is not externally verified. Platforms use CLI IDs `tiktok`, `youtube-shorts`, `instagram-reels`, `douyin`, `kuaishou`, `xiaohongshu`, `bilibili`. `--as-of` is the intended publication time; date-only/naive dates are UTC.

## Tests, packaging and Skill

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=validation/pytest.xml
.\.venv\Scripts\python.exe scripts/build_release.py
```

The release builder includes source, docs, tests, schemas and explicitly synthetic examples/reports plus validation records when present. It excludes virtual environments, external binaries and arbitrary private outputs. Local archives go to `dist/`; a user-facing copy is placed in `outputs/`.

Use [SKILL.md](SKILL.md) as the skill entrypoint after installing this package. To make it discoverable in another Codex installation, place the project folder under that installation's configured skills directory; no automatic global installation is performed here. The skill calls the actual CLI and preserves mode, provenance, abstention and privacy boundaries.

Actual local test results, repaired issues and environment versions are documented in [docs/TEST_REPORT.md](docs/TEST_REPORT.md). The subsequent GitHub publication ran all four Windows/Ubuntu and Python 3.10/3.12 combinations, each with 42 tests passing; see [docs/CI_REPORT.md](docs/CI_REPORT.md).

See [architecture](docs/architecture.md), [methods and limitations](docs/methodology.md), [privacy](docs/privacy.md), [changelog](CHANGELOG.md) and [release notes](docs/RELEASE_NOTES.md). Public repository: [viralforecast-skill](https://github.com/zyf628768-cmyk/viralforecast-skill). Publishing was explicitly requested by the user after local development.

