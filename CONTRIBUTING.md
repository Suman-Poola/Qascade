# Contributing to Qascade

Thank you for your interest in Qascade. Bug reports, feature requests, documentation fixes and
code contributions are all welcome. By taking part you agree to follow the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Reporting bugs, requesting features, asking for help

Use [GitHub Issues](https://github.com/Suman-Poola/Qascade/issues) for all three.

- **Bug:** use the bug report template. Include the Qascade, Qiskit, scikit-learn and Python
  versions, your OS, the backend or estimator you used, and a minimal reproducer.
- **Feature:** use the feature request template and describe the problem you want to solve.
- **Support:** open an issue and describe what you tried and what you expected.
- **Security problems:** do not open a public issue; see [SECURITY.md](SECURITY.md).

## Development setup

Requires Python 3.11 or newer (3.11 is the oldest supported version).

```bash
git clone https://github.com/Suman-Poola/Qascade.git
cd Qascade
python -m venv .venv            # or: uv venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

The `dev` extra installs the test and docs dependencies and the lint, type-check and build tools.

## Common tasks

```bash
pytest                          # full test suite
pytest -m "not slow"            # skip slow tests
pytest -m aer                   # only tests that need qiskit-aer
pytest -m ibm                   # only tests that use IBM Runtime fake backends (no network)
pytest -n auto --cov=qascade --cov-branch --cov-report=term   # parallel, with coverage

ruff check .                    # lint
ruff format .                   # format (use `ruff format --check .` to only check)
mypy                            # type-check (configured in pyproject.toml)

mkdocs serve                    # build the docs and serve them locally
mkdocs build --strict           # what CI runs; warnings are errors
```

`pre-commit run --all-files` runs the lint, format and type checks together.

## Coding standards

- **Docstrings:** NumPy style, on every public module, class, function and method.
- **Type hints:** full annotations on all code under `src/`; `mypy` runs in strict mode.
- **Tests:** every change comes with tests. Fixes should include a test that fails without the fix.
- **Coverage:** total coverage must stay at or above 90% (enforced by `fail_under` in
  `pyproject.toml`).
- **Style:** `ruff` (line length 100) decides formatting and import order; do not fight it.
- **Markers:** mark slow tests `@pytest.mark.slow`, tests needing Aer `@pytest.mark.aer`, and
  tests needing IBM Runtime `@pytest.mark.ibm`. Optional dependencies must be imported lazily in
  library code.
- **Design decisions:** significant choices are recorded in [DECISIONS.md](DECISIONS.md).

## Pull request process

1. Open an issue first for anything non-trivial, so the approach can be agreed before you write code.
2. Fork the repository and create a branch from `main`.
3. Make your change with tests and docs, and add an entry under `[Unreleased]` in `CHANGELOG.md`
   for user-visible changes.
4. Make sure `pytest`, `ruff check .`, `ruff format --check .` and `mypy` pass locally.
5. Open a pull request against `main` and fill in the template. CI must pass before merge.
6. Respond to review comments; the maintainer will merge when everything is resolved.

## Release process (maintainer)

1. Update `__version__` in `src/qascade/_version.py`.
2. In `CHANGELOG.md`, rename `[Unreleased]` to the new version and date, and start a fresh
   `[Unreleased]` section.
3. Commit, push to `main`, and wait for CI to pass.
4. Tag the commit `vX.Y.Z` (the tag without the `v` must equal the version in `_version.py`) and
   push the tag.
5. The tag triggers the release workflow: it builds the package, publishes to TestPyPI, checks the
   install, then publishes to PyPI after the maintainer approves the `pypi` environment. It then
   creates the GitHub release for the tag.
