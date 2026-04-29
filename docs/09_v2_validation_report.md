# V2 Validation Report / 第二版验证报告

Version: v0.1  
Date: 2026-04-29

## Implemented

- settings persistence
- skills and AI settings data model
- AI adapter boundary with safe null adapter
- title acceptance command
- post-acceptance generation
- project files after acceptance:
  - `project.json`
  - `relations.json`
  - `summary.md`
  - `naming_plan.json`
  - `materials_manifest.csv`
  - `agent_context.md`
- four-panel PySide6 tray UI:
  - Scene Monitor
  - Scene Records
  - Preferences
  - Skills & AI

## Local Checks

Passed:

```powershell
$env:PYTHONPATH="src"
py -m unittest discover -s tests
py -m compileall -q src tests
py -m peepaste demo --out .peepaste-runs\v2-demo
py -m peepaste accept-title .peepaste-runs\v2-demo --title "Accepted Visual Scene" --generate
py -m peepaste capture-windows --out .peepaste-runs\v2-windows-smoke
py -m peepaste accept-title .peepaste-runs\v2-windows-smoke --title "Windows Smoke Scene" --generate
```

GUI dependency installed and import check passed:

```powershell
py -m pip install -e '.[gui]'
py -c "import PySide6; import peepaste.ui.tray; print('gui import ok')"
```

## Snipaste Status

The command below ran successfully but captured 0 items in the current desktop state:

```powershell
py -m peepaste capture-windows --process Snipaste --out .peepaste-runs\v2-snipaste-smoke
```

Interpretation:

- the capture pipeline works
- no currently visible window matched the `Snipaste` filter during this run
- real Snipaste pinned-image scenes are still required for filter calibration

## Snipaste 6-Image Calibration

After preparing a real desktop scene with 6 Snipaste pinned images, the first broad filter captured 7 Snipaste windows:

- 6 pinned-image windows titled `Paster - Snipaste`
- 1 Snipaste preferences window

The capture filter was then refined with `--snipaste-pasters-only`.

Validated command:

```powershell
py -m peepaste capture-windows --process Snipaste --snipaste-pasters-only --out .peepaste-runs\snipaste-6-pasters-only
```

Result:

- captured 6 items
- all 6 items were `Paster - Snipaste`
- the Snipaste preferences window was excluded
- Chinese layout message rendered correctly when read as UTF-8

## Known Gaps

- no real AI provider call yet
- no persistent behavioral title-acceptance signal yet
- no packaged Windows installer yet
- GUI was import-tested, not long-running interaction tested
- Snipaste-specific filtering still needs real pinned image samples

## Next Validation Need

Prepare three real Snipaste scenes:

- 3 to 8 images
- 10 to 30 images
- mixed-content scene

Then run:

```powershell
peepaste capture-windows --process Snipaste --out .peepaste-runs\snipaste-real-01
```
