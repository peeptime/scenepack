from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from peepaste.analysis import LayoutAnalyzer
from peepaste.capture import capture_windows
from peepaste.generation import ProjectPackageManager
from peepaste.monitor import SceneMonitor
from peepaste.models import LayoutSnapshot
from peepaste.settings import AppSettings
from peepaste.storage import ProjectPackageWriter


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="peepaste", description="ScenePack local visual aggregation prototype.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Initialize ScenePack for internal testing.")
    init.add_argument("--storage-root", default="", help="Project package storage root.")
    init.add_argument("--language", choices=["en", "zh"], default="en")
    init.add_argument("--theme", choices=["light", "dark"], default="light")
    init.add_argument("--capture-filter", default="Snipaste")
    init.add_argument("--auto-monitor", action="store_true")
    init.add_argument("--startup-on-login", action="store_true")

    demo = subparsers.add_parser("demo", help="Analyze the bundled sample layout and write a project package.")
    demo.add_argument("--out", default=".peepaste-runs/demo", help="Output project package directory.")

    analyze = subparsers.add_parser("analyze", help="Analyze a layout JSON file.")
    analyze.add_argument("layout", help="Path to a JSON file with an items array.")
    analyze.add_argument("--out", default="", help="Optional project package output directory.")

    capture = subparsers.add_parser("capture-windows", help="Capture visible Windows desktop windows.")
    capture.add_argument("--process", default="", help="Optional process/title/class filter, for example Snipaste.")
    capture.add_argument("--snipaste-pasters-only", action="store_true", help="Keep only visible Snipaste pinned-image windows.")
    capture.add_argument("--out", default=".peepaste-runs/windows-capture", help="Output project package directory.")

    monitor = subparsers.add_parser("monitor-snipaste", help="Poll Snipaste pinned-image windows and cache stable scenes.")
    monitor.add_argument("--iterations", type=int, default=5, help="Number of polling ticks. Use 0 for continuous monitoring.")
    monitor.add_argument("--interval", type=float, default=1.5, help="Polling interval in seconds.")
    monitor.add_argument("--stable-ticks", type=int, default=2, help="Ticks required before a scene is considered stable.")
    monitor.add_argument("--out-root", default=".peepaste-runs/monitored-scenes", help="Root directory for stable scene packages.")

    accept = subparsers.add_parser("accept-title", help="Accept a project title and optionally generate post files.")
    accept.add_argument("package", help="Project package directory.")
    accept.add_argument("--title", required=True, help="Accepted title.")
    accept.add_argument("--generate", action="store_true", help="Generate post-acceptance files immediately.")

    generate = subparsers.add_parser("generate", help="Generate post-acceptance files for a package.")
    generate.add_argument("package", help="Project package directory.")

    settings = subparsers.add_parser("settings", help="Manage ScenePack settings.")
    settings_sub = settings.add_subparsers(dest="settings_command", required=True)
    settings_sub.add_parser("init", help="Write default settings if missing.")
    settings_sub.add_parser("show", help="Print current settings.")
    set_cmd = settings_sub.add_parser("set", help="Set a top-level setting.")
    set_cmd.add_argument("key", choices=["storage_root", "capture_filter", "language", "theme", "font_size", "accent_color", "ai_enabled", "ai_provider", "ai_key_env"])
    set_cmd.add_argument("value")

    gui = subparsers.add_parser("gui", help="Start optional PySide6 tray UI.")
    gui.add_argument("--out", default=".peepaste-runs/gui", help="Output project package directory.")

    args = parser.parse_args(argv)
    if args.command == "init":
        return _init_command(args)
    if args.command == "demo":
        sample = Path(__file__).resolve().parents[2] / "samples" / "sample_layout.json"
        return _analyze_file(sample, Path(args.out), write=True)
    if args.command == "analyze":
        return _analyze_file(Path(args.layout), Path(args.out) if args.out else None, write=bool(args.out))
    if args.command == "capture-windows":
        snapshot = capture_windows(process_filter=args.process or None, snipaste_pasters_only=args.snipaste_pasters_only)
        analysis = LayoutAnalyzer().analyze(snapshot)
        paths = ProjectPackageWriter(args.out).write_record(analysis)
        _print_result(analysis, paths)
        return 0
    if args.command == "monitor-snipaste":
        return _monitor_snipaste(args)
    if args.command == "accept-title":
        manager = ProjectPackageManager(args.package)
        manager.accept_title(args.title)
        print(f"Accepted title: {args.title}")
        if args.generate:
            result = manager.generate_after_acceptance()
            _print_generated(result.files)
        return 0
    if args.command == "generate":
        result = ProjectPackageManager(args.package).generate_after_acceptance()
        _print_generated(result.files)
        return 0
    if args.command == "settings":
        return _settings_command(args)
    if args.command == "gui":
        from peepaste.ui.tray import run_tray

        return run_tray(Path(args.out))
    return 2


