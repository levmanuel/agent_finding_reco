import os
import json
import re
import asyncio
import aiohttp
from aiohttp import ClientSession
from typing import Dict, Any

# Configuration Ollama
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL = "llama3.1"

class AuditAgent:
    def __init__(self, name: str, role: str, system_prompt: str, session: ClientSession):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.session = session  # Réutilisation de la session HTTP

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Traite les données d'entrée et renvoie une évaluation"""
        try:
            prompt = f"{self.system_prompt}\n\nDonnées à évaluer:\n{json.dumps(input_data, indent=2, ensure_ascii=False)}"
            response = await self._call_llm(prompt)
            return self._parse_response(response)
        except Exception as e:
            return {"agent": self.name, "error": f"Erreur lors du traitement: {str(e)}"}

    async def _call_llm(self, prompt: str) -> str:
        """Appel à l'API Ollama avec gestion des erreurs"""
        try:
            payload = {"model": MODEL, "prompt": prompt, "stream": False}
            async with self.session.post(OLLAMA_ENDPOINT, json=payload, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "Erreur: réponse vide")
                else:
                    return f"Erreur: API Ollama a retourné {response.status}"
        except aiohttp.ClientError as e:
            return f"Erreur réseau: {str(e)}"
        except asyncio.TimeoutError:
            return "Erreur: Temps de réponse dépassé"

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse la réponse du LLM en structure de données"""
        try:
            match = re.search(r"(\d+)/10", response)  # Recherche un score de 0 à 10
            score = int(match.group(1)) if match else None
            return {"agent": self.name, "evaluation": response, "score": score}
        except Exception as e:
            return {"agent": self.name, "evaluation": response, "error": f"Erreur de parsing: {str(e)}"}

class AgentNetwork:
    def __init__(self):
        self.session = ClientSession()  # Une seule session HTTP pour tous les agents
        self.agents = {
            "constat": AuditAgent("AnalyseConstat", "Analyste de Constat", 
                "Évaluez la clarté et la pertinence du constat d'audit. Un bon constat doit être factuel, précis et basé sur des preuves. Fournissez un score de 0 à 10.", self.session),
            "coherence": AuditAgent("EvaluationCoherence", "Évaluateur de Cohérence", 
                "Vérifiez la cohérence entre le constat identifié et la recommandation proposée. Fournissez un score de 0 à 10.", self.session),
            "delais": AuditAgent("VerificationDelais", "Vérificateur de Délais", 
                "Analysez la pertinence des dates de réalisation. Fournissez un score de 0 à 10.", self.session),
            "livrables": AuditAgent("ValidationLivrables", "Validateur de Livrables", 
                "Évaluez si les livrables sont clairement définis, mesurables et permettent de vérifier l'implémentation de la recommandation. Fournissez un score de 0 à 10.", self.session),
            "coordinateur": AuditAgent("Coordinateur", "Agent Coordinateur", 
                "Agrégez les évaluations des autres agents et produisez une évaluation globale. Fournissez un résumé clair et un score global de 0 à 10.", self.session)
        }

    async def evaluate_recommendation(self, recommendation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue une recommandation d'audit en utilisant tous les agents"""
        required_fields = ["constat", "recommandation", "date_realisation", "livrables"]
        missing = [field for field in required_fields if field not in recommendation_data]
        if missing:
            return {"error": f"Champs manquants: {', '.join(missing)}"}

        results = {}
        try:
            # Exécuter les agents spécialisés en parallèle
            tasks = [
                self.agents[agent_name].process(recommendation_data)
                for agent_name in self.agents if agent_name != "coordinateur"
            ]
            completed_tasks = await asyncio.gather(*tasks)
            for agent_name, result in zip([name for name in self.agents if name != "coordinateur"], completed_tasks):
                results[agent_name] = result
            
            # L'agent coordinateur agrège les résultats
            final_evaluation = await self.agents["coordinateur"].process({
                "recommendation": recommendation_data,
                "evaluations": results
            })
            
            return {
                "recommendation": recommendation_data,
                "agent_evaluations": results,
                "final_evaluation": final_evaluation
            }
        except Exception as e:
            return {"error": f"Évaluation échouée: {str(e)}"}

    async def close(self):
        """Ferme la session HTTP proprement"""
        await self.session.close()

def pretty_print_results(results: Dict[str, Any]):
    """Affichage lisible des résultats"""
    print("\n🔎 **Évaluation de la Recommandation** 🔍")
    print(f"\n📌 Constat : {results['recommendation']['constat']}")
    print(f"\n✅ Recommandation : {results['recommendation']['recommandation']}")
    
    print("\n📊 **Scores des agents** :")
    for agent, eval in results["agent_evaluations"].items():
        score = eval.get("score", "N/A")
        commentaire = eval["evaluation"]
        print(f"  - {agent.capitalize()} : {score}/10 - {commentaire}")

    print("\n📢 **Évaluation finale** :")
    print(results["final_evaluation"]["evaluation"])

# Exemple d'utilisation
async def main():
    recommendation = {
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

    network = AgentNetwork()
    try:
        evaluation_results = await network.evaluate_recommendation(recommendation)
        pretty_print_results(evaluation_results)
    finally:
        await network.close()  # Fermeture propre de la session HTTP

if __name__ == "__main__":
    asyncio.run(main())
