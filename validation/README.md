# Validation records

The local source suite passed 42 tests; the extracted release suite passed 42 tests. See docs/TEST_REPORT.md for actual results and commands, and GitHub Actions for independently executed CI.

Raw local logs, JUnit XML and environment records are intentionally excluded from this public repository because they contain machine-specific paths and metadata. Full local records remain in the user's delivered source archive. Generate your own records with `python -m pytest -q --junitxml=validation/pytest.xml` and the scripts documented in README.md.

Synthetic data validates software behavior only; it does not establish real-account prediction accuracy.
