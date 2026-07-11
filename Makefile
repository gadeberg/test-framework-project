.PHONY: install dev test check release-mode

install:
	uv sync
	uv run playwright install chromium

# Co-development: layer a live, local, uncommitted editable install of the
# framework on top of the pinned tag. Requires ../test-framework checked out
# side by side. Never commit a path source - see pyproject.toml.
dev:
	uv sync
	uv pip install -e ../test-framework

# --no-sync is required in dev mode: a plain `uv run` re-syncs against the
# lockfile and would drop the editable framework shadow mid-session.
test:
	uv run --no-sync pytest

check:
	uv run ruff format --check .
	uv run ruff check .
	uv run pyright
	uv run pytest

# Revert to the pinned GitHub-tag framework (undoes `make dev`).
release-mode:
	uv sync
