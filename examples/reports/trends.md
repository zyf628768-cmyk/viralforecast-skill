# ViralForecast — trends

Heuristic scores are not calibrated predictions. Statistical estimates are experimental.

Mode: n/a | Status: measured_sample

**SYNTHETIC DATA — software demonstration only; no commercial accuracy claim.**


## 同类内容近期流量

- 截止时间：2026-10-19T00:00:00+00:00；窗口：7.0 天
- 相似内容：24 条；可测量近期增速：24 条
- 同类内容播放增速中位数：250.00 次/小时
- 相对导入样本的热度比：2.78
- 同批样本前后窗口增速比：2.00

### 值得测试的改进

- 同类高增速样本的视频时长中位数约为 17.50秒。可制作一个接近该范围的版本，与当前版本做单变量对照。
- 同类高增速样本的镜头变化频率中位数约为 0.30次/秒。可制作一个接近该范围的版本，与当前版本做单变量对照。
- 前 3 秒启发式评分偏低：把核心结果、冲突或收益前置，测试不同开场。

样本相对热度不等于平台内部推流或全平台趋势；改进建议是待验证的实验。

- This is the imported sample's observed attention, not platform-wide recommendation exposure or ranking policy.
- Lexical TF-IDF similarity uses English words and Chinese character n-grams; it is not visual semantic similarity.
- At least two snapshots one hour apart inside each window are required for velocity. Single snapshots never imply recent growth.
- Sample heat is not controlled for creator size, content age, promotion or seasonality. Age-banded cumulative views are descriptive only.
- Recommendations are observational experiments; no promised traffic uplift or causal inference. Trend context never changes calibrated forecasts automatically.

## Full result

