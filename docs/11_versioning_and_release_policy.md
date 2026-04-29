# Versioning And Release Policy

Version: v0.1

## Purpose

This document defines how the public `ScenePack` repository should communicate versions and release maturity.

The goal is simple:

> make the repository feel consistent and honest before it becomes large.

## Current Public Baseline

Current public version:

- `0.3.0`

Current maturity:

- prototype
- source-first
- Windows-first

Current public constraints:

- package import path remains `peepaste`
- CLI remains `peepaste`
- public product name is `ScenePack`

## Versioning Rule

Use semantic versioning as a communication tool, even if the project is still early.

Interpretation for this repository:

- `MAJOR`: breaking workflow or compatibility changes
- `MINOR`: meaningful feature additions or workflow improvements
- `PATCH`: focused fixes, docs fixes, packaging fixes, or low-risk refinements

Example:

- `0.3.0` -> current public bootstrap snapshot
- `0.3.1` -> docs, packaging, or minor behavior fixes
- `0.4.0` -> new capability or clear workflow improvement
- `1.0.0` -> only when installation, workflow, compatibility, and public expectations are significantly more stable

## Release Labels

Use one of these release labels in README, tags, or release notes when helpful:

- `Prototype`
- `Internal Test`
- `Public Preview`
- `Beta`
- `Stable`

Current recommended label:

- `Prototype / Public repo bootstrap`

## What Must Change With A Release

For any intentional public release, update at least:

- `src/peepaste/__init__.py`
- `pyproject.toml`
- `CHANGELOG.md`
- `README.md` if release status or compatibility changed materially

## Public Naming Rule

Public-facing materials should use `ScenePack`.

Compatibility paths may still use:

- `peepaste`
- `src/peepaste`
- `py -m peepaste`

Do not hide this mismatch. Document it plainly until a deliberate engineering rename happens.

## Release Checklist

Before cutting a public release:

- confirm version number is updated in code and metadata
- update `CHANGELOG.md`
- review README for outdated claims
- rerun the most relevant tests
- confirm packaging notes still match reality
- document known limitations instead of burying them

## Tagging Guidance

When tags begin to matter, prefer:

- `v0.3.0`
- `v0.3.1`
- `v0.4.0`

Use GitHub Releases only when the release artifacts and notes are worth external consumption.

## Engineer Attitude

Release notes should be specific, measured, and evidence-based.

Avoid:

- inflated roadmap claims
- vague AI capability language
- implying support that is not tested

Prefer:

- exact version numbers
- exact tested environments
- exact workflow improvements
- exact known limitations
