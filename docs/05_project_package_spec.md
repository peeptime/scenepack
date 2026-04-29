# Project Package Spec / 项目包规范

Version: v0.1

## Core Idea

ScenePack saves a project scene, not only image files.

The project package should begin as a lightweight record and become richer only after title acceptance.

## Default Package

Before title acceptance, a package may contain:

```text
scenepack-project/
  scene_records/
    2026-04-29T103000.layout.json
    2026-04-29T103000.message.md
  assets/
    references or copied images
  project_state.json
```

## Required Before Acceptance

- `project_state.json`
- timestamped layout snapshots
- layout messages
- image references or copied images, based on user setting

## Optional Before Acceptance

- title candidate list
- thumbnail cache
- structure visualization cache

## Generated After Acceptance

After title or intent acceptance, ScenePack may generate:

```text
project.json
relations.json
summary.md
naming_plan.json
agent_context.md
materials_manifest.csv
task_brief.md
exports/
```

## File Roles

`project_state.json`

Stores project state, title status, mode state, capture history, privacy state, and generation readiness.

`layout.json`

Stores geometry facts, structure pool hits, graph summaries, and inference gates for one snapshot.

`message.md`

Stores a short human-readable structural message.

`relations.json`

Generated after acceptance. Stores stable relations and reasoning candidates.

`summary.md`

Generated after acceptance. Stores project-level summary.

`naming_plan.json`

Generated only when project type and title are clear enough.

## Naming Logic

Image naming should not use one fixed rule.

It should depend on accepted project type:

- project management: task or evidence oriented names
- image material: visual material names
- AI coding: prompt, UI, result, error, context names
- product research: competitor, page, feature, evidence names
- mixed scene: neutral timestamped names until clarified

## Mixed Scene Rule

If a scene contains highly mixed material and no accepted title:

- do not force project type
- do not apply strong naming rules
- keep neutral names
- mark the scene as mixed
- wait for title acceptance or AI mode

