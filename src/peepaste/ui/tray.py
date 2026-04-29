from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from peepaste.analysis import LayoutAnalyzer
from peepaste.capture import capture_windows
from peepaste.generation import ProjectPackageManager
from peepaste.lifecycle import SceneLifecycle, ScenePhase, phase_label
from peepaste.monitor import SceneMonitor
from peepaste.settings import AppSettings
from peepaste.storage import ProjectPackageWriter

try:
    from PySide6.QtCore import QEasingCurve, QMimeData, QPointF, QPropertyAnimation, QRectF, Qt, QTimer, QUrl
    from PySide6.QtGui import QAction, QColor, QDesktopServices, QDrag, QIcon, QPainter, QPen, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QColorDialog,
        QComboBox,
        QDialog,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGraphicsOpacityEffect,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMenu,
        QMessageBox,
        QPushButton,
        QSizePolicy,
        QSpinBox,
        QSplitter,
        QSystemTrayIcon,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False

    class QWidget:  # type: ignore[no-redef]
        pass


_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


def run_tray(out_dir: Path) -> int:
    if not QT_AVAILABLE:
        print("PySide6 is not installed. Install with: py -m pip install -e .[gui]")
        return 1

    settings = AppSettings.load()
    if out_dir:
        settings.storage_root = str(out_dir)

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(_stylesheet(settings))

    window = _ScenePackWindow(settings, app)
    tray = QSystemTrayIcon(QIcon(), app)
    tray.setToolTip("ScenePack")
    menu = QMenu()
    open_action = QAction(_tr(settings, "open_peepaste"))
    open_action.triggered.connect(window.show)
    monitor_action = QAction(_tr(settings, "toggle_monitor"))
    monitor_action.triggered.connect(window.scene.toggle_monitor)
    capture_action = QAction(_tr(settings, "capture_now"))
    capture_action.triggered.connect(window.scene.capture_now)
    quit_action = QAction(_tr(settings, "quit"))
    quit_action.triggered.connect(app.quit)
    menu.addAction(open_action)
    menu.addAction(monitor_action)
    menu.addAction(capture_action)
    menu.addSeparator()
    menu.addAction(quit_action)
    tray.setContextMenu(menu)
    tray.show()
    window.show()
    return app.exec()


class _ScenePackWindow(QMainWindow):
    def __init__(self, settings: AppSettings, app: QApplication):
        super().__init__()
        self.settings = settings
        self.app = app
        self.setWindowTitle("ScenePack")
        self.resize(1120, 720)

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title_area = QVBoxLayout()
        self.title = QLabel("ScenePack")
        self.title.setObjectName("appTitle")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("subtitle")
        title_area.addWidget(self.title)
        title_area.addWidget(self.subtitle)
        header.addLayout(title_area, 1)

        self.language = QComboBox()
        self.language.addItem("中文", "zh")
        self.language.addItem("English", "en")
        self.language.setCurrentIndex(max(0, self.language.findData(settings.appearance.language)))
        self.theme = QComboBox()
        self.theme.addItems(["light", "dark"])
        self.theme.setCurrentText(settings.appearance.theme)
        header.addWidget(self.language)
        header.addWidget(self.theme)
        layout.addLayout(header)

        self.tabs = QTabWidget()
        self.scene = _SceneWorkbench(settings)
        self.history = _HistoryPanel(settings)
        self.prefs = _PreferencesPanel(settings, app, self.refresh_language)
        self.skills = _SkillsPanel(settings)
        self.tabs.addTab(self.scene, "")
        self.tabs.addTab(self.history, "")
        self.tabs.addTab(self.prefs, "")
        self.tabs.addTab(self.skills, "")
        layout.addWidget(self.tabs, 1)

        self.scene.record_saved = self.history.refresh
        self.language.currentIndexChanged.connect(self.change_language)
        self.theme.currentTextChanged.connect(self.change_theme)
        self.tabs.currentChanged.connect(self._fade_current_tab)
        self.refresh_language()

        if settings.install.auto_monitor:
            QTimer.singleShot(250, self.scene.start_monitor)

    def change_language(self) -> None:
        self.settings.appearance.language = str(self.language.currentData())
        self.settings.save()
        self.refresh_language()

    def change_theme(self) -> None:
        self.settings.appearance.theme = self.theme.currentText()
        self.settings.save()
        self.app.setStyleSheet(_stylesheet(self.settings))

    def refresh_language(self) -> None:
        self.language.blockSignals(True)
        self.language.setCurrentIndex(max(0, self.language.findData(self.settings.appearance.language)))
        self.language.blockSignals(False)
        self.theme.blockSignals(True)
        self.theme.setCurrentText(self.settings.appearance.theme)
        self.theme.blockSignals(False)
        self.subtitle.setText(_tr(self.settings, "subtitle"))
        self.tabs.setTabText(0, _tr(self.settings, "tab_scene"))
        self.tabs.setTabText(1, _tr(self.settings, "tab_history"))
        self.tabs.setTabText(2, _tr(self.settings, "tab_prefs"))
        self.tabs.setTabText(3, _tr(self.settings, "tab_skills"))
        for panel in (self.scene, self.history, self.prefs, self.skills):
            panel.refresh_language()

    def _fade_current_tab(self, index: int) -> None:
        widget = self.tabs.widget(index)
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", widget)
        animation.setDuration(160)
        animation.setStartValue(0.82)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(lambda: widget.setGraphicsEffect(None))
        widget._peepaste_animation = animation  # type: ignore[attr-defined]
        animation.start()


