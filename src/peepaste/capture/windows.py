from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path

from peepaste.capture.snipaste import inspect_snipaste_path
from peepaste.models import LayoutSnapshot, RectItem


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def capture_windows(
    process_filter: str | None = None,
    include_empty_title: bool = True,
    snipaste_pasters_only: bool = False,
) -> LayoutSnapshot:
    """Capture visible desktop windows through Win32 APIs.

    This is a non-invasive capture path. It does not modify or inspect Snipaste
    internals; it only observes normal desktop window geometry.
    """

    items: list[RectItem] = []
    process_filter_lower = process_filter.lower() if process_filter else None

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def enum_proc(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        rect = wintypes.RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return True
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        if width <= 0 or height <= 0:
            return True
        title = _window_text(hwnd)
        if not title and not include_empty_title:
            return True
        process_path = _process_path(hwnd)
        process_name = Path(process_path).name if process_path else ""
        class_name = _class_name(hwnd)
        haystack = " ".join([title, process_name, class_name, process_path]).lower()
        if process_filter_lower and process_filter_lower not in haystack:
            return True
        if snipaste_pasters_only and not _is_snipaste_paster(title, process_name, class_name):
            return True
        metadata = {"process_path": process_path}
        if process_name.lower() == "snipaste.exe":
            info = inspect_snipaste_path(process_path)
            metadata.update(
                {
                    "snipaste_version": info.version,
                    "snipaste_supported": info.supported,
                    "snipaste_supported_range": f"{info.supported_min}~{info.supported_max}",
                }
            )
        items.append(
            RectItem(
                id=f"win_{len(items) + 1:03d}",
                x=float(rect.left),
                y=float(rect.top),
                width=float(width),
                height=float(height),
                title=title,
                source_ref=str(hwnd),
                process=process_name,
                class_name=class_name,
                metadata=metadata,
            )
        )
        return True

    user32.EnumWindows(enum_proc, 0)
    source = "windows"
    if process_filter:
        source = f"windows:{process_filter}"
    if snipaste_pasters_only:
        source = f"{source}:pasters"
    return LayoutSnapshot(items=items, source=source)


def _is_snipaste_paster(title: str, process_name: str, class_name: str) -> bool:
    return (
        process_name.lower() == "snipaste.exe"
        and title == "Paster - Snipaste"
        and "toolsavebits" in class_name.lower()
    )


def _window_text(hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def _class_name(hwnd: int) -> str:
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def _process_path(hwnd: int) -> str:
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return ""
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return ""
    try:
        size = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return buffer.value
        return ""
    finally:
        kernel32.CloseHandle(handle)
