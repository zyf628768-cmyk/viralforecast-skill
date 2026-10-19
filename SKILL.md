---
name: viralforecast
description: Analyze unpublished local short videos and copy using transparent heuristics, or forecast account performance from mature historical CSV records with temporal evaluation. Use for TikTok, Shorts, Reels, Douyin, Kuaishou, Xiaohongshu or Bilibili pre-publication assessment and post-publication error review.
---

# ViralForecast

Use the installed `viralforecast` CLI from this project. See [README.md](README.md) for setup and runnable commands, [docs/data.md](docs/data.md) for CSV definitions and [docs/methodology.md](docs/methodology.md) for statistical limits.

Analyze the user's local video, title, caption and optional cover/transcript with `viralforecast analyze`. Do not infer visual subjects, emotions, safety or spoken meaning from scene counts or file metadata. The built-in implementation has no visual semantic model and does not bundle speech recognition weights. A local transcription adapter is an explicit opt-in extension; inspect and trust its code before use.

Without history, report scores as **heuristic, not statistically calibrated**. Do not turn them into views, retention percentages or viral probabilities. The CLI deliberately emits no such forecasts in mode A.

With history, select one account/platform, preserve the pre-publication feature definition and run `predict` at the intended publication timestamp. Only mature seven-day outcomes before that timestamp are eligible. Fewer than 120 mature records or inadequate temporal separation causes automatic downgrade. Preserve null event probabilities and their support reasons. Read model-selection and calibration diagnostics instead of presenting every model as superior to a median baseline.

Run `backtest` for sample-outside-fit errors, interval coverage, Brier score and reliability bins. Synthetic CSVs validate software behavior only. Never claim commercial predictive accuracy from them. `compare` accepts actual outcomes after seven days; `report` renders an existing artifact to JSON, Markdown and escaped HTML.

All processing is local. Do not upload media or historical account data or publish a repository unless the user authorizes that action. Keep the limitations and synthetic-data labels in delivered reports.