class _SceneWorkbench(QWidget):
    def __init__(self, settings: AppSettings):
        super().__init__()
        self.settings = settings
        self.lifecycle = SceneLifecycle()
        self.scene_monitor: SceneMonitor | None = None
        self.written_fingerprints: set[str] = set()
        self.last_package: Path | None = None
        self.last_analysis: Any = None
        self.generated_files: dict[str, Path] = {}
        self.record_saved = lambda: None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._monitor_tick)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        top = QHBoxLayout()
        self.phase_badge = QLabel()
        self.phase_badge.setObjectName("phaseBadge")
        self.monitor_status = QLabel()
        self.monitor_status.setObjectName("monitorStatus")
        top.addWidget(self.phase_badge)
        top.addWidget(self.monitor_status, 1)
        layout.addLayout(top)

        controls = QHBoxLayout()
        self.monitor_button = QPushButton()
        self.capture_button = QPushButton()
        self.filter_label = QLabel()
        self.filter_input = QLineEdit(settings.capture_filter)
        controls.addWidget(self.monitor_button)
        controls.addWidget(self.capture_button)
        controls.addWidget(self.filter_label)
        controls.addWidget(self.filter_input, 1)
        layout.addLayout(controls)

        decision_bar = QHBoxLayout()
        self.accept_input = QLineEdit()
        self.accept_button = QPushButton()
        self.reject_button = QPushButton()
        self.regenerate_button = QPushButton()
        self.preview_button = QPushButton()
        self.copy_button = QPushButton()
        self.open_package_button = QPushButton()
        decision_bar.addWidget(self.accept_input, 1)
        decision_bar.addWidget(self.accept_button)
        decision_bar.addWidget(self.reject_button)
        decision_bar.addWidget(self.regenerate_button)
        decision_bar.addWidget(self.preview_button)
        decision_bar.addWidget(self.copy_button)
        decision_bar.addWidget(self.open_package_button)
        layout.addLayout(decision_bar)

        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        layout.addWidget(splitter, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 10, 0)
        metric_grid = QGridLayout()
        self.item_metric = _MetricCard()
        self.group_metric = _MetricCard()
        self.risk_metric = _MetricCard()
        self.image_metric = _MetricCard()
        metric_grid.addWidget(self.item_metric, 0, 0)
        metric_grid.addWidget(self.group_metric, 0, 1)
        metric_grid.addWidget(self.risk_metric, 1, 0)
        metric_grid.addWidget(self.image_metric, 1, 1)
        left_layout.addLayout(metric_grid)
        self.preview = _LayoutPreview()
        left_layout.addWidget(self.preview, 1)
        self.refs_label = QLabel()
        self.refs = QListWidget()
        self.refs.itemDoubleClicked.connect(self.open_reference_item)
        left_layout.addWidget(self.refs_label)
        left_layout.addWidget(self.refs)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(10, 0, 0, 0)
        self.decision = QTextEdit()
        self.decision.setReadOnly(True)
        self.candidates = QListWidget()
        self.candidates.itemClicked.connect(self.use_candidate)
        self.handoff_preview = QTextEdit()
        self.handoff_preview.setReadOnly(True)
        self.exports = _DraggableExportList(on_handoff=self._mark_handed_off)
        self.exports.itemDoubleClicked.connect(lambda item: _open_path(Path(item.data(Qt.ItemDataRole.UserRole))))
        self.content_tabs = QTabWidget()
        self.content_tabs.addTab(self.decision, "")
        self.content_tabs.addTab(self.candidates, "")
        self.content_tabs.addTab(self.handoff_preview, "")
        self.content_tabs.addTab(self.exports, "")
        right_layout.addWidget(self.content_tabs)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([500, 620])

        self.monitor_button.clicked.connect(self.toggle_monitor)
        self.capture_button.clicked.connect(self.capture_now)
        self.accept_button.clicked.connect(self.accept_and_generate)
        self.reject_button.clicked.connect(self.reject_candidate)
        self.regenerate_button.clicked.connect(self.regenerate_handoff)
        self.preview_button.clicked.connect(self.preview_handoff)
        self.copy_button.clicked.connect(self.copy_openclaw_context)
        self.open_package_button.clicked.connect(self.open_package)
        self.refresh_language()
        self._render_empty()

    def refresh_language(self) -> None:
        self.monitor_button.setText(_tr(self.settings, "pause_monitor") if self.timer.isActive() else _tr(self.settings, "start_monitor"))
        self.capture_button.setText(_tr(self.settings, "capture_now"))
        self.filter_label.setText(_tr(self.settings, "filter"))
        self.accept_input.setPlaceholderText(_tr(self.settings, "accepted_title"))
        self.accept_button.setText(_tr(self.settings, "accept_generate"))
        self.reject_button.setText(_tr(self.settings, "reject_candidate"))
        self.regenerate_button.setText(_tr(self.settings, "regenerate"))
        self.preview_button.setText(_tr(self.settings, "preview_handoff"))
        self.copy_button.setText(_tr(self.settings, "copy_openclaw"))
        self.open_package_button.setText(_tr(self.settings, "open_package"))
        self.refs_label.setText(_tr(self.settings, "key_refs"))
        self.content_tabs.setTabText(0, _tr(self.settings, "decision"))
        self.content_tabs.setTabText(1, _tr(self.settings, "title_candidates"))
        self.content_tabs.setTabText(2, _tr(self.settings, "handoff_preview"))
        self.content_tabs.setTabText(3, _tr(self.settings, "drag_exports"))
        self.item_metric.set_title(_tr(self.settings, "items"))
        self.group_metric.set_title(_tr(self.settings, "groups"))
        self.risk_metric.set_title(_tr(self.settings, "semantic_risk"))
        self.image_metric.set_title(_tr(self.settings, "image_reading"))
        self._render_phase()
        if self.last_analysis:
            self._render_analysis()
        else:
            self._render_empty()

    def start_monitor(self) -> None:
        self.settings.capture_filter = self.filter_input.text().strip() or "Snipaste"
        self.settings.save()
        self.scene_monitor = SceneMonitor(
            lambda: capture_windows(process_filter=self.settings.capture_filter or None),
            stable_ticks_required=self.settings.install.stable_capture_ticks,
        )
        interval_ms = max(250, int(self.settings.install.monitor_interval_seconds * 1000))
        self.timer.start(interval_ms)
        self.monitor_button.setText(_tr(self.settings, "pause_monitor"))
        self.lifecycle.phase = ScenePhase.SILENT_CAPTURE
        self.lifecycle.last_event = "monitor_started"
        self._render_phase(_tr(self.settings, "monitor_running"))

    def stop_monitor(self) -> None:
        self.timer.stop()
        self.monitor_button.setText(_tr(self.settings, "start_monitor"))
        self.lifecycle.last_event = "monitor_paused"
        self._render_phase(_tr(self.settings, "monitor_paused"))

    def toggle_monitor(self) -> None:
        if self.timer.isActive():
            self.stop_monitor()
        else:
            self.start_monitor()

    def capture_now(self) -> None:
        self.settings.capture_filter = self.filter_input.text().strip() or "Snipaste"
        self.settings.save()
        snapshot = capture_windows(process_filter=self.settings.capture_filter or None)
        self._record_snapshot(snapshot, source_event="manual_capture")

    def _monitor_tick(self) -> None:
        if not self.scene_monitor:
            return
        try:
            tick = self.scene_monitor.tick()
        except Exception as exc:  # pragma: no cover - GUI runtime guard
            self.stop_monitor()
            QMessageBox.warning(self, "ScenePack", f"{_tr(self.settings, 'monitor_error')}\n{exc}")
            return
        status = _tr(
            self.settings,
            "monitor_tick",
            items=len(tick.snapshot.items),
            changes=len(tick.changes),
            stable=tick.stable_ticks,
        )
        self._render_phase(status)
        if tick.is_stable and tick.snapshot.items and tick.fingerprint not in self.written_fingerprints:
            self.written_fingerprints.add(tick.fingerprint)
            self._record_snapshot(tick.snapshot, source_event="silent_stable_capture")

    def _record_snapshot(self, snapshot, source_event: str) -> None:
        analysis = LayoutAnalyzer().analyze(snapshot)
        package = _new_package_dir(Path(self.settings.storage_root))
        ProjectPackageWriter(package).write_record(analysis)
        self.last_package = package
        self.last_analysis = analysis
        self.generated_files = {}
        self.lifecycle.captured(package)
        self.lifecycle.last_event = source_event
        if analysis.title_candidates:
            self.accept_input.setText(analysis.title_candidates[0]["title"])
        self._render_analysis()
        self.record_saved()

    def accept_and_generate(self) -> None:
        if not self.last_package:
            QMessageBox.warning(self, "ScenePack", _tr(self.settings, "capture_first"))
            return
        title = self.accept_input.text().strip()
        if not title:
            QMessageBox.warning(self, "ScenePack", _tr(self.settings, "title_first"))
            return
        self.lifecycle.title_selected(title)
        manager = ProjectPackageManager(self.last_package)
        manager.accept_title(title)
        result = manager.generate_after_acceptance()
        self.generated_files = result.files
        self.lifecycle.generated(result.files)
        self._render_exports()
        self.preview_handoff()
        self.record_saved()

    def reject_candidate(self) -> None:
        self.accept_input.clear()
        self.lifecycle.title_selected("")
        self.lifecycle.last_event = "candidate_rejected"
        self._render_phase(_tr(self.settings, "candidate_rejected"))
        self._render_decision()

    def regenerate_handoff(self) -> None:
        if not self.last_package:
            return
        try:
            result = ProjectPackageManager(self.last_package).generate_after_acceptance()
        except Exception as exc:
            QMessageBox.information(self, "ScenePack", f"{_tr(self.settings, 'generate_first')}\n{exc}")
            return
        self.generated_files = result.files
        self.lifecycle.generated(result.files)
        self._render_exports()
        self.preview_handoff()

    def use_candidate(self, item: QListWidgetItem) -> None:
        title = item.data(Qt.ItemDataRole.UserRole)
        if title:
            self.accept_input.setText(str(title))
            self.lifecycle.title_selected(str(title))
            self._render_decision()

    def preview_handoff(self) -> None:
        target = self._preferred_handoff_file()
        if not target or not target.exists():
            self.handoff_preview.setPlainText(_tr(self.settings, "handoff_not_ready"))
            self.content_tabs.setCurrentWidget(self.handoff_preview)
            return
        self.handoff_preview.setPlainText(target.read_text(encoding="utf-8"))
        self.content_tabs.setCurrentWidget(self.handoff_preview)

    def copy_openclaw_context(self) -> None:
        target = self._preferred_handoff_file()
        if not target or not target.exists():
            QMessageBox.information(self, "ScenePack", _tr(self.settings, "generate_first"))
            return
        QApplication.clipboard().setText(target.read_text(encoding="utf-8"))
        self._mark_handed_off()
        self._toast(_tr(self.settings, "copied"))

    def open_package(self) -> None:
        if self.last_package:
            _open_path(self.last_package)

    def open_reference_item(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.ItemDataRole.UserRole) or {}
        source = str(data.get("source_ref") or "")
        path = Path(source)
        if path.exists() and path.suffix.lower() in _IMAGE_SUFFIXES:
            _ImagePreviewDialog(path, self).exec()
            return
        if path.exists():
            _open_path(path)
            return
        QMessageBox.information(self, "ScenePack", _reference_text(data))

    def _preferred_handoff_file(self) -> Path | None:
        if not self.last_package:
            return None
        bundle = self.last_package / "clipboard_bundle.txt"
        prompt = self.last_package / "openclaw_prompt.md"
        return bundle if bundle.exists() else prompt

    def _mark_handed_off(self) -> None:
        self.lifecycle.handed_off()
        self._render_phase(_tr(self.settings, "handed_off"))
        self._render_decision()

    def _render_empty(self) -> None:
        self.item_metric.set_value("0")
        self.group_metric.set_value("0")
        self.risk_metric.set_value("-")
        self.image_metric.set_value("-")
        self.preview.set_items([])
        self.refs.clear()
        self.candidates.clear()
        self.exports.clear()
        self.decision.setPlainText(_tr(self.settings, "empty_decision"))
        self.handoff_preview.setPlainText(_tr(self.settings, "handoff_not_ready"))
        self._render_phase()

    def _render_analysis(self) -> None:
        if not self.last_analysis:
            return
        analysis = self.last_analysis
        self.item_metric.set_value(str(analysis.compression["item_count"]))
        self.group_metric.set_value(str(analysis.compression["group_count"]))
        self.risk_metric.set_value(_risk_label(self.settings, analysis.gates["semantic_risk"]))
        self.image_metric.set_value(_bool_label(self.settings, analysis.gates["needs_image_reading"]))
        self.preview.set_items(analysis.snapshot.items)
        self.refs.clear()
        for item in analysis.snapshot.items[:24]:
            list_item = QListWidgetItem(_reference_label(item))
            list_item.setData(Qt.ItemDataRole.UserRole, item.to_dict())
            list_item.setToolTip(_reference_text(item.to_dict()))
            self.refs.addItem(list_item)
        self.candidates.clear()
        for candidate in analysis.title_candidates:
            label = f"{candidate['title']}  -  {candidate['confidence']}"
            list_item = QListWidgetItem(label)
            list_item.setData(Qt.ItemDataRole.UserRole, candidate["title"])
            self.candidates.addItem(list_item)
        self._render_exports()
        self._render_decision()
        self._render_phase()
        self._toast(_analysis_message(self.settings, analysis))

    def _render_decision(self) -> None:
        if not self.last_analysis:
            self.decision.setPlainText(_tr(self.settings, "empty_decision"))
            return
        self.decision.setPlainText(_decision_text(self.settings, self.lifecycle, self.last_analysis, self.last_package))

    def _render_exports(self) -> None:
        self.exports.clear()
        files = self.generated_files or (_generated_files_from_state(self.last_package) if self.last_package else {})
        for name, path in files.items():
            self.exports.add_path(name, Path(path))
        if not files:
            self.exports.add_text(_tr(self.settings, "exports_after_generate"))

    def _render_phase(self, status: str = "") -> None:
        self.phase_badge.setText(phase_label(self.lifecycle.phase, self.settings.appearance.language))
        if status:
            self.monitor_status.setText(status)
        elif self.timer.isActive():
            self.monitor_status.setText(_tr(self.settings, "monitor_running"))
        else:
            self.monitor_status.setText(_tr(self.settings, "monitor_idle"))

    def _toast(self, _text: str) -> None:
        effect = QGraphicsOpacityEffect(self.decision)
        self.decision.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b"opacity", self.decision)
        animation.setDuration(180)
        animation.setStartValue(0.7)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.finished.connect(lambda: self.decision.setGraphicsEffect(None))
        self.decision._peepaste_animation = animation  # type: ignore[attr-defined]
        animation.start()


