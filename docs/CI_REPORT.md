# GitHub publication validation — 2026-10-19

Version 0.2 follow-up: [run 39224579401](https://github.com/zyf628768-cmyk/viralforecast-skill/actions/runs/39224579401) passed all four Windows/Ubuntu × Python 3.10/3.12 jobs for commit `54908a728d716f4e556eb426ec2a2a16f1aaeea1`. CI uses the lightweight dependencies and explicitly skips the large-model integration test. Actual downloaded-model execution is documented separately in [UNDERSTANDING_TEST_REPORT.md](UNDERSTANDING_TEST_REPORT.md).

The owner authorized public publication after the initial local delivery. Source, Skill, docs, tests, schemas and explicitly simulated examples are published at [zyf628768-cmyk/viralforecast-skill](https://github.com/zyf628768-cmyk/viralforecast-skill).

The initial [CI run](https://github.com/zyf628768-cmyk/viralforecast-skill/actions/runs/39222158106) passed on both Windows versions but failed on Ubuntu before tests started: the external FFmpeg setup action reported `TypeError: fetch failed`. The workflow was fixed to install FFmpeg using Ubuntu's distribution package, while retaining the working Windows setup.

The corrected [CI run](https://github.com/zyf628768-cmyk/viralforecast-skill/actions/runs/39222473352) tested commit `cf4c95187f9d63e7646a30b2a8fdc861cc446df8`:

| Runner | Python | Actual pytest result |
|---|---|---|
| Ubuntu | 3.10 | 42 passed in 3.82s |
| Ubuntu | 3.12 | 42 passed in 2.40s |
| Windows | 3.12 | 42 passed in 4.69s |
| Windows | 3.10 | 42 passed in 3.96s |

JUnit artifacts are attached to the run. These are software compatibility/integration tests with simulated data; no real-account or commercial accuracy claim is established.

Raw local machine logs and paths were excluded from the public source snapshot. Full original local records remain in the user's local delivery ZIP. `docs/TEST_REPORT.md` is the historical local validation report; this document records the later remote execution and supersedes its earlier statement that GitHub CI had not yet run.
