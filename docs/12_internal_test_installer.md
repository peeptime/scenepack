# Internal Test Installer / 内测安装包

Version: v0.1  
Target package: ScenePack `0.3.0` internal build

## Package Type

The first internal build uses a PyInstaller one-folder package compressed as a ZIP.

This is intentional for internal testing:

- no registry writes by default
- easy to delete
- lower installer risk
- suitable for rapid Snipaste compatibility testing

A formal `.exe` installer can be added later through Inno Setup, NSIS, MSIX, or separate platform installers.

## Build

```powershell
.\tools\build_internal_package.ps1
```

Close any running packaged `ScenePack.exe` or `ScenePackCLI.exe` from `dist\` before rebuilding. The build script checks this up front because PyInstaller cannot replace a release folder while Windows still has one of its executables open.

Output:

```text
dist\ScenePack-0.3.0-internal-win64.zip
```

Run only the release output:

```text
dist\ScenePack\ScenePack.exe
dist\ScenePack-0.3.0-internal-win64\ScenePack.exe
```

Do not run `build\peepaste_internal\ScenePack.exe`. The `build` folder is PyInstaller work output and does not contain the full `_internal` runtime folder, so that intermediate executable can fail with `Error loading Python DLL`.

## First Run Initialization

After extracting the ZIP, run:

```powershell
ScenePackCLI.exe init --storage-root "$env:USERPROFILE\Documents\ScenePack\Projects" --language en --theme light --capture-filter Snipaste
```

Optional:

```powershell
ScenePackCLI.exe init --auto-monitor
ScenePackCLI.exe init --startup-on-login
```

The internal package includes:

- `default_settings.internal.json`
- `README.md`
- this installer note

## Snipaste Compatibility Target

Current internal target:

- Windows 11 Pro 22631.6783
- Snipaste Windows desktop
- Snipaste versions `2.10.8` through `2.11.3`
- pinned-image windows titled `Paster - Snipaste`
- class name containing `ToolSaveBits`

The app records detected Snipaste version metadata when available.

## Future Platform Packages

Separate packages are allowed and recommended:

- Windows 11 current
- Windows 11 older builds
- Windows 10
- macOS

The capture backend should remain platform-specific while analysis, package storage, settings, and AI adapters remain shared.

## Internal Test Checklist

- launch `ScenePack.exe`
- run initialization with `ScenePackCLI.exe`
- verify tray icon appears
- open 3 to 8 Snipaste pinned images
- run capture from the tray or CLI
- run `monitor-snipaste`
- accept a title
- confirm post-generation files are created
- test Snipaste `2.10.8` through `2.11.3`
- record failures with OS build, Snipaste version, number of pinned images, and whether groups changed

## Build Validation

Validated locally on Windows 11 Pro `22631.6783`:

```powershell
.\tools\build_internal_package.ps1 -SkipInstall
```

Generated:

```text
dist\ScenePack-0.3.0-internal-win64.zip
```

Smoke-tested packaged CLI:

```powershell
.\dist\ScenePack\ScenePackCLI.exe --help
.\dist\ScenePack\ScenePackCLI.exe init --storage-root "%USERPROFILE%\Documents\ScenePack\Projects" --language en --theme light --capture-filter Snipaste
.\dist\ScenePack\ScenePackCLI.exe monitor-snipaste --iterations 2 --interval 0.1 --stable-ticks 2
```

Package contents include:

- `ScenePack.exe` for GUI launch
- `ScenePackCLI.exe` for initialization, diagnostics, monitoring, and automation
- bundled docs and samples
- `default_settings.internal.json`

Known packaging note:

PyInstaller may warn about some Windows `api-ms-*` DLL references during analysis. The local build and packaged CLI smoke tests still passed on the target Windows 11 build. These warnings must be checked again on Windows 10 and older Windows 11 builds.

## Next Installer Step

For the next internal package, add:

- real `.ico` tray icon
- startup shortcut creation option
- uninstall script
- release manifest
- separate Windows 10 validation package if needed
