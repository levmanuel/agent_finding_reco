# Audit Recommendation Evaluation with Ollama & LangChain

## Overview
Multi-agent pipeline that evaluates French audit recommendations across four dimensions (clarity, coherence, deadlines, deliverables) using local LLMs via Ollama. Specialist agents run in parallel; a coordinator aggregates their structured outputs into a final scored synthesis.

## Features
- **Multi-agent evaluation**: four specialist agents assess one dimension each, a coordinator synthesizes
- **Structured output**: scores and evaluations are Pydantic-validated — no regex parsing
- **Two-speed model routing**: fast model (`llama3.2`) for parallel specialists, capable model (`qwen2.5`) for the coordinator
- **LangChain orchestration**: `RunnableParallel` for concurrency, `with_structured_output` for reliable JSON extraction

## Installation

**Prerequisites**: Python 3.10+, Ollama running locally at `http://localhost:11434`

```bash
git clone https://github.com/levmanuel/agent_finding_reco.git
cd agent_finding_reco
pip install langchain-ollama
ollama pull llama3.2
ollama pull qwen2.5
ollama serve
```

## Usage

```bash
python main.py
```

To evaluate a different recommendation, edit the `recommendation` dict in `main()` or call `evaluate_recommendation(data)` directly from your own code.

**Required fields**: `constat`, `recommandation`, `date_realisation`, `livrables`

## Example Input

```json
{
  "constat": "Les contrôles d'accès aux données sensibles ne sont pas documentés systématiquement, ce qui pourrait conduire à des accès non autorisés.",
  "recommandation": "Mettre en place une procédure formelle de documentation et de revue périodique des droits d'accès aux données sensibles.",
  "date_realisation": "2025-12-31",
  "responsable": "Département Sécurité IT",
  "livrables": [
    "Procédure documentée de gestion des droits d'accès",
    "Tableau de suivi des revues trimestrielles",
    "Rapport d'audit interne validant l'implémentation"
  ]
}
```

## Example Output

```
🔎 **Évaluation de la Recommandation** 🔍

📌 Constat : Les contrôles d'accès aux données sensibles...

✅ Recommandation : Mettre en place une procédure formelle...

📊 **Scores des agents** :
  - Constat : 6/10 — Faible à modéré
  - Coherence : 6/10 — L'évaluation est partielle car le constat est vague...
  - Delais : 5/10 — La date de réalisation laisse un temps relativement long...
  - Livrables : 8/10 — Les livrables sont clairement définis...

📢 **Évaluation finale** : 6/10

✅ Points forts :
  • Les livrables proposés sont clairs et précis.
  • La recommandation est pertinente et répond directement au constat.

⚠️  Axes d'amélioration :
  • Le constat devrait être plus détaillé pour clarifier la gravité du problème.
  • Les délais doivent être raccourcis.
```

## Troubleshooting
- **LLM raises a validation error**: the model failed to return valid JSON — retry or switch to a more capable model via `SPECIALIST_MODEL` / `COORDINATOR_MODEL` constants in `main.py`
- **Ollama not reachable**: ensure `ollama serve` is running and the model is pulled (`ollama pull <model>`)
- **Scores vary between runs**: LLM output is non-deterministic; scores are also not comparable across different models
