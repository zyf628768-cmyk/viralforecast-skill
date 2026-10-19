# Version 0.2 local model validation

The Chinese homepage introduction was rewritten and the requested introductory simulated-data sentence removed. Statistical limitations and synthetic labels remain in the methods, examples and reports.

Five actual pretrained models were downloaded from their public sources and loaded locally: SSDLite320 (COCO), R3D-18 (Kinetics-400), CLIP ViT-B/32, ViT FER2013 expression classifier and faster-whisper tiny multilingual. Hugging Face revisions and file hashes are recorded in the user's local model manifest. No pretrained weight is included in the public repository or source ZIP.

The ordinary suite initially passed 48 tests with the large-model integration test skipped. The real-model suite explicitly sets `VIRALFORECAST_MODELS` and offline environment flags, enabling that integration test rather than claiming stub coverage as learned-model validation.

Actual full-model result: **49 passed in 25.97s**, including the downloaded-model integration test. The saved positive-model JSON also passed the output Schema and exact HTML payload check; the expected spoken phrase was present in the actual ASR output.

Final source recheck: **49 passed in 32.89s**. The updated [four-environment CI run](https://github.com/zyf628768-cmyk/viralforecast-skill/actions/runs/39224579401) completed successfully on Windows/Ubuntu × Python 3.10/3.12. CI omits large local weights and therefore explicitly skips the single real-weight integration case; the local result above includes it.

An actual CLI run used a public-domain scikit-image astronaut test image in a short MP4 with locally synthesized Windows SAPI speech. Results:

- Object detector returned a person box (model score about 0.878).
- Face detector found face regions; the expression model classified visible expression cues. No identity recognition or true-emotion claim is made.
- CLIP produced scene candidates and copy cosine similarity. These are constrained image/text matches, not an exhaustive explanation of the video.
- R3D processed temporal clips and returned `uncertain` on this static-photo fixture; its top candidate was incorrect and below threshold. This validates execution and honest uncertainty, not action-recognition accuracy.
- Built-in ASR produced: “This is a local video test.” and “We can improve the opening before we publish.” This validates transcription on one clear synthetic English utterance, not general ASR quality.
- JSON, Markdown and HTML reports were actually generated locally.

First ASR execution failed because PyAV 19 removed the `metadata_errors` argument used by faster-whisper 1.2.1. The dependency was constrained to `av>=11,<17`; PyAV 16.1.0 was installed and the same real CLI rerun succeeded. This is a genuine compatibility repair, not a fabricated test record.

The no-face, non-speech fixture is a generated two-color video with sine audio. The optional real integration test checks all vision modules execute, no faces produce an explicit no-face result, and non-speech produces no transcript. Missing manifest/files, corrupted model hashes, invalid scores and conflicting transcript sources are covered separately.

Sources: [scikit-image public-domain fixture description](https://scikit-image.org/docs/stable/api/skimage.data), [model details and setup](local-understanding.md). Positive fixture media, raw local logs and model caches are retained locally and are not publicly uploaded. The earlier CI report is for version 0.1; current CI validates the lightweight suite without downloading heavy model weights. None of these checks establishes audience prediction accuracy or broad scene/action/expression/ASR accuracy.

