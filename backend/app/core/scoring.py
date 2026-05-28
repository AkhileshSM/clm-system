from typing import Dict
from ..models.schemas import Engineer, CognitiveLoadResult

# Configurable thresholds and weights
WEIGHTS = {
    "active_tickets": 0.20,
    "high_priority": 0.20,
    "context_switching": 0.15,
    "dependencies": 0.15,
    "repo_ownership": 0.10,
    "prod_support": 0.10,
    "active_incidents": 0.10,
}

MAX_VALUES = {
    "active_tickets": 10,
    "high_priority": 5,
    "dependencies": 5,
    "repo_ownership": 15,
    "active_incidents": 5,
}

THRESHOLDS = {
    "burnout": 81,
    "high": 66,
    "elevated": 41,
}

def calculate_cognitive_load(engineer: Engineer) -> CognitiveLoadResult:
    sprint = engineer.current_sprint
    struct = engineer.structural_load

    # Calculate normalized scores (0-100)
    active_tickets_score = (len(sprint.tickets) / MAX_VALUES["active_tickets"]) * 100

    high_priority_count = len([t for t in sprint.tickets if t.priority == "High"])
    high_priority_score = (high_priority_count / MAX_VALUES["high_priority"]) * 100

    context_switching_score = sprint.context_switching_factor * 100

    dependencies_score = (sprint.cross_team_dependencies / MAX_VALUES["dependencies"]) * 100

    repo_score = (struct.repos_owned / MAX_VALUES["repo_ownership"]) * 100

    prod_support_score = 100 if struct.prod_support_responsibility else 0

    incidents_score = (sprint.active_incidents / MAX_VALUES["active_incidents"]) * 100

    # Weighted average
    total_score = (
        (active_tickets_score * WEIGHTS["active_tickets"]) +
        (high_priority_score * WEIGHTS["high_priority"]) +
        (context_switching_score * WEIGHTS["context_switching"]) +
        (dependencies_score * WEIGHTS["dependencies"]) +
        (repo_score * WEIGHTS["repo_ownership"]) +
        (prod_support_score * WEIGHTS["prod_support"]) +
        (incidents_score * WEIGHTS["active_incidents"])
    )

    # Cap at 100
    total_score = min(100, total_score)

    # Determine status
    if total_score >= THRESHOLDS["burnout"]:
        status = "Burnout Risk"
    elif total_score >= THRESHOLDS["high"]:
        status = "High"
    elif total_score >= THRESHOLDS["elevated"]:
        status = "Elevated"
    else:
        status = "Normal"

    breakdown = {
        "active_tickets": active_tickets_score,
        "high_priority": high_priority_score,
        "context_switching": context_switching_score,
        "dependencies": dependencies_score,
        "repo_ownership": repo_score,
        "prod_support": prod_support_score,
        "active_incidents": incidents_score,
    }

    return CognitiveLoadResult(
        engineer_id=engineer.id,
        score=round(total_score, 2),
        status=status,
        breakdown=breakdown
    )
