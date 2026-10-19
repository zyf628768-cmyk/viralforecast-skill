# Actual local test report / 真实测试报告

Historical report for version 0.1. For the later implemented local vision/ASR capabilities and real-model tests, see [UNDERSTANDING_TEST_REPORT.md](UNDERSTANDING_TEST_REPORT.md). For remote CI execution, see [CI_REPORT.md](CI_REPORT.md).

Execution date: 2026-10-19 (Asia/Shanghai). This report describes actual local commands and generated artifacts; it does not describe a GitHub CI run.

## Environment

Windows 11 build 26200, 64-bit Python 3.12.14 in the project's `.venv`; NumPy 2.5.4, Pillow 13.0.0, pytest 9.1.1, jsonschema 4.26.0, imageio-ffmpeg 0.6.0. Local media tests used imageio-ffmpeg's FFmpeg 7.1 executable and separately downloaded FFprobe 9.0.2. Full recorded versions: `validation/artifact-verification.json`; dependency snapshot: `validation/dependencies.txt` (a record, not a portable lockfile). PyYAML 6.0.3 is used only by the external Skill validator.

The ordinary `python` shell command was an unusable Windows Store alias. A bundled Python created the virtual environment. Initial temporary-directory permission and restricted-network installation errors were resolved. Exact distinguishing errors and resolutions are retained in `validation/environment-issues.txt`. The final code runs without network calls.

## Executed checks

| Check | Actual result |
|---|---|
| First pytest suite | 38 passed, 6.73s |
| Expanded consistency suite | 41 passed, 5.33s |
| Final source suite | **42 passed, 5.35s**; JUnit `validation/pytest.xml` |
| Valid generated MP4 | H.264 portrait 180×320, about 6 seconds, two color scenes and AAC sine audio |
| Video integration | Metadata, near-3-second scene cut, still files, WAV and imported transcript checked |
| All five installed CLI commands | Successful real executable invocations; `validation/demo-commands.json` |
| Automatic downgrade | Small-history demo returned mode A with no numeric forecasts; dense-date embargo downgrade unit test passed |
| Error paths | Empty/malformed CSV, invalid numeric/date/count values, duplicate IDs, empty/corrupt media, missing FFmpeg/FFprobe, malformed transcript, unavailable adapter and immature actual data |
| Leakage checks | Future outcome mutation has no effect; calibration outcomes do not change point fitting/selection; outcomes never serve as input features; mature-label embargo verified |
| Backtest/serving consistency | Identical point/interval behavior at same temporal origin |
| Reports | Six result sets × JSON/Markdown/HTML = **18 files**; Schema validation and parsed HTML/Markdown equivalence passed |
| Skill | Official `quick_validate.py .` returned `Skill is valid!` |
| Dependency metadata | `pip check`: `No broken requirements found.` |
| Wheel | Built without network; separately installed into `work/wheel-installed`; isolated Python import selected the installed wheel and its packaged platform JSON |
| Extracted release | Extracted source ZIP into a separate local folder and reran the complete suite: **42 passed, 5.32s**; `validation/release-pytest.xml` and log |

Final suite command (with project-local TEMP/TMP and explicit FFPROBE set):

```powershell
.\.venv\Scripts\python.exe -m pytest -q --basetemp=work/pytest-run3 --junitxml=validation/pytest.xml
.\scripts\run_demo.ps1
.\.venv\Scripts\python.exe scripts/verify_outputs.py
```

Logs and JUnit XML are packaged under `validation/`. `demo-commands.json` records all arguments, actual exit codes and outputs, including expected-error exits of 2. Expected-error handling succeeds as a test; it does not mean invalid input succeeded as an analysis.

## Double-mode evidence and statistical limits

`reports/demo/mode-a/analysis.*` contains only heuristics with explicit `heuristic_not_statistically_calibrated` labeling. `reports/demo/mode-b/prediction.*` uses 260 explicitly synthetic history rows and produces both horizons, intervals, historical rate estimates and support-aware event probabilities. `reports/demo/downgrade/prediction.*` demonstrates fallback. `reports/demo/compare/comparison.*` compares against synthetic mature actual metrics. The development workspace stores the same reports under `outputs/demo/`.

The synthetic expanding-origin backtest (`--step 5`) evaluated **28 cases per horizon**, with no skipped origins. Actual view-count MAE: 24h **1462.70**, historical median baseline **1386.71**; 7d **3371.65**, baseline **3221.57**. Thus the served model **did not beat the simple baseline** in this demo. Both interval coverages were 26/28 ≈ 92.86%, with broad mean widths of about 8,722 and 16,976 views. Nominal 90% coverage on a synthetic sample is not a real-world guarantee.

Probability Brier/ECE/reliability and baseline comparisons are stored in the backtest and verification JSON. The 24h 3× event Brier was approximately 0.2102 versus baseline 0.1940, also worse. Do not claim calibration improvement from this dataset. No real-account data were provided or used; commercial forecasting accuracy remains unvalidated.

## Compatibility and untested capabilities

Only the local Windows/Python 3.12 environment was actually executed. GitHub Actions is configured for Windows/Ubuntu × Python 3.10/3.12 but has not run remotely. macOS, other interpreters, large videos, GPU inference, real ASR adapters, real account forecasting and production workloads were not tested. The local stub adapter test verifies the interface, not speech-recognition quality. There is no built-in visual semantic model, OCR, hosted UI or paid API dependency.

External FFmpeg/FFprobe are not bundled in source releases and must be installed/discovered as documented. The source archive and SHA256 are generated in local `dist/` and copied to `outputs/` for delivery. No GitHub publication or user-data upload occurred.