class _HistoryPanel(QWidget):
    def __init__(self, settings: AppSettings):
        super().__init__()
        self.settings = settings
        layout = QVBoxLayout(self)
        actions = QHBoxLayout()
        self.refresh_button = QPushButton()
        self.open_button = QPushButton()
        self.copy_button = QPushButton()
        actions.addWidget(self.refresh_button)
        actions.addWidget(self.open_button)
        actions.addWidget(self.copy_button)
        actions.addStretch(1)
        layout.addLayout(actions)

        splitter = QSplitter()
        self.records = QListWidget()
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.exports = _DraggableExportList()
        self.record_tabs = QTabWidget()
        self.record_tabs.addTab(self.details, "")
        self.record_tabs.addTab(self.exports, "")
        splitter.addWidget(self.records)
        splitter.addWidget(self.record_tabs)
        splitter.setSizes([360, 680])
        layout.addWidget(splitter, 1)

        self.refresh_button.clicked.connect(self.refresh)
        self.open_button.clicked.connect(self.open_selected)
        self.copy_button.clicked.connect(self.copy_selected_bundle)
        self.records.currentItemChanged.connect(lambda _current, _previous: self.show_selected())
        self.refresh()

    def refresh_language(self) -> None:
        self.refresh_button.setText(_tr(self.settings, "refresh"))
        self.open_button.setText(_tr(self.settings, "open_package"))
        self.copy_button.setText(_tr(self.settings, "copy_openclaw"))
        self.record_tabs.setTabText(0, _tr(self.settings, "details"))
        self.record_tabs.setTabText(1, _tr(self.settings, "drag_exports"))

    def refresh(self) -> None:
        self.records.clear()
        root = Path(self.settings.storage_root)
        packages = sorted(root.glob("scene_*")) if root.exists() else []
        for package in packages[-60:]:
            state = _load_json(package / "project_state.json")
            title = state.get("accepted_title") or (state.get("title_candidates") or [{}])[0].get("title", "Untitled")
            item = QListWidgetItem(f"{package.name} - {state.get('title_state', 'candidate')} - {title}")
            item.setData(Qt.ItemDataRole.UserRole, str(package))
            self.records.addItem(item)
        if self.records.count():
            self.records.setCurrentRow(self.records.count() - 1)
        else:
            self.details.setPlainText(_tr(self.settings, "no_records"))

    def show_selected(self) -> None:
        package = self._selected_package()
        self.exports.clear()
        if not package:
            return
        files = _generated_files_from_state(package)
        for name, path in files.items():
            self.exports.add_path(name, Path(path))
        summary = package / "summary.md"
        state = package / "project_state.json"
        if summary.exists():
            self.details.setPlainText(summary.read_text(encoding="utf-8"))
        elif state.exists():
            self.details.setPlainText(state.read_text(encoding="utf-8"))

    def open_selected(self) -> None:
        package = self._selected_package()
        if package:
            _open_path(package)

    def copy_selected_bundle(self) -> None:
        package = self._selected_package()
        if not package:
            return
        bundle = package / "clipboard_bundle.txt"
        prompt = package / "openclaw_prompt.md"
        target = bundle if bundle.exists() else prompt
        if target.exists():
            QApplication.clipboard().setText(target.read_text(encoding="utf-8"))

    def _selected_package(self) -> Path | None:
        item = self.records.currentItem()
        return Path(item.data(Qt.ItemDataRole.UserRole)) if item else None


