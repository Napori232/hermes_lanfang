---
name: local-model-routing
description: "Use when routing simple tasks to local Ollama model."
version: 1.0.0
---

# Local Model Routing (Ollama qwen3:8b)

Hermes uses the local Ollama instance (`http://localhost:11434/v1`, model `qwen3:8b`) for low-cost, high-privacy, and simple tasks.

## Responsibilities
- Simple Q&A and greeting
- Classification and filtering
- Message and text summarization
- TODO extraction from conversation
- Local privacy-sensitive text formatting

## Invocation Pattern
Hermes can call the local Ollama endpoint via HTTP API (`/v1/chat/completions`) or internal subagent/delegation when handling low-complexity offline workloads.
