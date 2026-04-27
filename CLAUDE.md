# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the project

**Prerequisite**: Ollama must be running locally before executing the script.

```bash
ollama serve                  # start the local LLM server (must be accessible at http://localhost:11434)
pip install langchain-ollama  # only non-stdlib dependency
python main.py
```

## Architecture

The entire system lives in `main.py` and implements a multi-agent evaluation pipeline for French audit recommendations using LangChain.

**Data flow**:
1. A recommendation dict (required keys: `constat`, `recommandation`, `date_realisation`, `livrables`) is passed to `evaluate_recommendation()`.
2. `build_pipeline()` constructs a `RunnableParallel` that runs four specialist chains concurrently: `constat`, `coherence`, `delais`, `livrables`.
3. Each specialist chain is a `ChatPromptTemplate | ChatOllama.with_structured_output(Evaluation)` — output is a validated Pydantic `Evaluation` object (fields: `score: int`, `evaluation: str`).
4. The coordinator receives condensed summaries (score + first 300 chars per agent) and returns a `FinalEvaluation` Pydantic object with `score`, `points_forts`, `axes_amelioration`, `synthese`.
5. `pretty_print_results()` formats the output.

**Key design points**:
- `with_structured_output()` forces the LLM to return schema-validated JSON — no regex parsing. If the LLM fails to comply, LangChain raises an exception (no silent fallback).
- `RunnableParallel` handles concurrency internally (threadpool); no manual async/session management.
- Models are set via two constants: `SPECIALIST_MODEL = "llama3.2:latest"` and `COORDINATOR_MODEL = "qwen2.5:7b"`. Scores are not comparable across models.

**Language**: Prompts and output are in French.
