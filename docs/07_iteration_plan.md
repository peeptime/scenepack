# Iteration Plan / 迭代计划

Version: v0.1

## Version 1: Record-State Prototype

Goal:

Save a high-quality structural record of a visual desktop scene without requiring AI or deep image reading.

Scope:

- Python core package
- CLI entry
- Windows window capture through public Win32 APIs
- structure pool analysis
- title candidates
- layout message
- project package writer
- optional PySide6 tray shell
- standard library tests

Non-goals:

- full Snipaste internal integration
- default image upload
- heavy project reasoning before title acceptance
- production installer

## Version 2: AI And GUI Prototype

Goal:

Add stronger user-facing product value through optional image reading, preference UI, and title acceptance workflow.

Scope:

- workbench-style tray UI with four panels
- preferences for color, font size, language, storage, privacy
- skills settings entry
- API key settings
- AI mode adapter interface
- title acceptance tracking
- post-generation files after acceptance
- Snipaste-specific capture validation
- downstream handoff packaging for OpenClaw and similar tools

Current v2 implementation target:

- settings persistence
- title acceptance CLI
- post-generation package files
- four-panel PySide6 tray workbench UI
- default no-response bypass wired into the GUI through monitor start/pause
- lifecycle state display: silent capture, needs confirmation, ready to handoff, handed off
- layout preview, key references, and title candidate interaction
- copy-and-drag handoff files for downstream tools
- local tests for settings and post-generation
- internal packaging clarification for `dist` versus `build`

Still planned for later v2 hardening:

- real API provider invocation
- persistent title acceptance signals from user behavior
- Snipaste贴图窗口专项样本调参
- GUI smoke testing after PySide6 installation
- file-backed image previews from captured materials

## Version 3: Productization

Goal:

Move from prototype to dependable Windows desktop software.

Scope:

- installer
- auto-start option
- crash logging
- versioned schema migration
- signed builds
- update channel
- stronger privacy controls
- public brand review
- trademark and patent review
