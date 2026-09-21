"""
Codex Sub-task Dispatcher (Minimal Context Slicer)
Dispatches coding tasks to Codex CLI with strictly scoped context (files/prompt only).
"""

import subprocess
import os

def dispatch_to_codex(instruction: str, target_files: list[str] = None, workdir: str = None) -> dict:
    """
    Invokes Codex CLI independently.
    Only passes the specific instruction and relevant file paths to Codex.
    Central Gemini context is NOT passed to Codex.
    """
    cmd = ["codex", "exec", "--sandbox", "danger-full-access"]
    
    prompt = instruction
    if target_files:
        files_hint = "\nTarget files:\n" + "\n".join(f"- {f}" for f in target_files)
        prompt += files_hint
        
    cmd.append(prompt)
    
    cwd = workdir or os.getcwd()
    
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
        return {
            "success": res.returncode == 0,
            "returncode": res.returncode,
            "stdout": res.stdout,
            "stderr": res.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
