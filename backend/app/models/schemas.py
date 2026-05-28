from pydantic import BaseModel, Field
from typing import List, Optional

class Ticket(BaseModel):
    id: str
    title: str
    priority: str
    points: int
    status: str

class CurrentSprint(BaseModel):
    tickets: List[Ticket]
    active_incidents: int
    cross_team_dependencies: int
    meetings_load_hours: int
    context_switching_factor: float

class StructuralLoad(BaseModel):
    repos_owned: int
    prod_support_responsibility: bool
    shared_services_ownership: List[str]
    architectural_review_load: str

class SprintHistory(BaseModel):
    sprint: str
    final_score: float

class Engineer(BaseModel):
    id: str
    name: str
    role: str
    team: str
    current_sprint: CurrentSprint
    structural_load: StructuralLoad
    history: List[SprintHistory]

class CognitiveLoadResult(BaseModel):
    engineer_id: str
    score: float
    status: str
    breakdown: dict
