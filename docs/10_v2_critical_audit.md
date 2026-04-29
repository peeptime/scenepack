# V2 Critical Audit / 第二版批判性审计

Version: v0.1  
Date: 2026-04-29

## Verdict

V2 proves the capture and package-generation pipeline, but it is not yet a product-grade desktop interaction.

Current V2 is closer to:

- structural backend prototype
- command-line workflow
- placeholder tray GUI
- Snipaste pinned-window detection proof

It is not yet:

- real-time visual aggregation software
- Snipaste group-aware assistant
- polished tray product
- Codex-like judgment interface
- Snipaste-like interaction companion

## Main Findings

### 1. No Real User Interaction Flow

Current GUI exposes tabs and text boxes, but not a meaningful user journey.

Missing:

- first-run onboarding
- capture state explanation
- title candidate review
- accept / defer / reject title interactions
- visible generation queue
- history browsing with preview
- reversible actions

Impact:

The user can run the system, but cannot yet feel that ScenePack is working with them.

### 2. No Snipaste Group Switching Awareness

Current capture can filter `Paster - Snipaste` windows, but it does not know:

- which Snipaste group is active
- whether a group switch happened
- whether a scene is old, new, or resumed
- whether one set of pasters belongs to one work scene

Impact:

ScenePack may save snapshots, but it cannot yet understand scene continuity.

### 3. No Real-Time Change Monitoring

Current capture is manual.

Missing:

- polling loop
- debounce
- snapshot diff
- movement / resize cache
- new / removed item detection
- stable-scene detection
- pre-processing before writing files

Impact:

The current system records moments. It does not yet observe the user's thinking process.

### 4. Tray Icon Is Not Product-Grade

Current tray uses an empty `QIcon()`.

Missing:

- actual icon asset
- tray status states
- capture running state
- warning state
- generation-ready state
- left-click behavior
- right-click compact menu

Impact:

The app does not yet have a Windows desktop presence.

### 5. No ScenePack Output And Judgment Window

Current output is plain text in `QTextEdit`.

Missing:

- scene canvas
- detected boxes overlay
- group cards
- title candidate cards
- relation confidence display
- semantic-risk warning
- post-generation file list
- one-click open package
- human-readable reasoning pane

Impact:

The user cannot inspect or trust the system's judgment.

### 6. No Snipaste/Codex-Inspired Frontend

Current UI is basic PySide widgets.

Missing:

- compact desktop-native visual style
- command surface
- structured status rail
- calm but information-dense panel layout
- readable Chinese/English typography
- relationship visualization
- polished preference panels

Impact:

The product value exists in the engine, but not yet in the experience.

### 7. Structure Quality Is Not Yet Visible

The structure pool exists internally, but the user cannot see why the system made a judgment.

Missing:

- visual explanation of `attention_anchor`
- visual explanation of `grid_candidate`
- group boundary preview
- uncertainty and "do not infer" explanation
- small-image / whitespace / isolation interpretation

Impact:

The system may be right internally but still feel like a black box.

## Open-Source Patterns To Study

Use open-source projects as interaction references, not as copy-paste code sources unless license review is complete.

Useful references:

- Qt / PySide6 system tray pattern: `QSystemTrayIcon`
- CopyQ: tray-based productivity utility, history-oriented workflow, settings-heavy desktop app
- ShareX: capture workflow, tray actions, after-capture task pipeline
- ScreenCapture: lightweight Windows tray capture behavior

What to borrow:

- tray state model
- history list interaction
- after-capture task pipeline
- compact preferences layout
- action menu structure

What not to copy directly:

- proprietary brand elements
- icons
- UI assets
- GPL code into a proprietary codebase without a license decision

## V2.1 Required Work

### Interaction

- define first-run flow
- define tray click behavior
- define capture / monitoring / generated states
- add accept / reject / defer title actions
- add package open actions

### Monitoring

- add `SceneMonitor`
- poll Snipaste paster windows at a configurable interval
- hash layout snapshots
- debounce fast changes
- cache stable snapshots
- detect added, removed, moved, resized items

### Snipaste

- keep `--snipaste-pasters-only`
- add group-switch heuristic
- record paster hwnd continuity
- support visible group snapshot identity
- keep preferences windows out of scene capture

### UI

- add real tray icon
- add status-aware tray menu
- replace raw text output with:
  - scene overview
  - group list
  - title candidate list
  - relation summary
  - risk/gate display
  - generated-file actions

### Product Surface

- make ScenePack feel like a small desktop companion, not a CLI wrapper
- keep default output light
- keep internal structure rich
- make judgment inspectable

## V2.1 Success Criteria

- user opens Snipaste with pinned images
- ScenePack detects changes without manual capture
- tray icon state changes when scene changes
- stable scene creates a cached record
- title candidates appear in a judgment panel
- user can accept, reject, or defer title
- post-generation happens only after acceptance
- user can inspect why ScenePack thinks a structure exists

