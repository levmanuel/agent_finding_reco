# Audit Recommendation Evaluation with Ollama

## 📌 Overview
This project uses multiple AI agents to evaluate audit recommendations by analyzing different aspects such as clarity, coherence, deadlines, and deliverables. It leverages the **Ollama** API with the **Llama 3.1** model to generate evaluations and scores.

## 🚀 Features
- **Multi-Agent Evaluation**: Specialized agents assess different aspects of an audit recommendation.
- **LLM Integration**: Uses Ollama's Llama 3.1 model for intelligent evaluation.
- **Async Processing**: Efficient execution using Python's `asyncio` and `aiohttp`.
- **Aggregated Final Score**: A coordinator agent summarizes and scores the recommendation.

## 🛠 Installation
### Prerequisites
- Python 3.8+
- Ollama running locally (ensure it is accessible at `http://localhost:11434`)
- Required Python libraries

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/levmanuel/agent_finding_reco.git
   cd agent_finding_reco
   ```
2. Install dependencies:
   ```bash
   pip install aiohttp
   ```
3. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

## 🏃 Usage
Run the script with:
```bash
python main.py
```
The program will analyze an audit recommendation and print the evaluation results.

## 📋 Example Input
```json
{
  "constat": "Les contrôles d'accès aux données sensibles ne sont pas documentés systématiquement, ce qui pourrait conduire à des accès non autorisés.",
  "recommandation": "Mettre en place une procédure formelle de documentation et de revue périodique des droits d'accès aux données sensibles.",
  "date_realisation": "2023-12-31",
  "responsable": "Département Sécurité IT",
  "livrables": [
    "Procédure documentée de gestion des droits d'accès",
    "Tableau de suivi des revues trimestrielles",
    "Rapport d'audit interne validant l'implémentation"
  ]
}
```

## 📊 Output Example
```
🔎 **Évaluation de la Recommandation** 🔍

📌 Constat : Les contrôles d'accès aux données sensibles ne sont pas documentés systématiquement...

✅ Recommandation : Mettre en place une procédure formelle...

📊 **Scores des agents** :
  - Constat : 8/10 - Bonne clarté et pertinence.
  - Coherence : 7/10 - Alignement correct avec le constat.
  - Delais : 6/10 - Délais potentiellement trop longs.
  - Livrables : 9/10 - Livrables bien définis.

📢 **Évaluation finale** : Score global 7.5/10. Quelques points d'amélioration sur les délais.
```

## 🛠 Troubleshooting
- If you get **"Erreur: Temps de réponse dépassé"**, ensure Ollama is running and accessible.
- If responses are empty, check Ollama logs for issues.
- Use `asyncio.run(main())` only once in the script to avoid runtime errors.

## 🏗 Future Improvements
- Add more detailed prompt engineering.
- Enable external API configuration.
- Implement caching for frequent queries.
