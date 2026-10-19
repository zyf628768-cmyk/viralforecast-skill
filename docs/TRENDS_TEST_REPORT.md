# CSV trend and release validation — 2026-10-19

The user selected platform-exported CSV input rather than live API collection. No real account/peer export was provided. Implemented support covers all seven platform IDs through a common snapshot contract and strictly filters one platform per analysis.

Actual local full suite with downloaded vision/ASR weights enabled: **59 passed in 34.09s**. This includes real local model execution, existing statistical/CLI tests, eight new trend tests and two public packaging boundary tests. The earlier lightweight run before packaging tests passed 56 tests with one heavyweight-model skip. Raw local JUnit/log records remain local and are excluded from the public ZIP.

Trend tests verify English/Chinese lexical similarity, strict observation cutoff, future-snapshot mutation invariance, account/platform isolation, duplicate/empty CSV errors, one-snapshot abstention, decreasing cumulative-counter abstention, paired-window velocity, evidence-backed feature suggestions, Schema validation, standalone trends/re-render CLI and attachment to video reports.

The real CLI was run against a generated synthetic CSV containing 40 content items and 200 snapshots. It selected 24 lexically similar items, all with valid two-window velocities. The synthetic output's peer median velocity was 250 views/hour versus a 90 views/hour sample median (ratio approximately 2.78), and the paired-window ratio was 2.0. These numbers are generated software-test data, not current platform traffic or evidence of commercial forecasting accuracy. Internal recommendation exposure is explicitly null.

`examples/reports/trends.json`, `.md` and `.html` contain the same actual synthetic run. HTML/Markdown include a readable overview and test suggestions alongside the canonical data. Sample support, timestamps, matching threshold, account exclusion and provenance are retained.

Public archive tests verify exclusion of raw private validation records/model binaries and rejection of any included CSV example declared real. The public source packager checks required code/docs, emits an internal per-file SHA256 manifest and a sidecar checksum, and verifies ZIP CRC. Large weights, virtual environments and private output folders are not public assets.

Limitations: similarity is lexical; heat is relative to imported samples and is not adjusted for creator size/promotion/content age. Cumulative view summaries are separately grouped by age. Improvement suggestions are observational single-variable experiments, not guaranteed or causal traffic uplifts. Trends are never added as an unvalidated multiplier to statistical forecasts.
