# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`test-framework-project` is **Repo 2** of a two-repo test-automation setup — the getting-started
example test project. It consumes
[`test-framework`](https://github.com/gadeberg/test-framework) (**Repo 1**, sibling checkout at
`../test-framework`) from GitHub by tag. This repo contains only `.feature` files, plain-Python
tests, project-specific page objects, and a bundled offline FastAPI mock — no framework
internals live here.

## Commands

```bash
make install            # uv sync + uv run playwright install chromium (browser binary, separate download)
uv run pytest            # everything, plain-Python + Gherkin together
uv run pytest -n auto    # parallel (pytest-xdist)
uv run pytest -m api     # marker-filtered
uv run pyright           # relaxed profile (tests/, support/)
make check               # ruff format --check + ruff check + pyright + pytest

make dev                 # uv sync (pinned tag) + uv pip install -e ../test-framework (editable, uncommitted)
make test                # uv run --no-sync pytest - --no-sync is required in dev mode, or a plain
                          # `uv run` re-syncs against the lockfile and drops the editable shadow
make release-mode        # uv sync - reverts to the pinned tag, no repo changes either way

uv run scripts/bump-framework.py v0.2.0   # edits the pinned tag, runs `uv lock`, shows the diff
```

## Architecture

**The committed `pyproject.toml` always pins `test-framework` by GitHub tag** —
`[tool.uv.sources]` uses `git = "...", tag = "vX.Y.Z"`, never a local `path =` source (that
breaks every other checkout and CI). The *only* sanctioned way to get a live framework edit is
`make dev`'s post-sync editable install, which is a venv-local, uncommitted layer that `make
release-mode` (`uv sync`) reverts. Never commit a path dependency here, even temporarily.

**`conftest.py` at the repo root starts the bundled FastAPI mock once per session** (in a
background thread via `uvicorn.Server`, on a free port, polled via `/health` until ready) and
overrides `base_url` to point at it — unless the `BASE_URL` environment variable is set, in
which case the suite targets that deployment and the mock is never started (configuration is
plain env vars; nothing loads a `.env` file). It also supplies
`page_registry`, mapping semantic page names (`"login"`, `"checkout"`) to the page-object
classes in `support/pages/` — this is what lets `steps/web.py`'s shared
`I am on the "{page_name}" page` step work without the framework needing to know this project's
pages in advance.

**`support/mockapp/app.py` serves both the JSON API and rendered HTML** — `/login` (API),
`/login-page` and `/checkout-page` (HTML with inline JS that calls back into `/login` /
`/checkout` via `fetch`). This is why the web examples exercise real async behavior: the checkout
page's confirmation text only appears after the JS fetch resolves, which is exactly what
`test-framework`'s `expect(...)`-based wait in `steps/web.py` is built to handle. If you add a
new mock page with async-populated content, don't read its text with a plain `.inner_text()`
immediately after a click — use `playwright.sync_api.expect(...)` first (see
`tests/web/test_checkout.py` for the pattern).

**`tests/`, `tests/api/`, `tests/web/` each have an `__init__.py`.** This is required, not
incidental: `tests/api/test_example.py` and `tests/web/test_example.py` share a basename, and
pytest's default import mode needs the packages to disambiguate them. If you add another
same-named file pair across `tests/api/` and `tests/web/`, this is why it still works.

**Both authoring styles carry the same requirement label, not the same step shape.** The
`REQ-1024` example exists as `features/api/login.feature` (`@REQ-1024`) and
`tests/api/test_login.py` (`@requirement("REQ-1024")`) — same label in the generated report,
deliberately different step granularity (Gherkin's Given/When/Then vs. Python's `step()`
groupings). Don't try to force one style to mimic the other's step tree.

**Adding a scenario/test that fits the existing step vocabulary needs no new step code** — just
`.feature` lines, or copy `tests/api/test_example.py` / `tests/web/test_example.py`. New step
*phrasing* belongs in `test-framework` (Repo 1), not here, since the vocabulary is meant to be
shared across every test project that depends on the framework.
