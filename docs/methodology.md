# Forecast methods and limits / 预测方法与局限

Version 0.2 adds optional learned local perception and built-in ASR; see [local-understanding.md](local-understanding.md). The metadata-only behavior described below remains the default. Perception outputs are separately labeled and do not change the historical statistical feature contract.

## Mode A

Scores use hand-written formulas in `analysis.py`: first-three-second score combines early scene cuts, title presence and question marks; completion proxy rewards configured duration; interaction proxy uses questions/hashtags; pacing uses scene-cut rate versus an editorial target. Relative potential is a weighted mean (30% hook, 30% duration proxy, 20% interaction, 20% pacing). These are arbitrary editorial aids, not measurements of real retention or comparative percentile ranks. No view count or viral probability is produced.

Frame extraction, scene detection, cover brightness/contrast and text/transcript character overlap are implemented. With `--understand`, local learned models add object boxes, temporal action candidates, scene semantic matching, image-copy similarity and visible-expression cues. With `--asr`, local Whisper generates timestamped speech segments; weights are downloaded separately and explicitly. Imported transcripts and trusted local adapters remain alternatives. OCR, safety screening and content truthfulness verification are not implemented. The built-in sine-wave demo's supplied transcript is illustrative and is not speech-recognition evidence.

## Mode B

Minimum 120 mature rows per account/platform. Sort by timestamp, then content ID. Use nominal 50% fit / 25% selection-residual / 25% calibration blocks. Purge fit labels that have not matured before the first selection post and selection labels not mature before the first calibration post. Require at least 20 rows per remaining block; otherwise downgrade to mode A with no numeric view forecasts.

Standardize the six allowlisted pre-publication features using fit-block statistics only. Fit ridge (fixed L2=10, unpenalized intercept) to `log(1+views)`. A median-of-fit-block baseline competes on the next chronological selection block using view-count MAE. Select ridge only when it improves MAE, otherwise serve the median. Do not refit on calibration labels. Points are expm1(log estimates), closer to conditional medians than arithmetic expected views. Numeric log outputs are bounded to [0,30] as a defensive cap, not as evidence for extrapolation.

Use absolute log residuals on the final calibration block to form a nominal 90% split-conformal interval with finite-sample order statistic `ceil((n+1)*.9)`. Clip lower bounds to zero. If the seven-day point is below the 24h point, raise it and expand its upper bound to include the adjusted point; apply the identical transformation in backtesting. The resulting intervals have no unconditional coverage guarantee under time drift or this postprocessing. Report empirical temporal coverage.

For each 3×/5× event, the threshold at serving is the median of **all eligible historical posts**, multiplied by 3 or 5. During calibration each post's threshold uses only its own already-mature history. A smoothed residual empirical CDF from the selection block gives raw probabilities. A fixed three-bin calibrator uses the final block's event labels, with five pseudo-observations toward the fit-block event-frequency prior. Each returned probability needs at least five positive and five negative calibration labels and at least ten samples in its selected bin. Otherwise probability is null; a raw CDF value is retained only as a clearly labeled diagnostic, not a calibrated success claim. Calibration does not guarantee accurate real-world probabilities.

Rates are the mean historical per-post seven-day interaction/view ratio across eligible nonzero-view posts. They are simple history estimates, not regressions or statistically calibrated conditional rates. Save rate is included alongside likes, comments and shares.

## Evaluation

`backtest` predicts later posts at their own publication times with an expanding mature-only history, fresh fit/selection/calibration blocks per origin, and no random shuffling. It reports MAE, RMSE, WAPE (null if zero denominator), median-baseline MAE, interval coverage and width. It reports supported-probability Brier scores, fit-only frequency-baseline Brier scores, five-bin ECE and reliability counts. Null probability cases are excluded and coverage-of-test-cases is shown; sparse or repeated-origin estimates require caution. Test outcomes never fit their own model/calibrator. Event thresholds vary by origin, matching the practical rolling account comparison.

`compare` records signed/absolute/percentage errors, interval inclusion, and optional observed interaction-rate errors for one mature post. A single error is not a sample-outside-fit benchmark. No model is certified superior to the baseline unless real account out-of-time metrics support it. Regression selection MAE and calibration diagnostics are not held-out test metrics.

Example CSVs are deliberately artificial, with frequent random bursts to exercise calibration branches. They prove neither commercially useful prediction nor accurate viral probabilities. Other limitations include small samples, selection/survivorship bias, distribution shift, campaign effects, platform changes, correlated posts, uncertainty from measurement and a lack of causal identification. No cross-platform forecast transfer, hyperparameter search, drift adaptation, user-level hierarchical modeling or production monitoring is included. Local deep perception models are optional and separate from the statistical forecast.

Implementation references: [FFprobe metadata documentation](https://www.ffmpeg.org/ffprobe.html), [FFmpeg filter documentation](https://www.ffmpeg.org/ffmpeg-filters.html), and [scikit-learn chronological split discussion](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html). This package implements its own embargoed split and NumPy ridge; it does not depend on scikit-learn.

