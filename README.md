# test-framework-project

Getting-started example test project consuming
[`test-framework`](https://github.com/gadeberg/test-framework) — a
spec-traceable pytest/pytest-bdd/pytest-playwright/httpx framework. This
repo contains only `.feature` files, plain-Python tests, project-specific
page objects, and a bundled offline mock — no framework internals.

Open source under the [0BSD license](LICENSE) — take it, copy it, modify
it, use it as the basis for your own test project, with no attribution or
other obligation required.

## Quickstart

```bash
git clone git@github.com:gadeberg/test-framework-project.git
cd test-framework-project
make install        # uv sync + uv run playwright install chromium (browser binary)
uv run pytest        # plain-Python and Gherkin tests together, green, offline
```

Then open `reports/report.html` — both authoring styles show up side by
side, with the `REQ-1024` requirement label attached to both, no JVM
involved.

`make install` runs two separate steps because `uv sync` does **not**
install Playwright's browser binaries — that's `playwright install
chromium` (only Chromium is used; installing all engines would triple the
download), a ~150MB fetch from Microsoft's CDN. In an air-gapped/qualified
environment, mirror or pre-provision a browser cache and point
`PLAYWRIGHT_BROWSERS_PATH` at it.

Configuration is plain environment variables — there is no `.env` loading:

- `BASE_URL` — set it (e.g. `BASE_URL=https://staging.example.com uv run
  pytest`) to point the suite at a real deployment; the bundled offline
  FastAPI mock (`conftest.py`) is then never started. Unset, the quickstart
  runs fully offline against the mock.
- `TEST_FRAMEWORK_REPORT_BACKEND` — `pyhtml` (default, no JVM) or `allure`
  (optional extra).

## Layout

```
features/api/login.feature     # Gherkin, @REQ-1024
features/web/checkout.feature
tests/api/test_login.py        # Python, @requirement("REQ-1024") - same label, same checks
tests/api/test_example.py      # copy-paste template for a new API test
tests/web/test_checkout.py
tests/web/test_example.py      # copy-paste template for a new UI test
support/mockapp/app.py         # FastAPI: /login JSON API + rendered login/checkout HTML
support/pages/                 # page objects: all UI selectors live here, never in tests/steps
conftest.py                    # starts the mock app once per session; registers page_registry
```

## Adding a test

- **New API or web scenario using existing phrasing**: add `.feature` lines only — no new step code. The shared vocabulary lives in `test-framework`'s `steps/api.py` / `steps/web.py`.
- **New Python test**: copy `tests/api/test_example.py` or `tests/web/test_example.py`, rename, edit the body. Pattern: arrange (fixtures) -> `with step(...):` actions -> `verify.*` checks.
- **New page**: add a class to `support/pages/` (a `path` + a `locators` field-name -> CSS-selector map), register it in `conftest.py`'s `page_registry` fixture.
- Tag every test/scenario with a requirement id: `@REQ-1234` in Gherkin, `@requirement("REQ-1234")` in Python. Both resolve to the same report label.

## Running

```bash
uv run pytest              # everything
uv run pytest -n auto      # in parallel (pytest-xdist)
uv run pytest -m api       # just the API-marked tests
uv run pyright             # relaxed type-check (tests/, support/)
```

`make check` runs the same gate as CI would: `ruff format --check` + `ruff check` + `pyright` + `pytest`.

## The two-repo operating model

This project consumes `test-framework` from GitHub **by tag** — the
committed path, never a local `path =` source (that breaks every other
checkout and CI). See `pyproject.toml`'s `[tool.uv.sources]`.

**Day to day (pinned)**: `make install` then `uv run pytest`. You're on
whatever tag `pyproject.toml` names.

**Co-developing the framework alongside a test** (check `test-framework` out
as a sibling directory first — `../test-framework` relative to this repo):

```bash
make dev              # uv sync (pinned tag), then uv pip install -e ../test-framework
make test             # uv run --no-sync pytest - --no-sync is required, or a plain
                       # `uv run` re-syncs against the lockfile and drops the
                       # editable shadow mid-session
# ... edit ../test-framework, re-run `make test`, changes are picked up instantly ...
make release-mode      # uv sync - reverts to the pinned tag, no repo changes either way
```

Nothing in this repo's committed files changes during `make dev` — the
editable install is a venv-local, uncommitted layer. The rule that matters:
**the committed `pyproject.toml` always pins the GitHub tag.**

## Bumping the framework version

```bash
uv run scripts/bump-framework.py v0.2.0
```

Edits the pinned tag in `pyproject.toml`, runs `uv lock`, and shows the diff
to review before committing. Check `test-framework`'s `CHANGELOG.md` for
what changed and whether it's breaking (semver: step-phrasing or
helper-signature breaks are major).

## Bootstrapping a second test project

Clone or copy this repo, delete the example tests, keep the
templates/mock/Makefile/page-object base. Plain `git`, no host-specific
template-repo feature — this is deliberate, since hosting may move on-prem
later.
