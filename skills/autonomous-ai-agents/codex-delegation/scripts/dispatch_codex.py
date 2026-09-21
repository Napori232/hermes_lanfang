"""
Codex Sub-task Dispatcher with Auto-Retry & Backup API Fallback
Dispatches coding tasks to Codex CLI with strictly scoped context (files/prompt only).
Handles 3 automatic retries on relay/network errors, then falls back to backup API/local model.
"""

import subprocess
import os
import time

def dispatch_to_codex(
    instruction: str, 
    target_files: list[str] = None, 
    workdir: str = None,
    max_retries: int = 3,
    backup_env: dict = None
) -> dict:
    """
    Invokes Codex CLI independently.
    Retries up to max_retries on transient errors (relay down, timeout, 429/5xx).
    Falls back to backup API / local endpoint if primary fails.
    """
    cmd = ["codex", "exec", "--sandbox", "danger-full-access"]
    
    prompt = instruction
    if target_files:
        files_hint = "\nTarget files:\n" + "\n".join(f"- {f}" for f in target_files)
        prompt += files_hint
        
    cmd.append(prompt)
    cwd = workdir or os.getcwd()

    # 1. 主线路重试 (最多 3 次)
    last_error = ""
    for attempt in range(1, max_retries + 1):
        try:
            res = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600
            )
            if res.returncode == 0:
                return {
                    "success": True,
                    "attempt": attempt,
                    "route": "primary",
                    "stdout": res.stdout,
                    "stderr": res.stderr
                }
            
            last_error = f"Exit code {res.returncode}: {res.stderr}"
            # 若是非网络/中转故障（如纯代码逻辑报错），直接返回让上层决策
            if "Connection" not in res.stderr and "50" not in res.stderr and "429" not in res.stderr:
                return {
                    "success": False,
                    "attempt": attempt,
                    "route": "primary",
                    "stdout": res.stdout,
                    "stderr": res.stderr
                }
        except subprocess.TimeoutExpired:
            last_error = "Execution timed out (600s)"
        except Exception as e:
            last_error = str(e)
        
        time.sleep(2 * attempt)

    # 2. 备用线路降级 (Backup API / 本地模型)
    if backup_env:
        env = os.environ.copy()
        env.update(backup_env)
        try:
            res = subprocess.run(
                cmd,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600
            )
            return {
                "success": res.returncode == 0,
                "attempt": 1,
                "route": "backup",
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except Exception as e:
            last_error = f"Backup route failed: {e}"

    return {
        "success": False,
        "route": "failed",
        "error": f"Failed after {max_retries} retries on primary, fallback also exhausted. Last error: {last_error}"
    }
