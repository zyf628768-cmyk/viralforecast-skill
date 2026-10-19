"""Generate deterministic, explicitly synthetic multi-snapshot peer traffic."""
import argparse
import csv
from datetime import datetime,timedelta,timezone
from pathlib import Path

FIELDS=["content_id","account_id","platform","published_at","observed_at","title","caption","views",
        "duration_seconds","cut_rate","likes","comments","shares","saves","data_source"]


def generate(path):
    p=Path(path)
    p.parent.mkdir(parents=True,exist_ok=True)
    end=datetime(2026,10,19,tzinfo=timezone.utc)
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS)
        w.writeheader()
        for i in range(40):
            similar=i<24
            for days in (14,8,7,1,0):
                current=end-timedelta(days=days)
                speed=(i+1)*10 if similar else 30
                elapsed=(current-(end-timedelta(days=16))).total_seconds()/3600
                views=int(speed*elapsed+(max(0,7-days)*24*speed if similar else 0))
                w.writerow(dict(content_id=f"TREND-SIM-{i:03}",account_id=f"peer-{i%8}",platform="tiktok",
                                published_at=(end-timedelta(days=16)).isoformat(),observed_at=current.isoformat(),
                                title="视频开场技巧 video opening tips" if similar else "宠物日常 cute pet diary",
                                caption="提升内容吸引力 how to improve an opening #video" if similar else "A quiet animal afternoon #pet",
                                views=views,duration_seconds=15+i%5,cut_rate=.2+i*.005,
                                likes=int(views*.05),comments=int(views*.004),shares=int(views*.01),saves=int(views*.012),data_source="synthetic"))
    return p


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="examples/data/synthetic_trends.csv")
    print(generate(p.parse_args().out))
