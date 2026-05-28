import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .core.scoring import calculate_cognitive_load
from .providers.data.base import SprintsDataProvider
from .providers.data.jira import JiraMCPProvider, MockJiraProvider
from .providers.llm.providers import OpenAIProvider, OllamaProvider, LLMProvider

app = FastAPI(title="Cognitive Load Management System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "mock-data/sprint_data.json"
data_provider: SprintsDataProvider | None = None

def get_data_provider() -> SprintsDataProvider:
    global data_provider
    if data_provider is not None:
        return data_provider

    provider = os.getenv("DATA_PROVIDER", "mock").lower()
    if provider == "jira_mcp":
        data_provider = JiraMCPProvider()
    elif provider == "mock":
        data_provider = MockJiraProvider(DATA_PATH)
    else:
        raise ValueError(f"Unsupported DATA_PROVIDER: {provider}")
    return data_provider

def get_llm_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        return OpenAIProvider()
    return OllamaProvider()

@app.get("/api/engineers", response_model=List[dict])
async def get_all_engineers():
    engineers = await get_engineers_or_503()
    return build_engineer_results(engineers)

@app.get("/api/engineers/{engineer_id}")
async def get_engineer(engineer_id: str):
    provider = get_data_provider_or_503()
    try:
        eng = await provider.get_engineer_by_id(engineer_id)
        load = calculate_cognitive_load(eng)
        return {"engineer": eng, "load": load}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Data provider unavailable: {e}")

@app.post("/api/recommendations")
async def get_recommendations():
    engineers = await get_engineers_or_503()
    llm = get_llm_provider()

    # Prepare a summary for the AI
    summary = []
    for eng in engineers:
        load = calculate_cognitive_load(eng)
        summary.append(f"{eng.name} ({eng.role}): Score {load.score}, Status {load.status}")

    prompt = f"The following is the current cognitive load of an engineering team:\n\n" + "\n".join(summary) + \
             "\n\nBased on this, provide 3 specific, actionable recommendations to redistribute work and reduce burnout risk."

    try:
        recommendation = await llm.generate_recommendation(prompt)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"LLM provider unavailable: {e}")

    applied_action = apply_mock_optimization_if_enabled(engineers)
    updated_engineers = await get_engineers_or_503()

    return {
        "recommendations": recommendation,
        "applied_action": applied_action,
        "engineers": build_engineer_results(updated_engineers),
    }

@app.post("/api/simulate/incident")
async def simulate_incident():
    provider = get_data_provider_or_503()
    if not isinstance(provider, MockJiraProvider):
        raise HTTPException(
            status_code=409,
            detail="Incident simulation is only available when DATA_PROVIDER=mock",
        )

    # Simple simulation: Add an incident to a random engineer
    engineers = await get_engineers_or_503()
    # For demo purposes, we'll just update the JSON file
    # In a real app, this would be a DB update
    import random
    target = random.choice(engineers)

    with open(DATA_PATH, 'r+') as f:
        data = json.load(f)
        for eng in data:
            if eng['id'] == target.id:
                eng['current_sprint']['active_incidents'] += 1
                break
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    return {"message": f"Incident spike simulated for {target.name}"}

async def get_engineers_or_503():
    try:
        return await get_data_provider_or_503().get_engineers()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Data provider unavailable: {e}")

def get_data_provider_or_503() -> SprintsDataProvider:
    try:
        return get_data_provider()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Data provider unavailable: {e}")

def build_engineer_results(engineers):
    results = []
    for eng in engineers:
        load = calculate_cognitive_load(eng)
        results.append({
            "engineer": eng,
            "load": load
        })
    return results

def apply_mock_optimization_if_enabled(engineers):
    provider = get_data_provider_or_503()
    if not isinstance(provider, MockJiraProvider):
        return "No workload changes applied because DATA_PROVIDER is not mock."

    ranked = sorted(
        [(eng, calculate_cognitive_load(eng)) for eng in engineers],
        key=lambda item: item[1].score,
        reverse=True,
    )

    overloaded = next((eng for eng, load in ranked if load.score >= 66), None)
    available = next(
        (
            eng for eng, load in reversed(ranked)
            if overloaded and eng.id != overloaded.id and load.score < 81
        ),
        None,
    )

    if not overloaded or not available:
        return "No mock workload change applied because the team is already balanced."

    with open(DATA_PATH, 'r+') as f:
        data = json.load(f)
        source = next(eng for eng in data if eng["id"] == overloaded.id)
        target = next(eng for eng in data if eng["id"] == available.id)
        movable_ticket = next(
            (
                ticket for ticket in reversed(source["current_sprint"]["tickets"])
                if ticket.get("status") != "in-progress"
            ),
            None,
        )

        changes = []
        if movable_ticket:
            source["current_sprint"]["tickets"].remove(movable_ticket)
            target["current_sprint"]["tickets"].append(movable_ticket)
            changes.append(
                f"moved {movable_ticket['id']} from {source['name']} to {target['name']}"
            )

        incident_delta = min(2, source["current_sprint"].get("active_incidents", 0))
        if incident_delta:
            source["current_sprint"]["active_incidents"] -= incident_delta
            target["current_sprint"]["active_incidents"] += 1
            changes.append(
                f"shifted {incident_delta} incident(s) away from {source['name']}"
            )

        dependency_delta = min(1, source["current_sprint"].get("cross_team_dependencies", 0))
        if dependency_delta:
            source["current_sprint"]["cross_team_dependencies"] -= dependency_delta
            changes.append(f"reduced one cross-team dependency for {source['name']}")

        if not changes:
            return "No movable mock workload was found to apply."

        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    return "Applied mock optimization: " + "; ".join(changes) + "."
