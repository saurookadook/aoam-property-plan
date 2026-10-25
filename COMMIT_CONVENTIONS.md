# Commit conventions

Derived from this repo's existing history. Follow it for every commit on a feature branch.

## Subject line

```
<type>(<scope>): <subject>
```

- `type` is required and lowercase. Pick one from the table below.
- `scope` is optional. Use it when the change is confined to one top-level area: `frontend`, `backend`, `postgres`, `nginx`, `scripts`, `doc`. Omit it when the change spans areas.
- `subject` is lowercase, imperative ("add", "fix", "replace", not "added" or "adds"), and has no trailing period.
- Keep the whole line under about 72 characters.

| Type    | Use for                                                                          |
| ------- | -------------------------------------------------------------------------------- |
| `feat`  | New behavior, new pages or components, and refactors that support a feature.     |
| `bug`   | A fix for broken behavior. Use `bug`, not `fix`.                                 |
| `chore` | Tooling, config, formatting, dependency changes, renames, and repo housekeeping. |
| `infra` | Docker images, deployment, database setup, and admin scripts.                    |
| `docs`  | Documentation and planning docs only.                                            |

Examples from history:

```
feat(frontend): replace eslint with oxlint
chore(frontend): remove generated stories from Storybook init
bug: fix issue with MarketsList sort controls
infra: minor changes to PostgreSQL image, update admin scripts
docs: record Chunk 6 status in the Phase 4 plan
```

## Body

- Optional for small, self-explanatory changes.
- When present, separate it from the subject with a blank line.
- Explain why the change was needed and what the reader could not tell from the diff. Do not restate the diff.
- Write plain prose paragraphs wrapped at about 80 columns. Use US spelling.

## Trailers

- Add a `Co-Authored-By:` trailer for each AI assistant that wrote part of the change, for example `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Put trailers last, after a blank line.

## Atomic commits

- Each commit holds one concern and leaves the tree in a working state.
- A refactor and the feature built on it are two commits.
- Formatting-only changes go in their own `chore` commit, separate from behavior changes.

## Pull request merges

PRs are squash-merged into `main`. The squash commit uses an uppercase bracketed type, a title, and the PR number:

```
[FEAT] Phase 4 Dashboard - Chunk 6 (#44)
[INFRA] frontend deploy setup
```

The squash body keeps the branch's individual commit messages as a bulleted list.
