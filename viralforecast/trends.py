"""Account/platform export analysis. Observed attention is not internal recommendation exposure."""
import csv
import math
import re
from collections import Counter, defaultdict
from datetime import timedelta

import numpy as np

from .analysis import rules
from .common import ForecastError, date, envelope, number

REQUIRED=("content_id","account_id","platform","published_at","observed_at","title","caption","views")
OPTIONAL=("duration_seconds","cut_rate","likes","comments","shares","saves")


def tokens(text):
    text=text.lower()
    words=re.findall(r"[a-z0-9]+",text)
    result=words+[a+" "+b for a,b in zip(words,words[1:])]
    for segment in re.findall(r"[\u3400-\u9fff]+",text):
        if len(segment)==1:
            result.append(segment)
        for n in (2,3):
            result.extend(segment[i:i+n] for i in range(len(segment)-n+1))
    return Counter(result)


def similarity(query, documents):
    """Fit TF-IDF only on eligible snapshots; cosine similarity is lexical, not semantic."""
    docs=[tokens(d) for d in documents]
    q=tokens(query)
    df=Counter(t for d in docs for t in d)
    idf={t:math.log((len(docs)+1)/(count+1))+1 for t,count in df.items()}
    def vector(c):
        return {t:(1+math.log(n))*idf.get(t,math.log(len(docs)+1)+1) for t,n in c.items()}
    vq=vector(q)
    normq=math.sqrt(sum(x*x for x in vq.values()))
    result=[]
    for doc in docs:
        v=vector(doc)
        norm=math.sqrt(sum(x*x for x in v.values()))
        result.append(sum(value*v.get(t,0) for t,value in vq.items())/(normq*norm) if normq and norm else 0.0)
    return result


def load_snapshots(path, platform, as_of, exclude_account=None):
    rules(platform)
    cutoff=date(as_of)
    groups=defaultdict(list)
    excluded_future=0
    try:
        with open(path,encoding="utf-8-sig",newline="") as f:
            reader=csv.DictReader(f)
            if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)):
                raise ForecastError("Trend CSV is empty or has duplicate headers")
            if set(REQUIRED)-set(reader.fieldnames):
                raise ForecastError("Trend CSV missing columns: "+", ".join(sorted(set(REQUIRED)-set(reader.fieldnames))))
            seen=set()
            for line,r in enumerate(reader,2):
                if r.get("platform")!=platform or (exclude_account and r.get("account_id")==exclude_account):
                    continue
                if None in r or any(r.get(k) is None for k in REQUIRED):
                    raise ForecastError(f"Malformed trend CSV row {line}")
                observed=date(r["observed_at"])
                if observed>cutoff:
                    excluded_future+=1
                    continue
                published=date(r["published_at"])
                if published>observed:
                    raise ForecastError(f"Trend observation precedes publication at row {line}")
                if not r["content_id"].strip() or not r["account_id"].strip():
                    raise ForecastError("Trend content_id and account_id must be nonempty")
                identity=(r["account_id"],r["content_id"])
                key=(*identity,observed)
                if key in seen:
                    raise ForecastError("Duplicate trend content snapshot")
                seen.add(key)
                r["views"]=number(r["views"],f"row {line} views")
                for k in OPTIONAL:
                    r[k]=number(r[k],k,.001 if k=="duration_seconds" else 0) if r.get(k) not in (None,"") else None
                if r.get("data_source") not in (None,"","real","synthetic"):
                    raise ForecastError("Trend data_source must be real or synthetic")
                r["published_at"],r["observed_at"]=published,observed
                groups[identity].append(r)
    except (OSError,UnicodeError,csv.Error) as exc:
        raise ForecastError(f"Cannot read trend CSV: {exc}") from exc
    for rows in groups.values():
        rows.sort(key=lambda r:r["observed_at"])
        if len({r["published_at"] for r in rows})!=1:
            raise ForecastError("Publication time must be stable across content snapshots")
    if not groups:
        raise ForecastError("No eligible trend snapshots for the selected platform/time/account filter")
    return groups,excluded_future


def velocity(rows, start, end):
    inside=[r for r in rows if start<=r["observed_at"]<=end]
    if len(inside)<2:
        return None
    first,last=inside[0],inside[-1]
    hours=(last["observed_at"]-first["observed_at"]).total_seconds()/3600
    if hours<1 or last["views"]<first["views"]:
        return None
    return {"views_per_hour":(last["views"]-first["views"])/hours,"view_increment":last["views"]-first["views"],
            "hours":hours,"from":first["observed_at"].isoformat(),"to":last["observed_at"].isoformat()}


def profile(row):
    text=row["title"]+" "+row["caption"]
    return {"duration_seconds":row.get("duration_seconds"),"cut_rate":row.get("cut_rate"),
            "title_length":len(row["title"]),"hashtag_count":len(re.findall(r"#[^\s#]+",text))}


def age_band(hours):
    return "under_24h" if hours<24 else "24_to_72h" if hours<72 else "3_to_7d" if hours<168 else "7d_plus"


