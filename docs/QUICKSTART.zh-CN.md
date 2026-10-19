# ViralForecast v0.2.0 使用说明

## 1. 下载与安装

下载 Release 附件 `viralforecast-skill-0.2.0.zip`，解压后进入 `viralforecast-skill` 文件夹。ZIP 内含完整源码、Skill、测试、JSON Schema、模拟示例和文档；大型预训练模型、Python 本身和 FFmpeg 需另行安装。

需要 Python 3.10+、FFmpeg 和 FFprobe。Windows 推荐安装 Python 3.12，然后在 PowerShell 中运行：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,media]"
$env:FFPROBE = 'C:\ffmpeg\bin\ffprobe.exe'
$env:FFMPEG = 'C:\ffmpeg\bin\ffmpeg.exe'
.\.venv\Scripts\viralforecast.exe --help
```

FFmpeg 已在 PATH 时不需要设置两个环境变量。`media` 可提供 FFmpeg 备用执行文件，但不提供 FFprobe。Linux/macOS 对应使用 `.venv/bin/python` 和 `.venv/bin/viralforecast`。

## 2. 无历史数据：先分析内容

```powershell
.\.venv\Scripts\python.exe examples/generate.py --out examples/data
.\.venv\Scripts\viralforecast.exe analyze --video examples/data/demo.mp4 --title "视频开场技巧 video opening tips" --caption "提升内容吸引力 #video" --platform tiktok --out outputs/my-video
```

把示例路径换成自己的视频，按需添加 `--cover cover.png`。输出包含 JSON、Markdown、HTML，以及关键帧和音轨。此模式的分数是启发式评估，不会凭空给出播放量或爆款概率。

平台标识：`tiktok`、`youtube-shorts`、`instagram-reels`、`douyin`、`kuaishou`、`xiaohongshu`、`bilibili`。

## 3. 本地视觉理解与自动语音识别

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[understanding]"
.\.venv\Scripts\python.exe -m viralforecast.models --download --directory models
.\.venv\Scripts\viralforecast.exe analyze --video your-video.mp4 --title "你的标题" --understand --asr --models-dir models --language zh --out outputs/understood
```

显式下载完成后，推理在本机运行。包含对象检测、短片段动作识别、场景语义与文案匹配、可见表情线索和 Whisper 转写。省略 `--language` 可自动判断语言。模型可能不确定或识别错误；表情线索不等于人物真实情绪。CLIP 的中文文案匹配效果有限，需人工复核。

## 4. 导入同类内容：看近期流量与改进方向

使用你有权访问的平台导出 CSV，按下面的字段映射。每行是一条内容在某一时刻的累计流量快照，同一内容可出现多行。

必填字段：`content_id,account_id,platform,published_at,observed_at,title,caption,views`。

可选字段：`duration_seconds,cut_rate,likes,comments,shares,saves,data_source`。真实数据填 `data_source=real`；模拟数据必须填 `synthetic`。时间使用 ISO 8601，建议明确时区。`views` 是快照时的累计播放量，不要填单次增量。

```powershell
.\.venv\Scripts\python.exe examples/generate_trends.py --out examples/data/synthetic_trends.csv
.\.venv\Scripts\viralforecast.exe trends --csv examples/data/synthetic_trends.csv --analysis outputs/my-video/analysis.json --as-of 2026-10-19T00:00:00Z --days 7 --out outputs/trends
```

换成真实数据后，把 `--as-of` 改为实际观察截止时间。也可以把趋势直接加进视频报告：

```powershell
.\.venv\Scripts\viralforecast.exe analyze --video your-video.mp4 --title "视频开场技巧" --platform douyin --trends-csv your-export.csv --as-of 2026-10-19T00:00:00Z --trend-days 7 --exclude-account your-account --out outputs/with-trends
```

报告会展示：相似内容、近期播放增量/每小时增速、样本相对热度、同一批内容的前后窗口走势、按内容年龄分组的累计播放量，以及值得进行单变量测试的时长、镜头节奏、标题和开场调整。中文相似度使用字符 n-gram，英文使用词项 TF-IDF；不是跨视频的语义检索。

**重要边界**：每个窗口至少两次相隔一小时的快照才能测量增速；只有一次快照就只显示累计播放量。至少 5 条相似内容与 10 条平台内基准样本支持相对热度，至少 5 条双窗口配对样本支持走势。高增速内容的特征建议需至少 12 条可测量相似样本。样本不足返回原因，不捏造热度。

这不是平台内部推荐曝光量，也不代表平台整体流量。平台导出不提供内部推流数据时，报告中的该项保持为空。建议反映样本关联，不能保证“改了就涨流量”。没有真实 CSV 时，示例只用于验证软件。

## 5. 有账号历史：统计预测与回测

```powershell
.\.venv\Scripts\viralforecast.exe predict --analysis outputs/my-video/analysis.json --history examples/data/synthetic_history.csv --account demo --platform tiktok --as-of 2026-10-19T00:00:00Z --out outputs/prediction
.\.venv\Scripts\viralforecast.exe backtest --history examples/data/synthetic_history.csv --account demo --platform tiktok --step 5 --out outputs/backtest
```

预测历史 CSV 与趋势快照 CSV 是两种格式。历史格式要求固定 24h/7d 指标，详见 `docs/data.md`。至少 120 条同账号、同平台且七天指标已成熟的记录；不足时自动降级。趋势上下文不会直接修改统计预测，避免未经回测的“热度加成”。

`compare` 对照发布后成熟实际表现；`report` 可重新生成 JSON、Markdown 和 HTML。使用任一子命令加 `--help` 查看参数。

## 6. 验证、隐私与校验和

```powershell
.\.venv\Scripts\python.exe -m pytest -q
Get-FileHash viralforecast-skill-0.2.0.zip -Algorithm SHA256
```

对照 Release 中的 `.sha256` 文件核验 ZIP。未安装大模型权重时，重量级模型测试会明确跳过；本地真实模型执行记录见 `docs/UNDERSTANDING_TEST_REPORT.md`。分析不上传你的内容，导出的报告仍可能包含标题、文案、转写和账号指标，请自行保护。源码采用 MIT，第三方依赖与模型保留各自许可。
