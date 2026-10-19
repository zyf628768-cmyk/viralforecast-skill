# ViralForecast Skill

[![tests](https://github.com/zyf628768-cmyk/viralforecast-skill/actions/workflows/test.yml/badge.svg)](https://github.com/zyf628768-cmyk/viralforecast-skill/actions/workflows/test.yml)

Local-first pre-publication video assessment and experimental account forecasting. MIT licensed. **No paid API or data upload is required.** This release is a Python CLI and reusable agent skill, not a hosted upload website.

## 中文说明

让每一次发布，都多一份判断依据。ViralForecast 面向 TikTok、YouTube Shorts、Instagram Reels、抖音、快手、小红书和 B 站，将视频、标题、文案与账号历史放在一起分析，帮你在发布前发现内容亮点、定位薄弱环节，找到更值得尝试的优化方向。各平台的评估参数可通过 JSON 灵活调整，适配你的内容类型与运营策略。

- **模式 A，无历史数据**：视频 + 标题/文案即可运行；输出相对传播潜力、前 3 秒、完播潜力、互动、节奏、风险与建议。所有分数均为**未统计校准的启发式评分**，不输出具体播放量或爆款概率。
- **模式 B，有历史数据**：至少 120 条同账号、同平台且 7 天指标已成熟的真实记录；输出 24h/7d 播放量点估计与名义 90% 区间、互动率，以及超过历史播放量中位数 3/5 倍的概率估计。概率校准支持不足时返回 null；记录不足或时间划分不足时降级。模型必须先与简单历史中位数比较，并可在后续样本外回测中检查是否真的更好。
- **看画面，也听内容**：启用本地理解扩展，即可进行对象检测、短片段动作识别、场景语义与文案匹配、可见表情线索分析，并用内置 Whisper 自动生成语音转写。基础模式仍支持关键帧、镜头切换、音轨和封面特征分析；模型在本机运行，内容无需上传。
- JSON、Markdown、HTML 同时生成；`compare` 对照发布后成熟指标分析误差；`backtest` 输出时间顺序样本外结果与概率校准诊断。


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

### 启用本地视频理解与语音识别

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[understanding]"
.\.venv\Scripts\python.exe -m viralforecast.models --download --directory models
.\.venv\Scripts\viralforecast.exe analyze --video examples/data/demo.mp4 --title "A color demonstration" --understand --asr --models-dir models --out outputs/understood
```

模型只在显式下载时联网，分析过程读取本地权重。表情结果描述画面中的可见线索，不推断人物真实心理状态；识别不确定或未检测到人脸时会如实标记。详见[本地理解能力与模型说明](docs/local-understanding.md)。

### 生成示例并运行

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

Custom platform editorial rules: `--rules examples/rules.json`. Optional custom transcription: `--transcriber your_local_module:transcribe`; the function receives the generated mono WAV path and returns `{"segments":[{"start":0,"end":1,"text":"..."}]}`. Use only a trusted module; imported code has your Python process permissions. This custom adapter is separate from the built-in `--asr` implementation. Choose one transcript source: import, custom adapter or built-in ASR.

Historical CSV columns and exact feature definitions are in [docs/data.md](docs/data.md). Use `data_source=real` only for your own real records; this declaration is not externally verified. Platforms use CLI IDs `tiktok`, `youtube-shorts`, `instagram-reels`, `douyin`, `kuaishou`, `xiaohongshu`, `bilibili`. `--as-of` is the intended publication time; date-only/naive dates are UTC.

## Tests, packaging and Skill

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=validation/pytest.xml
.\.venv\Scripts\python.exe scripts/build_release.py
```

The release builder includes source, docs, tests, schemas and explicitly synthetic examples/reports plus validation records when present. It excludes virtual environments, external binaries and arbitrary private outputs. Local archives go to `dist/`; a user-facing copy is placed in `outputs/`.

Use [SKILL.md](SKILL.md) as the skill entrypoint after installing this package. To make it discoverable in another Codex installation, place the project folder under that installation's configured skills directory; no automatic global installation is performed here. The skill calls the actual CLI and preserves mode, provenance, abstention and privacy boundaries.

Actual local test results, repaired issues and environment versions are documented in [docs/TEST_REPORT.md](docs/TEST_REPORT.md). The subsequent GitHub publication ran all four Windows/Ubuntu and Python 3.10/3.12 combinations, each with 42 tests passing; see [docs/CI_REPORT.md](docs/CI_REPORT.md).

Version 0.2 local model execution and its repaired dependency issue are recorded in [docs/UNDERSTANDING_TEST_REPORT.md](docs/UNDERSTANDING_TEST_REPORT.md). The original CI report is historical; the current Actions run checks the updated lightweight suite and marks the optional large-model test as skipped when weights are absent.

See [architecture](docs/architecture.md), [methods and limitations](docs/methodology.md), [privacy](docs/privacy.md), [changelog](CHANGELOG.md) and [release notes](docs/RELEASE_NOTES.md). Public repository: [viralforecast-skill](https://github.com/zyf628768-cmyk/viralforecast-skill). Publishing was explicitly requested by the user after local development.

