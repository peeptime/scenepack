param(
    [string]$Channel = "internal",
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root

function Invoke-Checked {
    param([scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE"
    }
}

function Assert-PackageNotRunning {
    $DistRoot = (Resolve-Path -LiteralPath "dist" -ErrorAction SilentlyContinue)
    if (-not $DistRoot) {
        return
    }

    $Running = Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -in @("ScenePack.exe", "ScenePackCLI.exe") -and
            $_.ExecutablePath -and
            $_.ExecutablePath.StartsWith($DistRoot.Path, [System.StringComparison]::OrdinalIgnoreCase)
        } |
        Select-Object ProcessId, Name, ExecutablePath

    if ($Running) {
        $Details = ($Running | ForEach-Object { "PID $($_.ProcessId): $($_.ExecutablePath)" }) -join [Environment]::NewLine
        throw "Close the running packaged ScenePack app before rebuilding. Running processes:$([Environment]::NewLine)$Details"
    }
}

try {
    if (-not $SkipInstall) {
        Invoke-Checked { py -m pip install -e ".[gui]" }
    }

    Assert-PackageNotRunning
    Invoke-Checked { py -m PyInstaller --noconfirm --clean "packaging\peepaste_internal.spec" }

    $Version = py -c "import peepaste; print(peepaste.__version__)"
    $PackageName = "ScenePack-$Version-$Channel-win64"
    $PackageRoot = Join-Path "dist" $PackageName
    $ZipPath = Join-Path "dist" "$PackageName.zip"

    if (Test-Path $PackageRoot) {
        Remove-Item -Recurse -Force $PackageRoot
    }
    if (Test-Path $ZipPath) {
        Remove-Item -Force $ZipPath
    }

    New-Item -ItemType Directory -Force -Path $PackageRoot | Out-Null
    if (-not (Test-Path "dist\ScenePack")) {
        throw "PyInstaller output not found: dist\ScenePack"
    }
    Copy-Item -Recurse -Force "dist\ScenePack\*" $PackageRoot
    Copy-Item -Force "packaging\default_settings.internal.json" $PackageRoot
    Copy-Item -Force "README.md" $PackageRoot
    Copy-Item -Force "docs\12_internal_test_installer.md" $PackageRoot

    Compress-Archive -Path (Join-Path $PackageRoot "*") -DestinationPath $ZipPath
    Remove-Item -Force -ErrorAction SilentlyContinue "build\peepaste_internal\ScenePack.exe", "build\peepaste_internal\ScenePackCLI.exe"
    Write-Host "Built internal package: $ZipPath"
    Write-Host "Run the app from: dist\ScenePack\ScenePack.exe"
    Write-Host "Do not run executables from build\peepaste_internal; that folder is only PyInstaller work output."
}
finally {
    Pop-Location
}
