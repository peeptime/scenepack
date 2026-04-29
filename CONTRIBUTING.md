# Contributing

Thanks for taking this repository seriously.

`ScenePack` is still early, so the main goal of contribution is not feature volume. It is improving the trustworthiness of the scene-to-context workflow.

## Current Priorities

High-value contribution areas:

- Windows capture reliability
- stable scene detection
- title acceptance UX
- handoff package quality
- documentation clarity
- packaging discipline
- tests around real workflow regressions

Lower priority right now:

- broad speculative AI integrations
- large frontend redesigns without workflow evidence
- premature multi-platform abstraction

## Ground Rules

- Keep user-facing claims modest and testable.
- Do not present the project as an official Snipaste extension.
- Prefer changes that reduce repeated explanation work for users.
- Avoid adding noisy AI output that does not improve handoff quality.
- Preserve compatibility paths unless a rename or break is intentional and documented.

## Setup

```powershell
py -m pip install -e .
$env:PYTHONPATH="src"
py -m unittest discover -s tests
```

Optional GUI setup:

```powershell
py -m pip install -e .[gui]
```

## Before Opening A Change

- Read [README.md](README.md) for public positioning.
- Read [docs/00_product_definition.md](docs/00_product_definition.md) for product scope.
- Read [docs/11_versioning_and_release_policy.md](docs/11_versioning_and_release_policy.md) for release expectations.

## Change Expectations

When contributing:

- keep edits scoped and intentional
- update docs when behavior or positioning changes
- add or update tests when logic changes
- call out known risks plainly
- avoid renaming compatibility paths casually

## Validation

Use the smallest relevant validation set, and report what you actually ran.

Common checks:

```powershell
$env:PYTHONPATH="src"
py -m unittest discover -s tests
py -m compileall -q src tests
```

If you changed packaging or GUI behavior, say so explicitly and note what you did or did not validate locally.