class _PreferencesPanel(QWidget):
    def __init__(self, settings: AppSettings, app: QApplication, on_saved):
        super().__init__()
        self.settings = settings
        self.app = app
        self.on_saved = on_saved
        layout = QFormLayout(self)
        self.storage_input = QLineEdit(settings.storage_root)
        self.browse = QPushButton()
        storage_row = QHBoxLayout()
        storage_row.addWidget(self.storage_input)
        storage_row.addWidget(self.browse)
        self.language = QComboBox()
        self.language.addItem("中文", "zh")
        self.language.addItem("English", "en")
        self.language.setCurrentIndex(max(0, self.language.findData(settings.appearance.language)))
        self.theme = QComboBox()
        self.theme.addItems(["light", "dark"])
        self.theme.setCurrentText(settings.appearance.theme)
        self.font_size = QSpinBox()
        self.font_size.setRange(9, 24)
        self.font_size.setValue(settings.appearance.font_size)
        self.accent = QLineEdit(settings.appearance.accent_color)
        self.pick_color_button = QPushButton()
        color_row = QHBoxLayout()
        color_row.addWidget(self.accent)
        color_row.addWidget(self.pick_color_button)
        self.auto_monitor = QCheckBox()
        self.auto_monitor.setChecked(settings.install.auto_monitor)
        self.interval = QSpinBox()
        self.interval.setRange(1, 30)
        self.interval.setValue(max(1, int(settings.install.monitor_interval_seconds)))
        self.stable_ticks = QSpinBox()
        self.stable_ticks.setRange(1, 10)
        self.stable_ticks.setValue(settings.install.stable_capture_ticks)
        self.read_images = QCheckBox()
        self.read_images.setChecked(settings.privacy.read_images_by_default)
        self.upload_images = QCheckBox()
        self.upload_images.setChecked(settings.privacy.upload_images_by_default)
        self.save_button = QPushButton()
        self.labels = {key: QLabel() for key in ["storage", "language", "theme", "font_size", "accent", "auto_monitor", "interval", "stable_ticks", "privacy"]}
        layout.addRow(self.labels["storage"], storage_row)
        layout.addRow(self.labels["language"], self.language)
        layout.addRow(self.labels["theme"], self.theme)
        layout.addRow(self.labels["font_size"], self.font_size)
        layout.addRow(self.labels["accent"], color_row)
        layout.addRow(self.labels["auto_monitor"], self.auto_monitor)
        layout.addRow(self.labels["interval"], self.interval)
        layout.addRow(self.labels["stable_ticks"], self.stable_ticks)
        layout.addRow(self.labels["privacy"], self.read_images)
        layout.addRow("", self.upload_images)
        layout.addRow("", self.save_button)
        self.browse.clicked.connect(self.browse_storage)
        self.pick_color_button.clicked.connect(self.pick_color)
        self.save_button.clicked.connect(self.save)
        self.refresh_language()

    def refresh_language(self) -> None:
        self.language.blockSignals(True)
        self.language.setCurrentIndex(max(0, self.language.findData(self.settings.appearance.language)))
        self.language.blockSignals(False)
        self.theme.blockSignals(True)
        self.theme.setCurrentText(self.settings.appearance.theme)
        self.theme.blockSignals(False)
        self.browse.setText(_tr(self.settings, "browse"))
        self.pick_color_button.setText(_tr(self.settings, "pick"))
        self.auto_monitor.setText(_tr(self.settings, "start_monitor_on_open"))
        self.read_images.setText(_tr(self.settings, "read_images"))
        self.upload_images.setText(_tr(self.settings, "upload_images"))
        self.save_button.setText(_tr(self.settings, "save_prefs"))
        for key in self.labels:
            self.labels[key].setText(_tr(self.settings, key))

    def browse_storage(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, _tr(self.settings, "select_storage"), self.storage_input.text())
        if folder:
            self.storage_input.setText(folder)

    def pick_color(self) -> None:
        color = QColorDialog.getColor(QColor(self.accent.text()), self)
        if color.isValid():
            self.accent.setText(color.name())

    def save(self) -> None:
        self.settings.storage_root = self.storage_input.text().strip() or self.settings.storage_root
        self.settings.appearance.language = str(self.language.currentData())
        self.settings.appearance.theme = self.theme.currentText()
        self.settings.appearance.font_size = self.font_size.value()
        self.settings.appearance.accent_color = self.accent.text().strip() or self.settings.appearance.accent_color
        self.settings.install.auto_monitor = self.auto_monitor.isChecked()
        self.settings.install.monitor_interval_seconds = float(self.interval.value())
        self.settings.install.stable_capture_ticks = self.stable_ticks.value()
        self.settings.privacy.read_images_by_default = self.read_images.isChecked()
        self.settings.privacy.upload_images_by_default = self.upload_images.isChecked()
        self.settings.save()
        self.app.setStyleSheet(_stylesheet(self.settings))
        self.on_saved()
        QMessageBox.information(self, "ScenePack", _tr(self.settings, "prefs_saved"))


