"""
LLM Request Adapter with Automatic Stream-to-NonStream Fallback
Supports OpenAI-compatible / Gemini-compatible API endpoints.
Attempts streaming first; automatically falls back to non-streaming if upstream stream breaks, drops, or returns empty response.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Generator, Dict, Any, Optional

def chat_completion_with_fallback(
    messages: list[Dict[str, str]],
    model: str,
    api_key: Optional[str] = None,
    base_url: str = "https://api.openai.com/v1",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    timeout: int = 60,
    on_stream_chunk: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Executes a chat completion request.
    1. Tries streaming mode (`stream: True`) first.
    2. If streaming yields no content, raises SSE decode error, or fails with network/gateway errors,
       gracefully falls back to non-streaming mode (`stream: False`).
    
    Returns:
        {
            "content": str,
            "mode_used": "stream" | "non_stream_fallback",
            "model": str,
            "finish_reason": str,
            "error": Optional[str]
        }
    """
    key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY", "")
    endpoint = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }

    base_payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens:
        base_payload["max_tokens"] = max_tokens

    # --- 阶段 1: 尝试流式模式 (Streaming) ---
    stream_payload = dict(base_payload)
    stream_payload["stream"] = True

    stream_content_chunks = []
    stream_failed = False
    failure_reason = ""

    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(stream_payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                stream_failed = True
                failure_reason = f"HTTP {response.status}"
            else:
                for line in response:
                    line_str = line.decode("utf-8", errors="replace").strip()
                    if not line_str:
                        continue
                    if line_str == "data: [DONE]":
                        break
                    if line_str.startswith("data: "):
                        data_part = line_str[6:].strip()
                        try:
                            chunk_json = json.loads(data_part)
                            choices = chunk_json.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                text = delta.get("content", "")
                                if text:
                                    stream_content_chunks.append(text)
                                    if on_stream_chunk:
                                        on_stream_chunk(text)
                        except json.JSONDecodeError:
                            continue

        full_streamed_text = "".join(stream_content_chunks).strip()
        # 如果流式没有输出任何内容，判定为流式兼容异常/空流
        if full_streamed_text:
            return {
                "content": full_streamed_text,
                "mode_used": "stream",
                "model": model,
                "finish_reason": "stop",
                "error": None
            }
        else:
            stream_failed = True
            failure_reason = "Empty stream response or premature SSE termination"

    except Exception as e:
        stream_failed = True
        failure_reason = f"Stream request exception: {e}"

    # --- 阶段 2: 降级回退到非流式模式 (Non-Streaming Fallback) ---
    non_stream_payload = dict(base_payload)
    non_stream_payload["stream"] = False

    try:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(non_stream_payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            choices = res_data.get("choices", [])
            content = ""
            finish_reason = "stop"
            if choices:
                msg = choices[0].get("message", {})
                content = msg.get("content", "")
                finish_reason = choices[0].get("finish_reason", "stop")

            return {
                "content": content,
                "mode_used": "non_stream_fallback",
                "fallback_from_reason": failure_reason,
                "model": model,
                "finish_reason": finish_reason,
                "error": None
            }
    except Exception as e:
        return {
            "content": "",
            "mode_used": "failed",
            "model": model,
            "finish_reason": "error",
            "error": f"Both stream and non-stream fallback failed. Stream error: {failure_reason} | Non-stream error: {e}"
        }

if __name__ == "__main__":
    # 单元测试与接口可用性验证样例
    sample_messages = [
        {"role": "user", "content": "你好，请输出一个'OK'确认测试。"}
    ]
    print("[Test] Initializing Chat Stream Fallback Runner...")
    # 可直接接入业务调用：
    # res = chat_completion_with_fallback(sample_messages, model="gpt-4o-mini")
    # print(f"Result: {res}")
