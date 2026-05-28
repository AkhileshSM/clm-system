import shutil

import pytest

from app.providers.data.jira import MockJiraProvider


@pytest.mark.asyncio
async def test_mock_jira_provider_loads_engineers(repo_root):
    provider = MockJiraProvider(repo_root / "mock-data" / "sprint_data.json")

    engineers = await provider.get_engineers()

    assert len(engineers) == 5
    assert engineers[0].name == "Sarah Chen"


@pytest.mark.asyncio
async def test_mock_jira_provider_fetches_engineer_by_id(repo_root):
    provider = MockJiraProvider(repo_root / "mock-data" / "sprint_data.json")

    engineer = await provider.get_engineer_by_id("eng-3")

    assert engineer.name == "Alex Rivera"


@pytest.mark.asyncio
async def test_mock_jira_provider_raises_for_missing_engineer(repo_root):
    provider = MockJiraProvider(repo_root / "mock-data" / "sprint_data.json")

    with pytest.raises(ValueError, match="Engineer missing not found"):
        await provider.get_engineer_by_id("missing")


def test_mock_data_copy_is_valid_json(repo_root, tmp_path):
    target = tmp_path / "sprint_data.json"
    shutil.copyfile(repo_root / "mock-data" / "sprint_data.json", target)

    assert target.read_text().startswith("[")
