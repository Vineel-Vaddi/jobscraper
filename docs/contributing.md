# Contributing to JobTailor

## Branch Naming Convention

We follow a simple pattern mapping branch concepts to issues:
`[type]/[issue-number]-[short-description]`

Valid `[type]` elements:
- `feat/`: For new features
- `fix/`: For resolving bugs
- `chore/`: For maintenance, dependency updates, and boilerplate

Example:
`feat/12-add-resume-vectorization`

## Pull Request Convention

- Reference the Issue ID within the PR body to auto-link. (e.g., `Resolves #15`).
- Ensure all CI tests pass.
- Prefix PR titles cleanly: `[Feat] Add vectorization`, `[Fix] Resolve PDF parsing timeout`.

## Commit Style

We encourage utilizing standard Conventional Commits inside branch merges, though we do not mechanically block non-conforming commits in the git-hooks yet to maintain speed.
- `feat: added semantic extraction`
- `fix: resolved auth token expiry bounds`
- `chore: updated NextJS template`
