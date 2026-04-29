# UX Handoff And Skill++ Decision

## Product UX Focus

ScenePack should not feel like a text log viewer. The user's main job is to confirm whether a captured visual scene matches their intent, then hand clean context to a downstream agent such as OpenClaw.

The GUI must therefore make these things visible immediately:

- What was captured: item count, group count, semantic risk, image-reading need.
- What needs confirmation: candidate title, accepted title, and key references.
- What can be handed off: OpenClaw prompt, review sheet, clipboard bundle, agent context, and manifest.
- What is uncertain: structural hints are evidence, not semantic truth.

## Current GUI Direction

The desktop UI should stay as a compact workbench:

- Scene Monitor: capture, inspect structure, preview layout, confirm title, generate files.
- Scene Records: reopen prior packages, inspect summaries, drag generated files out.
- Preferences: switch interface and content language between Chinese and English.
- Skills & AI: configure AI mode, naming patterns, and ignored structure signals.

The GUI should support both copy and drag handoff:

- Copy: put `clipboard_bundle.txt` on the clipboard for fast paste into OpenClaw.
- Drag: expose generated files as native file URLs plus text MIME payload when available.
- Preview: double-click image references when a source path is available; otherwise show source metadata.

## Required Interaction States

- Silent Capture: start or pause the bypass monitor; stable scenes are recorded quietly.
- Needs Confirmation: show the candidate title, key references, semantic risk, and image-reading need.
- Ready To Handoff: show a preview of the exact OpenClaw context before copy or drag.
- Handed Off: mark that the user copied or dragged context and keep the source package traceable.

## APP vs Skill++

Recommendation: keep a small APP, but move heavier reasoning into Skill++ modules.

Use the APP for:

- local capture and privacy-gated preview
- user confirmation
- language switching
- drag/copy handoff
- record browsing
- packaging generated files

Use Skill++ for:

- downstream reasoning templates
- OpenClaw prompt shaping
- naming strategy
- extraction policy
- optional AI analysis
- repeatable workflows that can run without the GUI

This hybrid shape is stronger than choosing only one side. A pure APP makes reasoning hard to evolve. A pure Skill++ flow loses the visual confirmation and drag-out interaction that makes ScenePack useful.

## Near-Term Acceptance Criteria

- Interface text can switch between Chinese and English without restarting.
- Captured scene content summary follows the selected language.
- Generated package includes OpenClaw-ready files.
- User can drag generated files out of the GUI.
- User can copy a single compact OpenClaw context bundle.
- Key references are visible before generation.
