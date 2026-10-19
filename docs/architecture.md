# Architecture / 架构

`CLI → input validation → media or history pipeline → result envelope → JSON/Markdown/HTML`.

- `media.py`: local FFprobe metadata, FFmpeg scene filter and stills, 16 kHz mono WAV, optional local transcript adapter and cover pixel statistics. Subprocess argument lists avoid shell interpolation. Media subprocesses time out after 180 seconds; maximum accepted duration is two hours. No networking protocols are allowed in media demuxing.
- `analysis.py`: seven editable platform profiles, lexical features and transparent 0–100 editorial heuristic scores. Profiles are project defaults, not current platform policy or official upload constraints.
- `history.py`: strict CSV validation, one account/platform, explicit feature allowlist, deduplication, UTC date normalization and mature-outcome filtering.
- `model.py`: NumPy ridge regression, median baseline, temporal selection and calibration, event support checks, expanding-origin evaluation and error comparison.
- `reporting.py`: canonical JSON plus escaped, self-contained HTML and Markdown containing complete results. HTML executes no scripts and fetches no remote content.
- `cli.py`: five executable commands; success exit 0, validation/dependency/media error exit 2, JSON diagnostic on stderr. Argparse usage errors also exit 2 but use argparse's normal text output.

No paid API, GPU, database or web service is required. The optional understanding extension uses explicitly downloaded local pretrained weights; metadata/forecast modes need none. Python 3.10+ is supported by source and configured in CI. Actual validation is recorded separately.

The CLI reads local files rather than exposing an upload web server. A future UI can call the same Python functions. Version 0.2 adds `models.py`, `understanding.py` and `speech.py` for explicitly enabled local models; see `local-understanding.md` for implementation boundaries.
