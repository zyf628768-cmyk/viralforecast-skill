# Release 0.2.0

Adds explicitly enabled local object detection, temporal action recognition, scene/copy matching, visible-expression cues and built-in multilingual Whisper transcription. Run `python -m viralforecast.models --download --directory models` after installing `.[understanding]`, then `viralforecast analyze --understand --asr --models-dir models ...`. Downloaded weights remain separate from the MIT source archive. See `local-understanding.md` and `UNDERSTANDING_TEST_REPORT.md` for boundaries and actual validation.

The Chinese introduction is rewritten around the creator's workflow. Model scores are separated from heuristic reach scores and are not calibrated correctness or virality probabilities. Expressions never establish a person's real emotions.

# Release 0.1.0 (historical)

Suggested repository name: `viralforecast-skill`.

Local-first pre-publication heuristics and experimental per-account forecasting for seven video platforms. Includes working analyze/predict/compare/backtest/report CLI commands, temporal ridge-versus-median selection, uncertainty intervals, support-aware event calibration, escaped reports and a reusable Skill entrypoint.

This release has no built-in visual semantic model, automatic ASR weights, paid APIs or hosted UI. The included data and demo outcomes are simulated and cannot establish commercial accuracy. Model intervals are nominal; evaluate out-of-time performance on your own account before making decisions.

Before a future public release, inspect the source archive and its checksum, run CI in the target repository and review your real-data export definitions. No GitHub repository, public release, upload or production service has been created during local development. The source is MIT; external FFmpeg binaries are installed separately under their own licenses.
