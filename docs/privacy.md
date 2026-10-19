# Privacy / 隐私

Version 0.2 explicitly downloads public model weights only through `python -m viralforecast.models --download`. Hugging Face snapshots are pinned and hashed; runtime inference is local-only. Face crops and transcript results remain in memory or local reports and are not uploaded. No identity recognition, psychological profiling or true-emotion inference is performed.

Analysis, fitting and reporting run on the user's machine. The implementation sends no media, transcripts or account data to an API. The application has no telemetry, API keys, purchase flow or production server access. Dependency installation and explicitly requested binary installation require network access; inference does not.

Output reports contain the supplied title, caption, features, transcript and local asset paths. Extracted stills/WAVs are stored in the selected output folder. Treat them as private, choose a local folder you control, and delete it when no longer required. This is ordinary deletion, not cryptographic erasure. Reports do not copy entire historical CSVs, but forecasts/backtests expose selected account metrics and IDs. Avoid publishing output reports containing private data.

An opt-in transcription adapter is arbitrary trusted Python code and can have its own network/data behavior; review it separately. The provided demo adapter test does not use a real ASR service. Media demuxing restricts network protocols; keep FFmpeg/Pillow and your operating system maintained when processing untrusted files.

Release packaging excludes the development virtual environment, runtime tools, temporary files and arbitrary output directories. Only explicitly synthetic demonstration artifacts are included. The MIT license applies to this project's code. FFmpeg, Python and installed packages retain their own licenses; external FFmpeg binaries are not bundled in the source ZIP.
