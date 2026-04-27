# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the project

**Prerequisite**: Ollama must be running locally before executing the script.

```bash
ollama serve          # start the local LLM server (must be accessible at http://localhost:11434)
pip install aiohttp   # only dependency beyond the stdlib
python main.py
```

## Architecture

The entire system lives in `main.py` and implements a multi-agent evaluation pipeline for French audit recommendations.

**Data flow**:
1. A recommendation dict (keys: `constat`, `recommandation`, `date_realisation`, `responsable`, `livrables`) is passed to `AgentNetwork.evaluate_recommendation()`.
2. Four specialist `AuditAgent` instances run **concurrently** via `asyncio.gather`: `constat`, `coherence`, `delais`, `livrables`.
3. Their results are fed to a fifth `coordinateur` agent that aggregates them into a global score.
4. `pretty_print_results()` formats the output.

**Key classes**:
- `AuditAgent` — wraps a single Ollama call. Each agent has a `system_prompt` baked in at construction time. `_parse_response` extracts a `score` using a `\d+/10` regex from free-text LLM output.
- `AgentNetwork` — owns a single shared `aiohttp.ClientSession` (passed to all agents), manages the parallel execution pattern, and must be closed with `await network.close()` to avoid resource leaks.

**LLM integration**: All agents call the same endpoint (`OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"`) with `stream=False` and a 30-second timeout. The model is `llama3.1` and can be changed via the `MODEL` constant.

**Language**: Prompts and output are in French.
