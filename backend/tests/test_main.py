import asyncio
import shutil

import pytest
from fastapi import HTTPException

import app.main as main
from app.providers.data.jira import JiraMCPProvider, MockJiraProvider


def reset_provider():
    main.data_provider = None
    main.DATA_PATH = None


def test_resolve_mock_data_path_from_repo_root(repo_root, monkeypatch):
    monkeypatch.chdir(repo_root)
    monkeypatch.delenv("MOCK_DATA_PATH", raising=False)

    assert main.resolve_mock_data_path() == repo_root / "mock-data" / "sprint_data.json"


def test_resolve_mock_data_path_honors_env(repo_root, monkeypatch):
    expected = repo_root / "mock-data" / "sprint_data.json"
    monkeypatch.setenv("MOCK_DATA_PATH", str(expected))

    assert main.resolve_mock_data_path() == expected


@pytest.mark.asyncio
async def test_get_all_engineers_returns_load_results(repo_root, monkeypatch):
    reset_provider()
    monkeypatch.setenv("DATA_PROVIDER", "mock")
    monkeypatch.setenv("MOCK_DATA_PATH", str(repo_root / "mock-data" / "sprint_data.json"))

    results = await main.get_all_engineers()

    assert len(results) == 5
    assert {"engineer", "load"} == set(results[0])


def test_get_data_provider_rejects_unknown_provider(monkeypatch):
    reset_provider()
    monkeypatch.setenv("DATA_PROVIDER", "unknown")

    with pytest.raises(ValueError, match="Unsupported DATA_PROVIDER"):
        main.get_data_provider()


def test_apply_mock_optimization_updates_temp_json(repo_root, tmp_path):
    source = repo_root / "mock-data" / "sprint_data.json"
    temp_data = tmp_path / "sprint_data.json"
    shutil.copyfile(source, temp_data)

    main.DATA_PATH = temp_data
    main.data_provider = MockJiraProvider(temp_data)
    engineers = asyncio.run(main.get_engineers_or_503())

    action = main.apply_mock_optimization_if_enabled(engineers)
    updated = asyncio.run(main.get_engineers_or_503())

    assert action.startswith("Applied mock optimization:")
    assert len(updated) == len(engineers)
    assert sum(len(e.current_sprint.tickets) for e in updated) == sum(
        len(e.current_sprint.tickets) for e in engineers
    )


def test_apply_mock_optimization_skips_non_mock_provider(monkeypatch):
    monkeypatch.setenv("JIRA_MCP_URL", "http://localhost:3001/mcp")
    main.data_provider = JiraMCPProvider()

    action = main.apply_mock_optimization_if_enabled([])

    assert action == "No workload changes applied because DATA_PROVIDER is not mock."


def test_get_data_provider_or_503_wraps_configuration_error(monkeypatch):
    reset_provider()
    monkeypatch.setenv("DATA_PROVIDER", "jira_mcp")
    monkeypatch.delenv("JIRA_MCP_URL", raising=False)

    with pytest.raises(HTTPException) as error:
        main.get_data_provider_or_503()

    assert error.value.status_code == 503
    assert "JIRA_MCP_URL is required" in error.value.detail