def _analyze_file(path: Path, out: Path | None, write: bool) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    snapshot = LayoutSnapshot.from_mapping(data)
    analysis = LayoutAnalyzer().analyze(snapshot)
    paths = ProjectPackageWriter(out).write_record(analysis) if write and out else {}
    _print_result(analysis, paths)
    return 0


def _print_result(analysis, paths: dict) -> None:
    print(analysis.layout_message["en"])
    print(analysis.layout_message["zh"])
    if analysis.title_candidates:
        best = analysis.title_candidates[0]
        print(f"Title candidate: {best['title']} ({best['confidence']})")
    print(f"Silent generation ready: {analysis.gates['silent_generation_ready']}")
    for name, path in paths.items():
        print(f"{name}: {path}")


def _print_generated(paths: dict) -> None:
    for name, path in paths.items():
        print(f"{name}: {path}")


def _settings_command(args) -> int:
    settings_path = AppSettings.default_path()
    settings = AppSettings.load(settings_path)
    if args.settings_command == "init":
        path = settings.save(settings_path)
        print(f"settings: {path}")
        return 0
    if args.settings_command == "show":
        print(json.dumps(settings.to_dict(), ensure_ascii=False, indent=2))
        return 0
    if args.settings_command == "set":
        _set_setting(settings, args.key, args.value)
        path = settings.save(settings_path)
        print(f"settings: {path}")
        return 0
    return 2


def _init_command(args) -> int:
    settings = AppSettings.load()
    if args.storage_root:
        settings.storage_root = os.path.expandvars(args.storage_root)
    settings.appearance.language = args.language
    settings.appearance.theme = args.theme
    settings.capture_filter = args.capture_filter
    settings.install.auto_monitor = args.auto_monitor
    settings.install.startup_on_login = args.startup_on_login
    settings.install.initialized = True
    path = settings.save()
    print(f"Initialized ScenePack settings: {path}")
    print(f"Storage root: {settings.storage_root}")
    print(f"Auto monitor: {settings.install.auto_monitor}")
    return 0


def _monitor_snipaste(args) -> int:
    out_root = Path(args.out_root)
    monitor = SceneMonitor(
        lambda: capture_windows(process_filter="Snipaste", snipaste_pasters_only=True),
        stable_ticks_required=args.stable_ticks,
    )
    written = set()
    ticks = monitor.run(iterations=args.iterations, interval_seconds=args.interval)
    for index, tick in enumerate(ticks, start=1):
        print(
            f"tick={index} items={len(tick.snapshot.items)} changes={len(tick.changes)} "
            f"stable_ticks={tick.stable_ticks} stable={tick.is_stable}"
        )
        if tick.is_stable and tick.fingerprint not in written and tick.snapshot.items:
            analysis = LayoutAnalyzer().analyze(tick.snapshot)
            package = out_root / f"scene_{tick.snapshot.captured_at.replace(':', '').replace('.', '')}"
            paths = ProjectPackageWriter(package).write_record(analysis)
            written.add(tick.fingerprint)
            print(f"stable_package: {paths['state']}")
    return 0


def _set_setting(settings: AppSettings, key: str, value: str) -> None:
    if key == "storage_root":
        settings.storage_root = value
    elif key == "capture_filter":
        settings.capture_filter = value
    elif key == "language":
        settings.appearance.language = value
    elif key == "theme":
        settings.appearance.theme = value
    elif key == "font_size":
        settings.appearance.font_size = int(value)
    elif key == "accent_color":
        settings.appearance.accent_color = value
    elif key == "ai_enabled":
        settings.ai.enabled = value.lower() in {"1", "true", "yes", "on"}
    elif key == "ai_provider":
        settings.ai.provider = value
    elif key == "ai_key_env":
        settings.ai.api_key_env = value