```json
{
  "schema_version": "1.0",
  "kind": "trends",
  "platform": "tiktok",
  "as_of": "2026-10-19T00:00:00+00:00",
  "window_days": 7.0,
  "query": {
    "title": "视频开场技巧 video opening tips",
    "caption": "提升内容吸引力 how to improve an opening #video",
    "minimum_lexical_similarity": 0.15,
    "excluded_account": null
  },
  "status": "measured_sample",
  "data_source": "synthetic",
  "coverage": {
    "recent_sample_posts": 40,
    "similar_posts": 24,
    "similar_with_velocity": 24,
    "baseline_with_velocity": 40,
    "paired_windows": 24,
    "excluded_future_snapshots": 0
  },
  "heat": {
    "type": "sample_relative_attention_proxy",
    "similar_median_views_per_hour": 250.0,
    "sample_baseline_median_views_per_hour": 90.0,
    "relative_heat_ratio": 2.7777777777777777,
    "band": "higher_than_sample",
    "paired_window_momentum_ratio": 2.0,
    "internal_recommendation_exposure": null
  },
  "age_banded_view_summaries": {
    "under_24h": {
      "posts": 0,
      "median_observed_views": null
    },
    "24_to_72h": {
      "posts": 0,
      "median_observed_views": null
    },
    "3_to_7d": {
      "posts": 0,
      "median_observed_views": null
    },
    "7d_plus": {
      "posts": 24,
      "median_observed_views": 69000.0
    }
  },
  "similar_content": [
    {
      "content_id": "TREND-SIM-000",
      "account_id": "peer-0",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 5520.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 20.0,
        "view_increment": 3360.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 10.0,
        "view_increment": 1680.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 15.0,
        "cut_rate": 0.2,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-001",
      "account_id": "peer-1",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 11040.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 40.0,
        "view_increment": 6720.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 20.0,
        "view_increment": 3360.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 16.0,
        "cut_rate": 0.20500000000000002,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-002",
      "account_id": "peer-2",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 16560.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 60.0,
        "view_increment": 10080.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 30.0,
        "view_increment": 5040.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 17.0,
        "cut_rate": 0.21000000000000002,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-003",
      "account_id": "peer-3",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 22080.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 80.0,
        "view_increment": 13440.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 40.0,
        "view_increment": 6720.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 18.0,
        "cut_rate": 0.21500000000000002,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-004",
      "account_id": "peer-4",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 27600.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 100.0,
        "view_increment": 16800.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 50.0,
        "view_increment": 8400.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 19.0,
        "cut_rate": 0.22,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-005",
      "account_id": "peer-5",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 33120.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 120.0,
        "view_increment": 20160.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 60.0,
        "view_increment": 10080.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 15.0,
        "cut_rate": 0.225,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-006",
      "account_id": "peer-6",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 38640.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 140.0,
        "view_increment": 23520.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 70.0,
        "view_increment": 11760.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 16.0,
        "cut_rate": 0.23,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-007",
      "account_id": "peer-7",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 44160.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 160.0,
        "view_increment": 26880.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 80.0,
        "view_increment": 13440.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 17.0,
        "cut_rate": 0.23500000000000001,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-008",
      "account_id": "peer-0",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 49680.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 180.0,
        "view_increment": 30240.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 90.0,
        "view_increment": 15120.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 18.0,
        "cut_rate": 0.24000000000000002,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-009",
      "account_id": "peer-1",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 55200.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 200.0,
        "view_increment": 33600.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 100.0,
        "view_increment": 16800.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 19.0,
        "cut_rate": 0.245,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-010",
      "account_id": "peer-2",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 60720.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 220.0,
        "view_increment": 36960.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 110.0,
        "view_increment": 18480.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 15.0,
        "cut_rate": 0.25,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-011",
      "account_id": "peer-3",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 66240.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 240.0,
        "view_increment": 40320.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 120.0,
        "view_increment": 20160.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 16.0,
        "cut_rate": 0.255,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-012",
      "account_id": "peer-4",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 71760.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 260.0,
        "view_increment": 43680.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 130.0,
        "view_increment": 21840.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 17.0,
        "cut_rate": 0.26,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-013",
      "account_id": "peer-5",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 77280.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 280.0,
        "view_increment": 47040.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 140.0,
        "view_increment": 23520.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 18.0,
        "cut_rate": 0.265,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-014",
      "account_id": "peer-6",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 82800.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 300.0,
        "view_increment": 50400.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 150.0,
        "view_increment": 25200.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 19.0,
        "cut_rate": 0.27,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-015",
      "account_id": "peer-7",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 88320.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 320.0,
        "view_increment": 53760.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 160.0,
        "view_increment": 26880.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 15.0,
        "cut_rate": 0.275,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-016",
      "account_id": "peer-0",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 93840.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 340.0,
        "view_increment": 57120.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 170.0,
        "view_increment": 28560.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 16.0,
        "cut_rate": 0.28,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-017",
      "account_id": "peer-1",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 99360.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 360.0,
        "view_increment": 60480.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 180.0,
        "view_increment": 30240.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 17.0,
        "cut_rate": 0.28500000000000003,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-018",
      "account_id": "peer-2",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 104880.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 380.0,
        "view_increment": 63840.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 190.0,
        "view_increment": 31920.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 18.0,
        "cut_rate": 0.29000000000000004,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-019",
      "account_id": "peer-3",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 110400.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 400.0,
        "view_increment": 67200.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 200.0,
        "view_increment": 33600.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 19.0,
        "cut_rate": 0.29500000000000004,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-020",
      "account_id": "peer-4",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 115920.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 420.0,
        "view_increment": 70560.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 210.0,
        "view_increment": 35280.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 15.0,
        "cut_rate": 0.30000000000000004,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-021",
      "account_id": "peer-5",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 121440.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 440.0,
        "view_increment": 73920.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 220.0,
        "view_increment": 36960.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 16.0,
        "cut_rate": 0.305,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-022",
      "account_id": "peer-6",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 126960.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 460.0,
        "view_increment": 77280.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 230.0,
        "view_increment": 38640.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 17.0,
        "cut_rate": 0.31,
        "title_length": 25,
        "hashtag_count": 1
      }
    },
    {
      "content_id": "TREND-SIM-023",
      "account_id": "peer-7",
      "title": "视频开场技巧 video opening tips",
      "similarity": 1.0,
      "published_at": "2026-10-03T00:00:00+00:00",
      "observed_at": "2026-10-19T00:00:00+00:00",
      "observed_views": 132480.0,
      "age_hours": 384.0,
      "age_band": "7d_plus",
      "recent_velocity": {
        "views_per_hour": 480.0,
        "view_increment": 80640.0,
        "hours": 168.0,
        "from": "2026-10-12T00:00:00+00:00",
        "to": "2026-10-19T00:00:00+00:00"
      },
      "previous_velocity": {
        "views_per_hour": 240.0,
        "view_increment": 40320.0,
        "hours": 168.0,
        "from": "2026-10-05T00:00:00+00:00",
        "to": "2026-10-12T00:00:00+00:00"
      },
      "features": {
        "duration_seconds": 18.0,
        "cut_rate": 0.315,
        "title_length": 25,
        "hashtag_count": 1
      }
    }
  ],
  "improvements": [
    {
      "priority": "test",
      "feature": "duration_seconds",
      "current": 6.0,
      "peer_top_quartile_median": 17.5,
      "peer_interquartile_range": [
        16.25,
        18.0
      ],
      "evidence_posts": 6,
      "evidence_ids": [
        "TREND-SIM-023",
        "TREND-SIM-022",
        "TREND-SIM-021",
        "TREND-SIM-020",
        "TREND-SIM-019",
        "TREND-SIM-018"
      ],
      "suggestion": "同类高增速样本的视频时长中位数约为 17.50秒。可制作一个接近该范围的版本，与当前版本做单变量对照。",
      "interpretation": "observational association; not evidence that changing this feature increases views"
    },
    {
      "priority": "test",
      "feature": "cut_rate",
      "current": 0.16666666666666666,
      "peer_top_quartile_median": 0.3025,
      "peer_interquartile_range": [
        0.29625,
        0.30874999999999997
      ],
      "evidence_posts": 6,
      "evidence_ids": [
        "TREND-SIM-023",
        "TREND-SIM-022",
        "TREND-SIM-021",
        "TREND-SIM-020",
        "TREND-SIM-019",
        "TREND-SIM-018"
      ],
      "suggestion": "同类高增速样本的镜头变化频率中位数约为 0.30次/秒。可制作一个接近该范围的版本，与当前版本做单变量对照。",
      "interpretation": "observational association; not evidence that changing this feature increases views"
    },
    {
      "priority": "review",
      "feature": "opening",
      "suggestion": "前 3 秒启发式评分偏低：把核心结果、冲突或收益前置，测试不同开场。",
      "interpretation": "content heuristic, not a measured causal traffic effect"
    }
  ],
  "limitations": [
    "This is the imported sample's observed attention, not platform-wide recommendation exposure or ranking policy.",
    "Lexical TF-IDF similarity uses English words and Chinese character n-grams; it is not visual semantic similarity.",
    "At least two snapshots one hour apart inside each window are required for velocity. Single snapshots never imply recent growth.",
    "Sample heat is not controlled for creator size, content age, promotion or seasonality. Age-banded cumulative views are descriptive only.",
    "Recommendations are observational experiments; no promised traffic uplift or causal inference. Trend context never changes calibrated forecasts automatically."
  ]
}
```
