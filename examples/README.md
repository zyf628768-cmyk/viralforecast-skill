# Synthetic examples

Run `python examples/generate.py --out examples/data` after installing the project. It generates a six-second, two-scene portrait H.264 MP4 with sine audio, a navy PNG cover, an illustrative timestamped transcript, 260 deterministic simulated historical posts (seed 42, every nine days), invalid/empty CSV fixtures and simulated mature actual outcomes.

The transcript does not transcribe the sine wave; it tests the imported-transcript interface. Burst events are deliberately frequent in the CSV to exercise calibration code. Every generated history row has `data_source=synthetic`. The generated actual metrics are also synthetic. No performance result from this data is evidence of commercial forecasting accuracy.

`rules.json` demonstrates editable editorial defaults. Use real pre-publication features computed with the same definitions when importing a real CSV; see `docs/data.md`. Generated data are included in the local release ZIP for reproducibility, while `.gitignore` keeps them out of source commits by default.
