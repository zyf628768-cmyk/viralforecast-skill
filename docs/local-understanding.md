# Local content understanding

Install the optional extension (CPU builds of Torch are recommended on Windows):

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[understanding]"
.\.venv\Scripts\python.exe -m viralforecast.models --download --directory models
.\.venv\Scripts\viralforecast.exe analyze --video examples/data/demo.mp4 --title "A color demonstration" --understand --asr --models-dir models --out outputs/understood
```

The download command explicitly obtains public weights, pins Hugging Face snapshots to their resolved commit IDs and writes SHA256 checksums. Subsequent `analyze` calls load only these local files, verify checksums, never download a model implicitly and never upload media. Dependencies and model weights require substantial disk space; weights are excluded from the repository and source release. The optional extension is not needed for metadata-only analysis or forecasting.

| Capability | Actual implementation | Boundary |
|---|---|---|
| Objects | Torchvision SSDLite320 MobileNetV3, COCO weights, sampled-frame boxes and labels | Fixed object vocabulary; threshold 0.5; no tracking |
| Actions | Torchvision R3D-18, Kinetics-400 weights, up to three two-second clips | Temporal classification, not action detection throughout an entire video; uncertain below 0.4 |
| Visual semantics | CLIP ViT-B/32 ranks configurable scene descriptions and computes frame/copy cosine similarity | Basic semantic matching, not general video reasoning; English-oriented, Chinese copy may perform poorly |
| Expression cues | OpenCV frontal face regions + ViT fine-tuned on FER2013 | Visible expressions only; no mood, intent or mental-health inference; no face means abstention |
| Built-in ASR | faster-whisper tiny multilingual, CPU int8, VAD, timestamped segments | Language auto-detection or `--language zh/en`; can hallucinate or omit speech |

`--understand` enables the first four capabilities. `--asr` independently enables built-in transcription. Imported transcripts, custom transcribers and built-in ASR are mutually exclusive. Silent videos return `no_audio`; non-speech audio may yield empty segments. The plain CLI remains lightweight when neither flag is set.

Use `--semantic-labels labels.json` with a JSON array of 2–64 English descriptions, each at most 200 characters. CLIP scores depend on the candidate list; a softmax score is not a calibrated probability that a label is true. All model provenance and uncertain/no-face states are retained in the report. Model results do not enter the six-feature statistical forecast automatically, because existing histories do not contain consistent matching training features.

Sources and separate model licenses: [Torchvision detector](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.detection.ssdlite320_mobilenet_v3_large.html), [R3D-18](https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.video.r3d_18.html), [CLIP model card](https://huggingface.co/openai/clip-vit-base-patch32), [expression model card](https://huggingface.co/trpakov/vit-face-expression), [faster-whisper](https://github.com/SYSTRAN/faster-whisper). This project is MIT; optional weights and dependencies retain their own terms. CLIP's model card emphasizes research use and domain-specific validation. Neither expressions nor model similarity can prove a person's real emotion or audience response.