class _SkillsPanel(QWidget):
    def __init__(self, settings: AppSettings):
        super().__init__()
        self.settings = settings
        layout = QFormLayout(self)
        self.ai_enabled = QCheckBox()
        self.ai_enabled.setChecked(settings.ai.enabled)
        self.provider = QLineEdit(settings.ai.provider)
        self.key_env = QLineEdit(settings.ai.api_key_env)
        self.token_budget = QSpinBox()
        self.token_budget.setRange(500, 200000)
        self.token_budget.setValue(settings.ai.token_budget)
        self.title_patterns = QTextEdit("\n".join(settings.skills.title_patterns))
        self.ignored_signals = QTextEdit("\n".join(settings.skills.ignored_structure_signals))
        self.save_button = QPushButton()
        self.labels = {key: QLabel() for key in ["ai", "provider", "api_key_env", "token_budget", "title_patterns", "ignored_signals"]}
        layout.addRow(self.labels["ai"], self.ai_enabled)
        layout.addRow(self.labels["provider"], self.provider)
        layout.addRow(self.labels["api_key_env"], self.key_env)
        layout.addRow(self.labels["token_budget"], self.token_budget)
        layout.addRow(self.labels["title_patterns"], self.title_patterns)
        layout.addRow(self.labels["ignored_signals"], self.ignored_signals)
        layout.addRow("", self.save_button)
        self.save_button.clicked.connect(self.save)
        self.refresh_language()

    def refresh_language(self) -> None:
        self.ai_enabled.setText(_tr(self.settings, "enable_ai"))
        self.save_button.setText(_tr(self.settings, "save_skills"))
        for key in self.labels:
            self.labels[key].setText(_tr(self.settings, key))

    def save(self) -> None:
        self.settings.ai.enabled = self.ai_enabled.isChecked()
        self.settings.ai.provider = self.provider.text().strip() or self.settings.ai.provider
        self.settings.ai.api_key_env = self.key_env.text().strip() or self.settings.ai.api_key_env
        self.settings.ai.token_budget = self.token_budget.value()
        self.settings.skills.title_patterns = _non_empty_lines(self.title_patterns.toPlainText())
        self.settings.skills.ignored_structure_signals = _non_empty_lines(self.ignored_signals.toPlainText())
        self.settings.save()


