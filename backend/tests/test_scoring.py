from app.core.scoring import calculate_cognitive_load
from app.models.schemas import CurrentSprint, Engineer, SprintHistory, StructuralLoad, Ticket


def make_engineer(**overrides):
    engineer = Engineer(
        id="eng-test",
        name="Test Engineer",
        role="Backend Engineer",
        team="Platform",
        current_sprint=CurrentSprint(
            tickets=[
                Ticket(id="T-1", title="High priority work", priority="High", points=5, status="todo"),
                Ticket(id="T-2", title="Medium priority work", priority="Medium", points=3, status="todo"),
            ],
            active_incidents=1,
            cross_team_dependencies=1,
            meetings_load_hours=4,
            context_switching_factor=0.2,
        ),
        structural_load=StructuralLoad(
            repos_owned=2,
            prod_support_responsibility=False,
            shared_services_ownership=[],
            architectural_review_load="Low",
        ),
        history=[SprintHistory(sprint="S1", final_score=30)],
    )

    for key, value in overrides.items():
        setattr(engineer, key, value)

    return engineer


def test_calculate_cognitive_load_returns_expected_normal_score():
    result = calculate_cognitive_load(make_engineer())

    assert result.engineer_id == "eng-test"
    assert result.status == "Normal"
    assert result.score == 17.33
    assert result.breakdown["high_priority"] == 20.0


def test_calculate_cognitive_load_caps_score_at_100():
    engineer = make_engineer(
        current_sprint=CurrentSprint(
            tickets=[
                Ticket(id=f"T-{index}", title="Critical work", priority="High", points=8, status="todo")
                for index in range(20)
            ],
            active_incidents=20,
            cross_team_dependencies=10,
            meetings_load_hours=20,
            context_switching_factor=1.0,
        ),
        structural_load=StructuralLoad(
            repos_owned=30,
            prod_support_responsibility=True,
            shared_services_ownership=["Auth", "Payments"],
            architectural_review_load="High",
        ),
    )

    result = calculate_cognitive_load(engineer)

    assert result.score == 100
    assert result.status == "Burnout Risk"
