# Repository Guidelines

This repository contains the Graphiti CLI, a Python 3.10+ Click-based tool that exposes Graphiti knowledge-graph operations from the terminal.

## Project Structure & Module Organization
- `cli/`: CLI entry point and commands (`graphiti_cli.py`, `commands/`, `query/`, `utils/`).
- `tests/`: Unit tests for utilities and validators; pytest is configured via `pytest.ini`.
- `docs/`, `examples/`: Reference material and sample usage.
- Script entrypoint: `graphiti` (declared in `pyproject.toml`).

## Build, Test, and Development Commands
- Install (editable): `pip install -e .` and optionally `pip install -e ".[ai]"`.
- Run CLI: `graphiti --help`.
- Quick checks: `pytest -q` (unit tests in `tests/`).
- Local examples: `./test_cli.sh` or try `graphiti search "authentication"`.

## Coding Style & Naming Conventions
- Python style: 4-space indentation, type hints encouraged, docstrings for public functions.
- Naming: `snake_case` for functions/variables, `PascalCase` for classes, CLI flags in `--kebab-case`.
- Formatting/Linting: no enforced tool in repo; prefer `black` and `ruff` locally before PRs.

## Testing Guidelines
- Framework: `pytest` (see `pytest.ini`). Unit tests match `tests/test_*.py`.
- Markers: use `@pytest.mark.integration` for tests that hit live services; default CI runs unit tests only.
- Add focused tests for new utilities and command behaviors; keep output deterministic.

## Commit & Pull Request Guidelines
- Commit style: Conventional Commits (e.g., `feat(cli): ...`, `fix: ...`, `chore(docs): ...`).
- PRs: clear description, linked issues, reproduction steps, and before/after snippets for CLI output. Include env notes if integration-tested.

## Security & Configuration Tips
- Required env: `NEO4J_PASSWORD`. Optional: `NEO4J_URI` (default `bolt://localhost:7687`), `NEO4J_USER` (default `neo4j`), `OPENAI_API_KEY` for NL queries.
- Use a local `.env` (git-ignored); never commit secrets.

## Agent-Specific Instructions
- ByteRover MCP: call `byterover-retrieve-knowledge` before tasks and `byterover-store-knowledge` after successful tasks.
- Read `CLAUDE-GUIDE.md` and `CLAUDE.md` for Graphiti’s custom entities/edges and search strategies.

Examples (see GUIDE.md for more)
```bash
pip install -e . && graphiti maintenance stats --detailed
pytest -q
graphiti search "updates" --created-after 2024-01-01 --method hybrid
```

## Integration Test Instructions (Codex)
- Use the installed `graphiti` command (not `python -m ...`). Ensure `pip install -e .` succeeded and `command -v graphiti` works.
- Setup: `set -a; source .env; set +a; export GRAPHITI_TELEMETRY_ENABLED=false` and confirm Neo4j/Graphiti backend is running and reachable.
- Stats smoke: `graphiti maintenance stats -o json` (exit 0; JSON output). Add `--detailed` if desired.
- Add episode: `graphiti episodes add "AGENTS-IT-$(date +%s)" "integration smoke" --source text --group-id agents_it` → record returned UUID.
- Get episodes: `graphiti episodes get --group-id agents_it --last-n 5 -o jsonc` and verify the name/content appears.
- Basic search: `graphiti search "integration" -g agents_it --full-output -o json` (expect hits; otherwise investigate indexing/connectivity).
- Centered search: pick a UUID from results → `graphiti search "integration" --center-node <node-uuid> --ids-only`.
- Export: `graphiti maintenance export -g agents_it -o /tmp/graphiti_export.json && test -s /tmp/graphiti_export.json`.
- Optional (LLM configured only): `graphiti search "integration" --reranker cross_encoder -o pretty` and `graphiti maintenance build-communities -g agents_it`.

Notes (temporal + query)
- The `query` command requires optional extras: `pip install -e ".[ai]"` (installs `claude-code-sdk`). If not installed, skip `graphiti query ...` entirely. Even `--dry-run` imports this package.
- Accepted time formats: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, YYYY-MM-DD HH:MM:SS, YYYY-MM-DDTHH:MM:SSZ. Times are treated as UTC. See GUIDE.md for details.
