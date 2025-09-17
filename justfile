uv_flags := "--frozen --isolated --all-groups"

[private]
default:
  just --list

lock:
  uv lock --upgrade --no-cache

lint:
  uv run {{uv_flags}} ruff check src tests examples

fmt:
  uv run {{uv_flags}} ruff format src tests examples
