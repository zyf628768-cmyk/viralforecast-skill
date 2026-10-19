# Data contract / 数据约定

CSV is UTF-8 (BOM accepted), comma-delimited, with one row per published post. Required columns:

| Column | Definition |
|---|---|
| content_id | Nonempty, unique per selected account/platform |
| account_id, platform | Exact account and CLI platform identifier |
| published_at | ISO 8601 publication timestamp; naive timestamps are treated as UTC |
| duration_seconds | Video duration, positive |
| cut_rate | Scene cuts per second using the same scene filter/threshold as inference |
| title_length | Python character count of title |
| text_length | Character count of `(title + ' ' + caption).strip()` |
| question_count | ASCII and full-width question marks in title + caption |
| hashtag_count | `#[^\s#]+` token count |
| views_24h, views_7d | Nonnegative cumulative views measured at exactly 24h / 7d; 7d >= 24h |
| likes_7d, comments_7d, shares_7d, saves_7d | Cumulative seven-day interactions; normalized to <= views |
| data_source (optional) | `real` or `synthetic`; omitted declarations are reported unverified |

All feature/metric numbers must be finite. Extra columns are ignored by the feature allowlist; outcomes and identifiers never enter regression. Invalid numeric/date/duplicate records in the selected account/platform fail validation. Rows for other accounts/platforms are skipped, never pooled. Metrics that legitimately exceed views must be normalized before import; this release uses bounded rate definitions.

Only posts with `published_at + 7 days < prediction timestamp` are eligible. This intentionally excludes exactly-boundary labels and uses a conservative seven-day window for both horizons. The exporter must ensure outcomes were actually available by then: corrected metrics, deleted posts, retrospective edits, inconsistent exposure windows, missing posts and re-upload duplicates cannot be detected from CSV alone. Never substitute a lifetime view count for a seven-day label.

Historical features must describe the content **before publication**. Do not export post-publication title revisions, comments, recommendation impressions or audience retention as features. The software can enforce column boundaries but cannot verify the provenance of a user-declared feature.

Each event horizon uses its own median: 3×/5× the mature historical 24h median for 24h views; the mature seven-day median for seven-day views. This is not a platform-wide viral definition.

`schemas/input.schema.json` describes analysis flags; the CLI uses flags rather than loading a request JSON. `output.schema.json` describes report envelopes; transcript and mature actual JSON have separate schemas. Runtime semantic checks also enforce date ordering, duration bounds and horizon monotonicity. Example actual data is explicitly synthetic.
