"""Built-in CPU/int8 multilingual Whisper transcription, strictly local."""
from .common import ForecastError
from .models import require


def transcribe(audio, directory, language=None):
    if audio is None:
        return {"status":"no_audio","segments":[]}
    path, provenance=require(directory,"speech")
    try:
        from faster_whisper import WhisperModel
        model=WhisperModel(str(path),device="cpu",compute_type="int8",local_files_only=True,cpu_threads=4)
        segments,info=model.transcribe(audio,language=language,beam_size=3,vad_filter=True,
                                      condition_on_previous_text=False)
        result=[{"start":float(s.start),"end":float(s.end),"text":s.text.strip()} for s in segments if s.text.strip()]
        return {"status":"built_in_local_asr","segments":result,"language":info.language,
                "language_score":float(info.language_probability),"model":provenance["source"],
                "revision":provenance.get("revision"),"limitations":["ASR can omit or hallucinate words; review before publishing."]}
    except ImportError as exc:
        raise ForecastError('ASR dependencies missing; install .[understanding]') from exc
    except Exception as exc:
        raise ForecastError(f"Built-in local ASR failed: {exc}") from exc
