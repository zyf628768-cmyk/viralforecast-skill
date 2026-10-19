"""Deterministic synthetic demo fixtures. Not audience-performance evidence."""
import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image

from viralforecast.history import REQUIRED
from viralforecast.media import binary, run


def generate(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)
    with (root / "synthetic_history.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(REQUIRED) + ["data_source"])
        writer.writeheader()
        for i in range(260):
            duration = rng.uniform(8, 80)
            cuts = rng.uniform(.02, .6)
            # Deliberately frequent artificial bursts make probability plumbing testable.
            burst = 12 if rng.random() < .32 else 1
            views = int(max(1, (800 + 900 * cuts) * burst * rng.lognormvariate(0, .4)))
            writer.writerow({"content_id": f"SIM-{i:04}", "account_id": "demo", "platform": "tiktok",
                             "published_at": (datetime(2020,1,1,tzinfo=timezone.utc) + timedelta(days=9*i)).isoformat(),
                             "duration_seconds": round(duration,3), "cut_rate": round(cuts,4), "title_length": rng.randint(8,60),
                             "text_length": rng.randint(30,200), "question_count": rng.randint(0,3), "hashtag_count": rng.randint(0,6),
                             "views_24h": int(views * rng.uniform(.3,.7)), "views_7d": views,
                             "likes_7d": int(views*.05), "comments_7d": int(views*.005),
                             "shares_7d": int(views*.01), "saves_7d": int(views*.015), "data_source": "synthetic"})
    # One valid two-scene, six-second portrait MP4 plus sine audio, generated locally.
    run([binary("ffmpeg"), "-nostdin", "-y", "-f", "lavfi", "-i", "color=c=red:s=180x320:r=24:d=3",
         "-f", "lavfi", "-i", "color=c=blue:s=180x320:r=24:d=3",
         "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=16000:duration=6",
         "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]", "-map", "[v]", "-map", "2:a",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(root / "demo.mp4")])
    Image.new("RGB", (180,320), "navy").save(root / "cover.png")
    (root / "transcript.json").write_text(json.dumps({"segments": [{"start":0,"end":2.5,"text":"How to make a simple video?"},
                                                                 {"start":3,"end":5.5,"text":"Try one clear change today."}]}), encoding="utf-8")
    (root / "actual.json").write_text(json.dumps({"account_id":"demo", "platform":"tiktok", "published_at":"2026-10-20T00:00:00Z",
                                                 "observed_at":"2026-10-28T00:00:00Z", "views_24h":1500,"views_7d":3500,
                                                 "data_source":"synthetic"}), encoding="utf-8")
    (root / "empty.csv").write_text("", encoding="utf-8")
    (root / "invalid.csv").write_text("published_at,views_7d\nnot-a-date,-1\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="examples/data")
    generate(p.parse_args().out)