class _MetricCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("metricCard")
        layout = QVBoxLayout(self)
        self.title = QLabel()
        self.value = QLabel("-")
        self.value.setObjectName("metricValue")
        layout.addWidget(self.title)
        layout.addWidget(self.value)

    def set_title(self, text: str) -> None:
        self.title.setText(text)

    def set_value(self, text: str) -> None:
        self.value.setText(text)


class _LayoutPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.items = []
        self.setMinimumHeight(260)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_items(self, items) -> None:
        self.items = list(items)
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#f8fafc"))
        if not self.items:
            painter.setPen(QColor("#64748b"))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No scene")
            return
        min_x = min(item.x for item in self.items)
        min_y = min(item.y for item in self.items)
        max_x = max(item.right for item in self.items)
        max_y = max(item.bottom for item in self.items)
        width = max(1.0, max_x - min_x)
        height = max(1.0, max_y - min_y)
        margin = 18
        scale = min((self.width() - margin * 2) / width, (self.height() - margin * 2) / height)
        ox = (self.width() - width * scale) / 2
        oy = (self.height() - height * scale) / 2
        colors = ["#0f766e", "#b45309", "#2563eb", "#be123c", "#4d7c0f", "#7c3aed"]
        for index, item in enumerate(self.items):
            rect_x = ox + (item.x - min_x) * scale
            rect_y = oy + (item.y - min_y) * scale
            rect_w = max(4, item.width * scale)
            rect_h = max(4, item.height * scale)
            color = QColor(colors[index % len(colors)])
            fill = QColor(color)
            fill.setAlpha(42)
            painter.setBrush(fill)
            painter.setPen(QPen(color, 2))
            painter.drawRoundedRect(QRectF(rect_x, rect_y, rect_w, rect_h), 6, 6)
            painter.setPen(color)
            painter.drawText(QPointF(rect_x + 6, rect_y + 16), item.id)


class _DraggableExportList(QListWidget):
    def __init__(self, on_handoff=None):
        super().__init__()
        self.on_handoff = on_handoff or (lambda: None)
        self.setDragEnabled(True)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)

    def add_path(self, label: str, path: Path) -> None:
        item = QListWidgetItem(f"{label}  -  {path.name}")
        item.setData(Qt.ItemDataRole.UserRole, str(path))
        text = path.read_text(encoding="utf-8") if path.exists() and path.suffix.lower() in {".md", ".txt"} else ""
        item.setData(Qt.ItemDataRole.UserRole + 1, text)
        item.setToolTip(str(path))
        self.addItem(item)

    def add_text(self, text: str) -> None:
        item = QListWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
        self.addItem(item)

    def startDrag(self, _supported_actions) -> None:
        selected = self.selectedItems()
        urls = []
        text_parts = []
        for item in selected:
            path_value = item.data(Qt.ItemDataRole.UserRole)
            if path_value:
                urls.append(QUrl.fromLocalFile(str(path_value)))
            text = item.data(Qt.ItemDataRole.UserRole + 1)
            if text:
                text_parts.append(str(text))
        if not urls and not text_parts:
            return
        mime = QMimeData()
        if urls:
            mime.setUrls(urls)
        if text_parts:
            mime.setText("\n\n".join(text_parts))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)
        self.on_handoff()


