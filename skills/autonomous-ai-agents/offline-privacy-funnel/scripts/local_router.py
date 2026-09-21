"""
Local Model Router & Context Slicer (Ollama Qwen3:8b)
Provides lightweight, offline routing, regex filtering, and minimal-context structuring.
"""

import json
import re
import urllib.request
import urllib.error

OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen3:8b"

TRIVIAL_PATTERNS = [
    r"^(收到|好的|好|ok|OK|行|可以|嗯|嗯嗯|知道了|哈哈|嘻嘻|拉倒|得嘞)[\.!\?~～\s]*$",
]

def is_trivial_confirmation(text: str) -> bool:
    text = text.strip()
    return any(re.match(pattern, text, re.IGNORECASE) for pattern in TRIVIAL_PATTERNS)

def slice_context_local(raw_text: str, timeout: int = 60) -> dict:
    """
    Sends raw, private text to local Ollama (Qwen) with strict JSON output constraint.
    Keeps raw text strictly offline. Returns structured minimal context.
    """
    if is_trivial_confirmation(raw_text):
        return {
            "type": "trivial",
            "action_needed": False,
            "summary": "",
            "todo": None
        }

    system_prompt = (
        "Output ONLY a valid JSON object. "
        'Schema: {"has_action_item": bool, "summary": "1 sentence brief without names", "action_description": "task or null", "is_urgent": bool}'
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\n\nInput Text:\n{raw_text}\n\nJSON:",
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1,
            "num_predict": 128
        }
    }

    try:
        req = urllib.request.Request(
            OLLAMA_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            response_text = res_data.get("response", "").strip()
            return json.loads(response_text)
    except Exception as e:
        return {
            "error": str(e),
            "fallback": True,
            "raw_preview": raw_text[:50]
        }

if __name__ == "__main__":
    test_trivial = "好的"
    print("Trivial test:", is_trivial_confirmation(test_trivial))
    
    test_text = "周四前所有人把开题报告初稿发到邮箱，周五下午2点在信息楼301开例会。"
    print("Local Qwen Slicing test:", slice_context_local(test_text))
