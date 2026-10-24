---
name: windows-disk-cleanup
description: "Audit and clean developer disk space safely on Windows."
version: 0.1.0
author: Chen Luzhe, Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [disk, cleanup, windows, cache, storage]
---

# Windows Disk Cleanup Skill

Audit disk usage and reclaim storage on Windows developer systems without breaking active project environments or deleting personal data.

## When to Use

- User requests C drive cleanup, reports low disk space, or asks to investigate storage hogs.
- Periodic maintenance of bloated developer caches (NVIDIA shader cache, uv/pip, IDE AI runtimes).
- Don't use for: deleting user documents, source repositories, or databases without explicit user consent.

## Key Targets & Safety Profiles

| Path | Typical Size | Safety & Behavior |
| :--- | :--- | :--- |
| `AppData/Local/NVIDIA/DXCache` | 10–30+ GB | Safe. DirectX shader cache; rebuilt automatically by GPU driver as needed. |
| `AppData/Local/Temp` | 2–10+ GB | Safe. Skip files locked by running processes. |
| `AppData/Local/uv/cache` | 3–15+ GB | Safe. Run `uv cache clean` or remove files directly. |
| `AppData/Local/pip/cache` | 1–5 GB | Safe. Download cache. |
| IDE AI Runtimes (e.g. `AppData/Roaming/TRAE SOLO CN/ModularData`) | 3–10 GB | Confirm before full wipe; contains sandbox Python/Node VMs and local agent snapshots. |
| WeChat / Feishu media files | 5–20+ GB | Never delete directly; direct user to in-app storage managers. |

## Procedure

### 1. Diagnose Disk Usage Reliably

Do not rely on complex inline PowerShell scripts when running in MSYS/Git-Bash terminals due to quote and escaping breakage. Use Python with `os.scandir` or `df -h /c` for fast, accurate size auditing:

```python
import os

def get_dir_size(path):
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        total += get_dir_size(entry.path)
                except Exception:
                    pass
    except Exception:
        pass
    return total
```

### 2. Present Categorized Findings Before Wiping

Always classify storage into:
1. **Zero-risk safe caches** (NVIDIA DXCache, user Temp, pip/uv download caches).
2. **Conditional application runtimes** (discontinued IDEs, local agent snapshots, Docker/VM layers).
3. **Personal communication data** (WeChat `xwechat_files`, Feishu `LarkShell`) — report size only, never auto-delete.

### 3. Clean Locked & Read-Only Files Safely

Standard `shutil.rmtree` on Windows fails with `[WinError 5] Access is denied` whenever Git objects or read-only files are encountered (common in editor packages and cache snapshots).

Always supply an error handler that removes the `S_IWRITE` bit:

```python
import os, stat, shutil

def remove_readonly(func, path, excinfo):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

# Usage:
shutil.rmtree(target_dir, onerror=remove_readonly)
```

For directories containing files in use by running processes (e.g., `AppData/Local/Temp`), iterate and delete unlocked entries individually; do not let a single locked file abort the entire cleanup pass.

### 4. Verify & Report Results

Run `df -h /c` after cleaning and summarize:
- Space available before vs. after.
- Total gigabytes freed.
- Breakdown per category cleaned.

## Pitfalls

1. **PowerShell script parsing errors in bash:** Writing PowerShell one-liners with `Select-Object @{...}` through MSYS bash breaks on quotes and braces. Prefer native Python snippets.
2. **`uv cache clean` hangs on locked files:** If another process is holding the uv cache or virtualenv, `uv cache clean` may wait indefinitely or timeout. Use bounded timeouts or prune contents directly with Python.
3. **Wiping IDE sandboxes silently:** Tools like Trae, Cursor, and VS Code store full isolated Python/Node/binary distributions inside `AppData/Roaming`. Verify whether the user still uses that tool before wiping its environment files.
