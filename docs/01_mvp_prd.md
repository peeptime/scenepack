# MVP PRD / 最小版本需求

Version: v0.1  
Target: ScenePack first desktop demo

## Target Environment

- Windows 11 Pro, build 22631.6783
- Snipaste Desktop 64-bit, version 2.10.8, 2025-06-03
- Desktop tray app
- Compact GUI panels

## First User

The first user is a heavy desktop visual worker:

- uses Snipaste or pinned screenshots often
- arranges multiple screenshots to think
- later sends the material to AI, documents, tables, or agents
- wants less repeated explanation of scattered materials

## MVP Goal

The MVP should prove:

> ScenePack can silently capture a visual scene and save a high-quality structural record that is useful for later title matching, AI reasoning, and project package generation.

## Must Have

- Windows tray tool
- Snipaste-oriented scene capture
- layout snapshot capture
- high-quality structure pool tagging
- timestamped scene records
- light layout message
- title candidate attempt
- title acceptance state
- preference GUI
- color settings
- font size settings
- language settings: English and Chinese
- AI provider settings
- skill settings entry for user personalization
- visual layout preview in the GUI
- key reference list before generation
- drag or copy handoff files for downstream tools
- start/pause control for the default bypass monitor
- visible lifecycle state for the current scene
- handoff preview before copying or dragging downstream context

## Compact Windows

The first GUI should use compact panels arranged as a practical workbench rather than a large workspace or a pure text log view.

Recommended panels:

- Scene: bypass monitor state, current captured layout, title candidates, key references, and generation actions
- Scene Records: timestamped scene history and generated handoff files
- Preferences: appearance, language, storage, privacy
- Skills And AI: API keys, AI mode, personal rules, structure preferences

## Default Capture Output

Immediately after capture, ScenePack should save only:

- timestamp
- layout snapshot
- structure tags
- layout message
- optional title candidates

It should not immediately generate full project reasoning files.

## Title Handling

ScenePack may attempt an initial title.

The title can come from:

- layout structure
- user typed text
- image content in AI mode
- repeated scene similarity
- user edits or acceptance behavior

The title becomes accepted only after one of these signals:

- user clicks accept
- user opens the title and does not modify it
- user sees the same title twice without changing it
- user keeps using the same title across stable snapshots

## Post Generation

Only after title or intent acceptance should ScenePack silently generate deeper files:

- relation reasoning
- project summary
- naming plan
- task brief
- downstream export files
- OpenClaw handoff prompt
- quick review sheet
- compact clipboard bundle

## Non Goals For MVP

- replacing Snipaste
- modifying Snipaste internals
- reverse engineering Snipaste
- uploading images by default
- forcing users to name projects
- generating many files before title acceptance
- treating spatial structure as confirmed semantic truth

## Success Criteria

- capture is stable on the target Windows and Snipaste version
- default records are small but structurally rich
- title candidates feel useful, not invasive
- AI mode can produce a stronger title or summary when enabled
- users can keep working without extra manual steps
- users can understand what needs confirmation before handoff
- downstream files can be copied or dragged out without manual repackaging
- default monitoring happens visibly but does not interrupt the user
- handoff content is previewable before it leaves ScenePack
