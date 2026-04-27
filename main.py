import json
from typing import Any, Dict

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableLambda
from pydantic import BaseModel, Field

SPECIALIST_MODEL = "llama3.2:latest"
COORDINATOR_MODEL = "qwen2.5:7b"
REQUIRED_FIELDS = ["constat", "recommandation", "date_realisation", "livrables"]

SPECIALIST_PROMPTS = {
    "constat": (
        "Évaluez la clarté et la pertinence du constat d'audit. "
        "Un bon constat doit être factuel, précis et basé sur des preuves."
    ),
    "coherence": (
        "Vérifiez la cohérence entre le constat identifié et la recommandation proposée."
    ),
    "delais": (
        "Analysez si la date de réalisation est réaliste et proportionnée "
        "à la complexité de la recommandation."
    ),
    "livrables": (
        "Évaluez si les livrables sont clairement définis, mesurables et suffisants "
        "pour vérifier l'implémentation de la recommandation."
    ),
}

COORDINATOR_PROMPT = (
    "Agrégez les évaluations des agents spécialisés et produisez une synthèse globale. "
    "Identifiez les points forts et les axes d'amélioration."
)


class Evaluation(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Score de 0 à 10")
    evaluation: str = Field(..., description="Évaluation détaillée")


class FinalEvaluation(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Score global de 0 à 10")
    points_forts: list[str] = Field(..., description="Points forts de la recommandation")
    axes_amelioration: list[str] = Field(..., description="Axes d'amélioration")
    synthese: str = Field(..., description="Synthèse globale")


def make_specialist_chain(system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Données à évaluer:\n{data}"),
    ])
    llm = ChatOllama(model=SPECIALIST_MODEL).with_structured_output(Evaluation)
    return prompt | llm


def build_pipeline():
    specialists = RunnableParallel(**{
        key: make_specialist_chain(prompt)
        for key, prompt in SPECIALIST_PROMPTS.items()
    })

    coordinator_prompt = ChatPromptTemplate.from_messages([
        ("system", COORDINATOR_PROMPT),
        ("human", "Recommandation originale:\n{data}\n\nÉvaluations des agents:\n{evaluations}"),
    ])
    coordinator_llm = ChatOllama(model=COORDINATOR_MODEL).with_structured_output(FinalEvaluation)

    def run_coordinator(inputs: dict) -> dict:
        evaluations = "\n".join(
            f"- {key}: {result.score}/10 — {result.evaluation[:300]}"
            for key, result in inputs["specialist_results"].items()
        )
        final = (coordinator_prompt | coordinator_llm).invoke({
            "data": inputs["data"],
            "evaluations": evaluations,
        })
        return {"specialist_results": inputs["specialist_results"], "final_evaluation": final}

    def pipeline(data_str: str) -> dict:
        specialist_results = specialists.invoke({"data": data_str})
        return run_coordinator({"data": data_str, "specialist_results": specialist_results})

    return pipeline


def evaluate_recommendation(data: Dict[str, Any]) -> Dict[str, Any]:
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        return {"error": f"Champs manquants: {', '.join(missing)}"}

    pipeline = build_pipeline()
    results = pipeline(json.dumps(data, indent=2, ensure_ascii=False))
    return {"recommendation": data, **results}


def pretty_print_results(results: Dict[str, Any]) -> None:
    if "error" in results:
        print(f"\n❌ Erreur : {results['error']}")
        return

    reco = results["recommendation"]
    print("\n🔎 **Évaluation de la Recommandation** 🔍")
    print(f"\n📌 Constat : {reco['constat']}")
    print(f"\n✅ Recommandation : {reco['recommandation']}")

    print("\n📊 **Scores des agents** :")
    for key, eval_data in results["specialist_results"].items():
        print(f"  - {key.capitalize()} : {eval_data.score}/10 — {eval_data.evaluation[:120]}")

    final = results["final_evaluation"]
    print(f"\n📢 **Évaluation finale** : {final.score}/10")
    print("\n✅ Points forts :")
    for point in final.points_forts:
        print(f"  • {point}")
    print("\n⚠️  Axes d'amélioration :")
    for axe in final.axes_amelioration:
        print(f"  • {axe}")
    print(f"\n{final.synthese}")


if __name__ == "__main__":
    recommendation = {
        "constat": (
            "Les contrôles d'accès aux données sensibles ne sont pas documentés systématiquement, "
            "ce qui pourrait conduire à des accès non autorisés."
        ),
        "recommandation": (
            "Mettre en place une procédure formelle de documentation et de revue périodique "
            "des droits d'accès aux données sensibles."
        ),
        "date_realisation": "2023-12-31",
        "responsable": "Département Sécurité IT",
        "livrables": [
            "Procédure documentée de gestion des droits d'accès",
            "Tableau de suivi des revues trimestrielles",
            "Rapport d'audit interne validant l'implémentation",
        ],
    }

    results = evaluate_recommendation(recommendation)
    pretty_print_results(results)
