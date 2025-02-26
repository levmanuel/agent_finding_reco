# 🚀 Audit Recommendation Evaluation System

Ce projet implémente un réseau d'agents spécialisés pour évaluer la qualité des recommandations d'audit en utilisant un modèle LLM via Ollama.

## 📌 Fonctionnalités
- Évaluation automatique des recommandations d'audit via plusieurs agents.
- Utilisation d'Ollama pour générer des scores et des analyses détaillées.
- Agrégation des évaluations individuelles en une analyse globale.

## 🛠️ Installation et Prérequis

### 1️⃣ Installer Ollama
Assurez-vous que Ollama est installé et lancé sur votre machine :
```sh
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

### 2️⃣ Installer les dépendances Python
```sh
pip install aiohttp
```

### 3️⃣ Vérifier le bon fonctionnement d'Ollama
Testez l'API avec :
```sh
curl -X POST http://localhost:11434/api/generate -d '{"model": "mistral", "prompt": "Test"}'
```
Si la réponse est vide ou affiche une erreur, assurez-vous qu'Ollama est bien lancé.

## 📂 Structure du projet
```
📁 audit-system
│── 📄 main.py          # Script principal
│── 📄 agents.py        # Définition des agents d'évaluation
│── 📄 README.md        # Documentation
```

## 🚀 Utilisation
Exécutez le programme avec :
```sh
python main.py
```
Le système évaluera une recommandation d'audit et affichera les résultats.

## ⚠️ Problèmes courants et solutions
- **Temps de réponse dépassé ?**
  - Vérifiez que Ollama tourne avec `ollama serve`
  - Augmentez le timeout dans `aiohttp`
  - Testez avec un modèle plus léger (`mistral` au lieu de `llama3.1`)

- **Erreur de connexion ?**
  - Vérifiez que l'API est accessible avec `curl`

## 📝 Exemples de sortie
Le programme retourne une évaluation sous forme JSON :
```json
{
  "recommendation": { "constat": "...", "recommandation": "..." },
  "agent_evaluations": {
    "constat": { "evaluation": "...", "score": 8 },
    "coherence": { "evaluation": "...", "score": 9 }
  },
  "final_evaluation": { "evaluation": "Résumé final", "score": 8.5 }
}
```