class _ImagePreviewDialog(QDialog):
    def __init__(self, path: Path, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(path.name)
        self.resize(860, 620)
        layout = QVBoxLayout(self)
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(str(path))
        label.setPixmap(pixmap.scaled(820, 560, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(label)


def _new_package_dir(root: Path) -> Path:
    from datetime import datetime

    root.mkdir(parents=True, exist_ok=True)
    return root / f"scene_{datetime.now().strftime('%Y%m%dT%H%M%S')}"


def _non_empty_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _load_json(path: Path) -> dict[str, Any]:
    if not path or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _generated_files_from_state(package: Path | None) -> dict[str, Path]:
    if not package:
        return {}
    state = _load_json(package / "project_state.json")
    return {name: Path(path) for name, path in state.get("generated_files", {}).items()}


def _open_path(path: Path) -> None:
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


def _analysis_message(settings: AppSettings, analysis) -> str:
    return analysis.layout_message.get(settings.appearance.language) or analysis.layout_message["en"]


def _decision_text(settings: AppSettings, lifecycle: SceneLifecycle, analysis, package: Path | None) -> str:
    message = _analysis_message(settings, analysis)
    if settings.appearance.language == "zh":
        return (
            f"{message}\n\n"
            f"状态：{phase_label(lifecycle.phase, 'zh')}\n"
            f"最近事件：{lifecycle.last_event}\n"
            f"包目录：{package or '-'}\n"
            f"需要确认标题：{_bool_label(settings, analysis.gates['needs_title_confirmation'])}\n"
            f"需要读图授权：{_bool_label(settings, analysis.gates['needs_image_reading'])}\n\n"
            "下一步：确认标题后生成交接包；生成后预览内容，再复制或拖给 OpenClaw。"
        )
    return (
        f"{message}\n\n"
        f"State: {phase_label(lifecycle.phase, 'en')}\n"
        f"Last event: {lifecycle.last_event}\n"
        f"Package: {package or '-'}\n"
        f"Needs title confirmation: {_bool_label(settings, analysis.gates['needs_title_confirmation'])}\n"
        f"Needs image permission: {_bool_label(settings, analysis.gates['needs_image_reading'])}\n\n"
        "Next: confirm the title, generate the handoff package, preview it, then copy or drag it to OpenClaw."
    )


def _reference_label(item) -> str:
    title = item.title or item.process or item.id
    return f"{item.id} - {title} - {int(item.width)}x{int(item.height)}"


def _reference_text(data: dict[str, Any]) -> str:
    return (
        f"ID: {data.get('id')}\n"
        f"Title: {data.get('title') or '-'}\n"
        f"Process: {data.get('process') or '-'}\n"
        f"Source: {data.get('source_ref') or '-'}\n"
        f"Box: {data.get('x')}, {data.get('y')}, {data.get('width')} x {data.get('height')}"
    )


def _risk_label(settings: AppSettings, risk: str) -> str:
    if settings.appearance.language == "zh":
        return {"low": "低", "medium": "中", "high": "高"}.get(risk, risk)
    return risk


def _bool_label(settings: AppSettings, value: bool) -> str:
    if settings.appearance.language == "zh":
        return "是" if value else "否"
    return "yes" if value else "no"


def _tr(settings: AppSettings, key: str, **kwargs) -> str:
    language = settings.appearance.language if settings.appearance.language in _TEXT else "en"
    value = _TEXT[language].get(key) or _TEXT["en"].get(key, key)
    return value.format(**kwargs) if kwargs else value


_TEXT = {
    "en": {
        "subtitle": "Quietly records the scene, asks for confirmation, then prepares a clean handoff.",
        "open_peepaste": "Open ScenePack",
        "toggle_monitor": "Start / pause monitor",
        "capture_now": "Capture now",
        "quit": "Quit",
        "tab_scene": "Scene",
        "tab_history": "History",
        "tab_prefs": "Preferences",
        "tab_skills": "Skills & AI",
        "start_monitor": "Start monitor",
        "pause_monitor": "Pause monitor",
        "filter": "Filter",
        "accepted_title": "Confirm or rewrite the scene title",
        "accept_generate": "Accept + Generate",
        "reject_candidate": "Reject",
        "regenerate": "Regenerate",
        "preview_handoff": "Preview handoff",
        "copy_openclaw": "Copy OpenClaw",
        "open_package": "Open package",
        "key_refs": "Key references",
        "decision": "Decision",
        "title_candidates": "Title candidates",
        "handoff_preview": "Handoff preview",
        "drag_exports": "Drag exports",
        "details": "Details",
        "items": "Items",
        "groups": "Groups",
        "semantic_risk": "Risk",
        "image_reading": "Image reading",
        "empty_decision": "The bypass is idle. Start monitoring or capture once to create a scene record.",
        "capture_first": "Capture a scene before accepting a title.",
        "title_first": "Confirm or rewrite the title first.",
        "generate_first": "Generate the handoff package first.",
        "copied": "OpenClaw context copied.",
        "candidate_rejected": "Candidate rejected. Rewrite the title or capture again.",
        "exports_after_generate": "Generate a handoff package to expose draggable files.",
        "handoff_not_ready": "No handoff package yet.",
        "handed_off": "Handoff marked as completed.",
        "monitor_running": "Bypass monitor is watching for stable scenes.",
        "monitor_idle": "Bypass monitor is idle.",
        "monitor_paused": "Bypass monitor paused.",
        "monitor_error": "Monitor stopped because capture failed.",
        "monitor_tick": "Tick: {items} items, {changes} changes, stable {stable}",
        "refresh": "Refresh",
        "no_records": "No records yet.",
        "browse": "Browse",
        "pick": "Pick",
        "start_monitor_on_open": "Start monitor when GUI opens",
        "read_images": "Allow image reading by default",
        "upload_images": "Allow image upload by default",
        "save_prefs": "Save preferences",
        "storage": "Storage",
        "language": "Language",
        "theme": "Theme",
        "font_size": "Font size",
        "accent": "Accent",
        "auto_monitor": "Auto monitor",
        "interval": "Monitor interval",
        "stable_ticks": "Stable ticks",
        "privacy": "Privacy",
        "select_storage": "Select storage folder",
        "prefs_saved": "Preferences saved.",
        "ai": "AI",
        "enable_ai": "Enable AI mode",
        "save_skills": "Save Skills & AI",
        "provider": "Provider",
        "api_key_env": "API key env",
        "token_budget": "Token budget",
        "title_patterns": "Title patterns",
        "ignored_signals": "Ignored signals",
    },
    "zh": {
        "subtitle": "安静记录现场，等待用户确认，再准备干净的下游交接。",
        "open_peepaste": "打开 ScenePack",
        "toggle_monitor": "开始 / 暂停监控",
        "capture_now": "立即捕获",
        "quit": "退出",
        "tab_scene": "现场",
        "tab_history": "历史",
        "tab_prefs": "偏好",
        "tab_skills": "Skill 与 AI",
        "start_monitor": "开始监控",
        "pause_monitor": "暂停监控",
        "filter": "过滤",
        "accepted_title": "确认或改写现场标题",
        "accept_generate": "确认并生成",
        "reject_candidate": "拒绝",
        "regenerate": "重新生成",
        "preview_handoff": "预览交接",
        "copy_openclaw": "复制给 OpenClaw",
        "open_package": "打开包",
        "key_refs": "关键参考",
        "decision": "决策",
        "title_candidates": "候选标题",
        "handoff_preview": "交接预览",
        "drag_exports": "拖拽导出",
        "details": "详情",
        "items": "项目",
        "groups": "分组",
        "semantic_risk": "风险",
        "image_reading": "读图",
        "empty_decision": "旁路当前空闲。开始监控或立即捕获后，会生成现场记录。",
        "capture_first": "请先捕获现场，再确认标题。",
        "title_first": "请先确认或改写标题。",
        "generate_first": "请先生成交接包。",
        "copied": "已复制 OpenClaw 上下文。",
        "candidate_rejected": "已拒绝候选标题。请改写标题或重新捕获。",
        "exports_after_generate": "生成交接包后，这里会出现可拖拽文件。",
        "handoff_not_ready": "还没有可交接内容。",
        "handed_off": "已标记为完成交接。",
        "monitor_running": "旁路监控正在观察稳定现场。",
        "monitor_idle": "旁路监控空闲。",
        "monitor_paused": "旁路监控已暂停。",
        "monitor_error": "捕获失败，监控已停止。",
        "monitor_tick": "轮询：{items} 个项目，{changes} 个变化，稳定 {stable} 次",
        "refresh": "刷新",
        "no_records": "暂无记录。",
        "browse": "浏览",
        "pick": "选择",
        "start_monitor_on_open": "打开 GUI 后自动开始监控",
        "read_images": "默认允许读图",
        "upload_images": "默认允许上传图片",
        "save_prefs": "保存偏好",
        "storage": "存储位置",
        "language": "语言",
        "theme": "主题",
        "font_size": "字号",
        "accent": "强调色",
        "auto_monitor": "自动监控",
        "interval": "监控间隔",
        "stable_ticks": "稳定次数",
        "privacy": "隐私",
        "select_storage": "选择存储文件夹",
        "prefs_saved": "偏好已保存。",
        "ai": "AI",
        "enable_ai": "启用 AI 模式",
        "save_skills": "保存 Skill 与 AI",
        "provider": "服务商",
        "api_key_env": "API Key 环境变量",
        "token_budget": "Token 预算",
        "title_patterns": "标题模式",
        "ignored_signals": "忽略信号",
    },
}


def _stylesheet(settings: AppSettings) -> str:
    accent = settings.appearance.accent_color
    font_size = settings.appearance.font_size
    if settings.appearance.theme == "dark":
        bg = "#15181c"
        panel = "#20252b"
        panel_2 = "#262c34"
        text = "#f5f7fb"
        muted = "#aab4c4"
        border = "#3a424f"
    else:
        bg = "#eef2f4"
        panel = "#ffffff"
        panel_2 = "#f8fafc"
        text = "#172033"
        muted = "#526070"
        border = "#d3dbe5"
    hover = QColor(accent).darker(112).name()
    return f"""
        QWidget {{
            background: {bg};
            color: {text};
            font-family: "{settings.appearance.font_family}";
            font-size: {font_size}px;
        }}
        #appTitle {{
            font-size: {font_size + 10}px;
            font-weight: 700;
        }}
        #subtitle, #monitorStatus {{
            color: {muted};
        }}
        #phaseBadge {{
            background: {panel_2};
            border: 1px solid {accent};
            border-radius: 8px;
            color: {accent};
            font-weight: 700;
            padding: 6px 10px;
        }}
        QTabWidget::pane, QTextEdit, QLineEdit, QComboBox, QSpinBox, QListWidget {{
            background: {panel};
            border: 1px solid {border};
            border-radius: 8px;
            padding: 6px;
        }}
        QTabBar::tab {{
            background: transparent;
            padding: 9px 14px;
            margin-right: 4px;
            border-bottom: 2px solid transparent;
        }}
        QTabBar::tab:selected {{
            color: {accent};
            border-bottom: 2px solid {accent};
        }}
        QPushButton {{
            background: {accent};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 9px 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: {hover};
        }}
        #metricCard {{
            background: {panel_2};
            border: 1px solid {border};
            border-radius: 8px;
        }}
        #metricValue {{
            font-size: {font_size + 8}px;
            font-weight: 700;
        }}
    """