def improvement_actions(analysis, peers):
    result=[]
    ranked=sorted([p for p in peers if p["recent_velocity"]],key=lambda p:p["recent_velocity"]["views_per_hour"],reverse=True)
    top=ranked[:max(3,math.ceil(len(ranked)*.25))]
    if len(ranked)>=12:
        for key,label,unit in [("duration_seconds","视频时长","秒"),("cut_rate","镜头变化频率","次/秒"),("title_length","标题长度","字符")]:
            values=[p["features"][key] for p in top if p["features"].get(key) is not None]
            current=analysis.get("features",{}).get(key)
            if len(values)>=3 and current is not None:
                low,median,high=[float(x) for x in np.quantile(values,[.25,.5,.75])]
                if current<low or current>high:
                    result.append({"priority":"test","feature":key,"current":float(current),
                                   "peer_top_quartile_median":median,"peer_interquartile_range":[low,high],
                                   "evidence_posts":len(values),"evidence_ids":[p["content_id"] for p in top if p["features"].get(key) is not None],
                                   "suggestion":f"同类高增速样本的{label}中位数约为 {median:.2f}{unit}。可制作一个接近该范围的版本，与当前版本做单变量对照。",
                                   "interpretation":"observational association; not evidence that changing this feature increases views"})
    if analysis.get("scores",{}).get("first_3_seconds",100)<60:
        result.append({"priority":"review","feature":"opening","suggestion":"前 3 秒启发式评分偏低：把核心结果、冲突或收益前置，测试不同开场。","interpretation":"content heuristic, not a measured causal traffic effect"})
    if not result:
        result.append({"priority":"collect_evidence","suggestion":"目前没有足够证据定位稳定的流量差异。补齐同类样本的多次快照，并逐项测试开场、标题和封面。"})
    return result


def trends(csv_path, analysis, as_of, days=7, min_similarity=.15, exclude_account=None):
    if not isinstance(analysis,dict) or analysis.get("kind")!="analysis":
        raise ForecastError("Trends require a saved analysis result")
    days=number(days,"trend days",1,30)
    threshold=number(min_similarity,"minimum similarity",0,1)
    platform=analysis.get("platform")
    groups,future=load_snapshots(csv_path,platform,as_of,exclude_account)
    end=date(as_of)
    start=end-timedelta(days=days)
    previous=start-timedelta(days=days)
    latest=[rs[-1] for rs in groups.values() if rs[-1]["observed_at"]>=start]
    scores=similarity(analysis.get("title","")+" "+analysis.get("caption",""),[r["title"]+" "+r["caption"] for r in latest])
    peers=[]
    all_recent=[]
    for row,score in zip(latest,scores):
        rs=groups[(row["account_id"],row["content_id"])]
        recent=velocity(rs,start,end)
        prior=velocity(rs,previous,start)
        if recent:
            all_recent.append(recent["views_per_hour"])
        if score<threshold:
            continue
        age=(row["observed_at"]-row["published_at"]).total_seconds()/3600
        peers.append({"content_id":row["content_id"],"account_id":row["account_id"],"title":row["title"],
                      "similarity":float(score),"published_at":row["published_at"].isoformat(),"observed_at":row["observed_at"].isoformat(),
                      "observed_views":row["views"],"age_hours":age,"age_band":age_band(age),
                      "recent_velocity":recent,"previous_velocity":prior,"features":profile(row)})
    peers.sort(key=lambda p:p["similarity"],reverse=True)
    measured=[p for p in peers if p["recent_velocity"]]
    med=float(np.median([p["recent_velocity"]["views_per_hour"] for p in measured])) if measured else None
    baseline=float(np.median(all_recent)) if all_recent else None
    ratio=med/baseline if med is not None and baseline and len(measured)>=5 and len(all_recent)>=10 else None
    paired=[p for p in measured if p["previous_velocity"]]
    current_pair=float(np.median([p["recent_velocity"]["views_per_hour"] for p in paired])) if len(paired)>=5 else None
    previous_pair=float(np.median([p["previous_velocity"]["views_per_hour"] for p in paired])) if len(paired)>=5 else None
    momentum=current_pair/previous_pair if current_pair is not None and previous_pair else None
    sources={r.get("data_source") or "unspecified" for rs in groups.values() for r in rs}
    bands={}
    for band in ("under_24h","24_to_72h","3_to_7d","7d_plus"):
        ps=[p for p in peers if p["age_band"]==band]
        bands[band]={"posts":len(ps),"median_observed_views":float(np.median([p["observed_views"] for p in ps])) if ps else None}
    return envelope("trends",platform=platform,as_of=end.isoformat(),window_days=days,
                    query={"title":analysis.get("title",""),"caption":analysis.get("caption",""),
                           "minimum_lexical_similarity":threshold,"excluded_account":exclude_account},
                    status="measured_sample" if len(measured)>=5 else "insufficient_velocity_samples",
                    data_source="synthetic" if sources=={"synthetic"} else "user_declared_real_unverified" if sources=={"real"} else "mixed_or_unspecified",
                    coverage={"recent_sample_posts":len(latest),"similar_posts":len(peers),"similar_with_velocity":len(measured),
                              "baseline_with_velocity":len(all_recent),"paired_windows":len(paired),"excluded_future_snapshots":future},
                    heat={"type":"sample_relative_attention_proxy","similar_median_views_per_hour":med,
                          "sample_baseline_median_views_per_hour":baseline,"relative_heat_ratio":ratio,
                          "band":"higher_than_sample" if ratio is not None and ratio>=1.5 else "lower_than_sample" if ratio is not None and ratio<=.67 else "near_sample" if ratio is not None else "insufficient_support",
                          "paired_window_momentum_ratio":momentum,
                          "internal_recommendation_exposure":None},
                    age_banded_view_summaries=bands,similar_content=peers,
                    improvements=improvement_actions(analysis,peers),
                    limitations=["This is the imported sample's observed attention, not platform-wide recommendation exposure or ranking policy.",
                                 "Lexical TF-IDF similarity uses English words and Chinese character n-grams; it is not visual semantic similarity.",
                                 "At least two snapshots one hour apart inside each window are required for velocity. Single snapshots never imply recent growth.",
                                 "Sample heat is not controlled for creator size, content age, promotion or seasonality. Age-banded cumulative views are descriptive only.",
                                 "Recommendations are observational experiments; no promised traffic uplift or causal inference. Trend context never changes calibrated forecasts automatically."])
