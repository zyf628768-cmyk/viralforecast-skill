---
name: viralforecast
description: Analyze unpublished local short videos and copy using transparent heuristics, or forecast account performance from mature historical CSV records with temporal evaluation. Use for TikTok, Shorts, Reels, Douyin, Kuaishou, Xiaohongshu or Bilibili pre-publication assessment and post-publication error review.
---

# ViralForecast

Use the installed `viralforecast` CLI from this project. See [README.md](README.md) for setup and runnable commands, [docs/data.md](docs/data.md) for CSV definitions and [docs/methodology.md](docs/methodology.md) for statistical limits.

Analyze the user's local video, title, caption and optional cover/transcript with `viralforecast analyze`. For learned object/action/scene and visible-expression analysis use `--understand`; for built-in local Whisper transcription use `--asr`. Install `.[understanding]` and explicitly download model weights using `python -m viralforecast.models --download --directory models` before running these flags. See [docs/local-understanding.md](docs/local-understanding.md). Inference reads local verified files only. No visual or spoken meaning can be inferred from metadata-only results. Visible expressions never establish true feelings, mood, intent or mental health. Missing faces and uncertain predictions must remain explicit. A custom transcription adapter is an opt-in alternative; inspect and trust its code before use.

Without history, report scores as **heuristic, not statistically calibrated**. Do not turn them into views, retention percentages or viral probabilities. The CLI deliberately emits no such forecasts in mode A.

With history, select one account/platform, preserve the pre-publication feature definition and run `predict` at the intended publication timestamp. Only mature seven-day outcomes before that timestamp are eligible. Fewer than 120 mature records or inadequate temporal separation causes automatic downgrade. Preserve null event probabilities and their support reasons. Read model-selection and calibration diagnostics instead of presenting every model as superior to a median baseline.

Run `backtest` for sample-outside-fit errors, interval coverage, Brier score and reliability bins. Synthetic CSVs validate software behavior only. Never claim commercial predictive accuracy from them. `compare` accepts actual outcomes after seven days; `report` renders an existing artifact to JSON, Markdown and escaped HTML.

For recent peer traffic, use `trends --csv snapshots.csv --analysis analysis.json --as-of timestamp`, or attach it with `analyze --trends-csv`. See [docs/QUICKSTART.zh-CN.md](docs/QUICKSTART.zh-CN.md) for the separate snapshot CSV contract. Honor platform, account filters and cutoff; never include future observations. One snapshot cannot establish recent velocity. Report sample counts, missing support and observed attention as a sample-relative proxy, never internal recommendation exposure or platform-wide heat. Improvement suggestions are observational hypotheses for controlled tests, not promises of more views. Do not inject a trend multiplier into statistical forecasts without validation.

All processing is local. Do not upload media or historical account data or publish a repository unless the user authorizes that action. Keep the limitations and synthetic-data labels in delivered reports.
