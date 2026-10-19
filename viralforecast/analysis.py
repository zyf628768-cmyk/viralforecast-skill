import json
import re
from pathlib import Path

from .common import ForecastError, envelope, number, read_json
from .media import inspect_video


def rules(platform, config=None):
    values = json.loads(Path(__file__).with_name("platforms.json").read_text())
    if platform not in values:
        raise ForecastError(f"Unknown platform: {platform}; choose {', '.join(values)}")
    rule = values[platform]
    if config:
        custom = read_json(config)
        if not isinstance(custom, dict) or set(custom) - set(rule):
            raise ForecastError("Rule JSON must contain only documented rule keys")
        rule.update(custom)
    return {k: number(v, k, 0.001) for k, v in rule.items()}


def text_features(title, caption, segments):
    text = title + " " + caption
    transcript_text = " ".join(s["text"] for s in segments)
    a = set(re.findall(r"\w", text.lower()))
    b = set(re.findall(r"\w", transcript_text.lower()))
    return {"title_length": len(title), "text_length": len(text.strip()),
            "question_count": text.count("?") + text.count("？"),
            "hashtag_count": len(re.findall(r"#[^\s#]+", text)),
            "transcript_chars": len(transcript_text),
            "text_transcript_character_overlap": len(a & b) / len(a | b) if b else None}


def analyze(video, title="", caption="", platform="tiktok", output="media", config=None,
            transcript_path=None, adapter=None, cover=None, understand=False, asr=False,
            models_dir="models", language=None, semantic_labels=None):
    if asr and (transcript_path or adapter):
        raise ForecastError("Choose built-in ASR, transcript import or local adapter, not multiple sources")
    r = rules(platform, config)
    m = inspect_video(video, output, transcript_path, adapter, cover)
    if asr:
        from .speech import transcribe
        m["transcript"] = transcribe(m["audio_path"], models_dir, language)
    if understand:
        from .understanding import understand as run_understanding
        m["understanding"] = run_understanding(video, m, title, caption, models_dir, semantic_labels)
        m["visual_semantics"] = "local_models"
        m["analysis_scope"] += "; local learned object/action/scene/expression models"
    f = text_features(title, caption, m["transcript"]["segments"])
    f.update({"duration_seconds": m["duration_seconds"], "cut_rate": m["cut_rate"]})
    def clamp(x):
        return round(max(0, min(100, x)), 1)
    pace = clamp(100 - 60 * abs(m["cut_rate"] - r["cut_target"]) / r["cut_target"])
    hook = clamp(35 + min(25, m["first_3s_cuts"] * 10) + min(20, f["question_count"] * 10) + (10 if title else 0))
    completion = clamp(90 - 35 * abs(m["duration_seconds"] / r["ideal_duration"] - 1))
    interaction = clamp(35 + min(25, f["question_count"] * 12) + min(15, f["hashtag_count"] * 5))
    scores = {"relative_potential": clamp(.3 * hook + .3 * completion + .2 * interaction + .2 * pace),
              "first_3_seconds": hook, "completion_potential": completion, "interaction_potential": interaction, "pacing": pace}
    risks = ["No topic safety, copyright or factual accuracy verification; expression cues do not reveal true emotions." if understand else "Local vision models were not requested; metadata does not reveal visual subjects or true emotions.",
             "Platform rule values are editable editorial defaults, not official limits or learned ranking rules."]
    tips = ["Review the first 3 seconds manually; state the promised benefit early.",
            "Test one title/cover variation at a time and record mature outcomes."]
    if m["duration_seconds"] > r["max_duration"]:
        risks.append("Duration exceeds this project's configured editorial range.")
    if f["hashtag_count"] > 8:
        risks.append("Many hashtags: inspect relevance manually.")
    if f["title_length"] > r["ideal_title_length"]:
        tips.append("Title exceeds the configured editorial length target; consider a focused shorter version.")
    if m["cut_rate"] < r["cut_target"] / 2:
        tips.append("Review slow sections; scene change counts do not measure storytelling quality.")
    if not m["transcript"]["segments"]:
        tips.append("Supply timestamped transcript JSON or a trusted local transcription adapter for lexical joint features.")
    return envelope("analysis", mode="A", assessment_type="heuristic_not_statistically_calibrated",
                    platform=platform, title=title, caption=caption, features=f, media=m, scores=scores,
                    rules=r, risks=risks, suggestions=tips,
                    limitations=["Scores are hand-written proxies, not audience retention estimates or success probabilities.",
                                 "Text/transcript overlap is lexical; optional visual copy alignment is separately reported in media.understanding."])
