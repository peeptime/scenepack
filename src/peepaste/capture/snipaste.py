from __future__ import annotations

import ctypes
import re
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_MIN = "2.10.8"
SUPPORTED_MAX = "2.11.3"


@dataclass(frozen=True)
class SnipasteVersionInfo:
    path: str
    version: str
    supported: bool
    supported_min: str = SUPPORTED_MIN
    supported_max: str = SUPPORTED_MAX


def inspect_snipaste_path(path: str) -> SnipasteVersionInfo:
    version = get_file_version(path) or parse_version_from_path(path) or "unknown"
    supported = is_supported_version(version)
    return SnipasteVersionInfo(path=path, version=version, supported=supported)


def is_supported_version(version: str, min_version: str = SUPPORTED_MIN, max_version: str = SUPPORTED_MAX) -> bool:
    parsed = parse_version(version)
    if not parsed:
        return False
    min_tuple = parse_version(min_version)
    max_tuple = parse_version(max_version)
    return bool(min_tuple and max_tuple and min_tuple <= parsed <= max_tuple)


def parse_version(version: str) -> tuple[int, ...] | None:
    match = re.search(r"(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?", version)
    if not match:
        return None
    return tuple(int(part) for part in match.groups(default="0"))


def parse_version_from_path(path: str) -> str:
    match = re.search(r"Snipaste[-_]?(\d+\.\d+\.\d+(?:\.\d+)?)", path, flags=re.IGNORECASE)
    return match.group(1) if match else ""


def get_file_version(path: str) -> str:
    target = Path(path)
    if not target.exists():
        return ""
    version = ctypes.WinDLL("version", use_last_error=True)
    size = version.GetFileVersionInfoSizeW(str(target), None)
    if not size:
        return ""
    buffer = ctypes.create_string_buffer(size)
    if not version.GetFileVersionInfoW(str(target), 0, size, buffer):
        return ""
    value = ctypes.c_void_p()
    value_len = wintypes.UINT()
    if not version.VerQueryValueW(buffer, "\\", ctypes.byref(value), ctypes.byref(value_len)):
        return ""
    fixed = ctypes.cast(value, ctypes.POINTER(VS_FIXEDFILEINFO)).contents
    major = fixed.dwFileVersionMS >> 16
    minor = fixed.dwFileVersionMS & 0xFFFF
    patch = fixed.dwFileVersionLS >> 16
    build = fixed.dwFileVersionLS & 0xFFFF
    if build:
        return f"{major}.{minor}.{patch}.{build}"
    return f"{major}.{minor}.{patch}"


class VS_FIXEDFILEINFO(ctypes.Structure):
    _fields_ = [
        ("dwSignature", wintypes.DWORD),
        ("dwStrucVersion", wintypes.DWORD),
        ("dwFileVersionMS", wintypes.DWORD),
        ("dwFileVersionLS", wintypes.DWORD),
        ("dwProductVersionMS", wintypes.DWORD),
        ("dwProductVersionLS", wintypes.DWORD),
        ("dwFileFlagsMask", wintypes.DWORD),
        ("dwFileFlags", wintypes.DWORD),
        ("dwFileOS", wintypes.DWORD),
        ("dwFileType", wintypes.DWORD),
        ("dwFileSubtype", wintypes.DWORD),
        ("dwFileDateMS", wintypes.DWORD),
        ("dwFileDateLS", wintypes.DWORD),
    ]

