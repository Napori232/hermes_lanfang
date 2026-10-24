---
name: local-model-routing
description: "Use when routing simple tasks to local Ollama; verify endpoint behavior first."
version: 1.1.0
---

# Local Model Routing (Ollama)

Use this skill when deciding whether or how to send a low-cost or privacy-sensitive task to a local Ollama model. Treat an alias in `config.yaml` as a selectable target, **not** as proof that Hermes automatically routes work to it.

## Procedure

1. **Inspect configuration without exposing credentials.** Confirm the default model/provider, model aliases, and any explicit routing rule. If no routing rule exists, report that local selection is manual; do not claim that simple tasks already use Ollama.
2. **Verify the service and model separately.** Check the Ollama version, installed model list, and loaded-model list. A listed model only proves installation, not successful inference.
3. **Probe the native Ollama API first.** Send a bounded, deterministic request to `/api/generate` or `/api/chat` with `stream:false`, a short exact-response prompt, a small output cap, and `think:false` when supported. Record elapsed time and the returned user-visible content.
4. **Probe the exact integration protocol separately.** If Hermes uses an OpenAI-compatible alias, test `/v1/chat/completions` in both streaming and non-streaming modes. Inspect `message.content` and any reasoning field independently.
5. **Choose the route from evidence.** Use the local endpoint only for bounded simple work when both the chosen protocol and visible output are reliable. Keep the remote default for complex work or when the compatibility path is unreliable. State whether the conclusion concerns the model, the native API, or the Hermes adapter.
6. **When duplicate messages are reported, separate layers before blaming the model.** Compare direct native and compatibility responses, inspect exact duplicate rows in the affected session store, then inspect compression/recovery and client logs. Prompt length or strict instructions can reduce answer quality, but they do not by themselves create duplicate persisted turns.

## Suitable Workloads

- Classification, filtering, and extraction with a fixed output shape
- Short local summaries and formatting of privacy-sensitive text
- Deterministic low-token transformations after a successful endpoint probe

## Decision Rules and Pitfalls

- **Do not route by alias name alone; aliases only map a provider endpoint and model, while routing requires an explicit rule or manual selection.**
- **Test native and OpenAI-compatible endpoints independently; Qwen-family reasoning can consume a completion budget while leaving `message.content` empty on a compatibility adapter.**
- **Disable thinking for bounded utility tasks when the endpoint supports it; otherwise hidden reasoning can dominate latency and token limits.**
- **Test stream and non-stream behavior independently; a valid HTTP completion does not guarantee that the client extracts visible text correctly.**
- **Do not diagnose duplicated output from prompt strictness alone; verify database duplication, retry/replay, compression recovery, and UI rendering in that order of evidence.**
- **Do not make a local model the global default from one successful native probe; validate the same protocol Hermes will actually invoke.**

## Reporting

Report four distinct facts: service availability, model installation, native inference result, and Hermes-compatible inference result. Do not collapse them into “the local model works.”

For optional reusable probes, see `scripts/stream_fallback_runner.py`.