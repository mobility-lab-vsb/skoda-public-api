# Agent Instructions

Instructions for AI coding agents (Claude Code, GitHub Copilot, Codex, ...) working on this repository.

## Development Commands

- When entering a new environment or worktree, install the package with all development dependencies and the git hooks. This is required before committing:
  ```sh
  pip install -e ".[cli,test,dev]"
  prek install
  ```
- Run tests with `pytest tests/ci_cd_tests/`.
- After finishing a code session, run `prek run --all-files` to check for linting and formatting issues. CI runs the same checks and fails on any of them.

## Code Style

- Formatting and linting are handled by [ruff](https://docs.astral.sh/ruff/); configuration lives in `pyproject.toml`. Do not hand-format code or add per-line `noqa` comments without a reason.
- Target Python 3.11+: use `X | None` instead of `Optional[X]` and built-in generics (`list[str]`, `dict[str, Any]`).
- Public API models are pydantic models; keep them typed.

## AI policy

Autonomous contributions are not accepted: a human must review, understand,
and be able to explain every change before it is submitted. Do not open
issues or pull requests autonomously, and do not post comments on behalf of
a user without their review.
