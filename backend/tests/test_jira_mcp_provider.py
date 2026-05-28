import json

import pytest

from app.providers.data.jira import JiraMCPProvider


def test_jira_mcp_provider_requires_url(monkeypatch):
    monkeypatch.delenv("JIRA_MCP_URL", raising=False)

    with pytest.raises(ValueError, match="JIRA_MCP_URL is required"):
        JiraMCPProvider()


def test_jira_mcp_provider_normalizes_jira_record():
    provider = JiraMCPProvider(server_url="http://mcp.test")

    engineer = provider._to_engineer({
        "assignee": {
            "accountId": "jira-123",
            "displayName": "Taylor Kim",
        },
        "team": "Platform",
        "issues": [
            {
                "key": "PLAT-1",
                "summary": "Fix deploy workflow",
                "priority": "High",
                "story_points": 5,
                "status": "todo",
            }
        ],
        "active_incidents": 2,
        "cross_team_dependencies": 1,
        "context_switching_factor": 0.4,
        "repos_owned": 3,
        "prod_support_responsibility": True,
        "shared_services_ownership": ["Deploy"],
    })

    assert engineer.id == "jira-123"
    assert engineer.name == "Taylor Kim"
    assert engineer.current_sprint.tickets[0].id == "PLAT-1"
    assert engineer.current_sprint.tickets[0].points == 5
    assert engineer.structural_load.prod_support_responsibility is True


def test_jira_mcp_provider_rejects_record_without_engineer_id():
    provider = JiraMCPProvider(server_url="http://mcp.test")

    with pytest.raises(ValueError, match="missing engineer id"):
        provider._to_engineer({"issues": []})


def test_jira_mcp_provider_extracts_supported_record_lists():
    provider = JiraMCPProvider(server_url="http://mcp.test")

    assert provider._extract_records([{"id": "eng-1"}]) == [{"id": "eng-1"}]
    assert provider._extract_records({"workloads": [{"id": "eng-2"}]}) == [{"id": "eng-2"}]
    assert provider._extract_records({"id": "eng-3"}) == [{"id": "eng-3"}]


def test_jira_mcp_provider_rejects_non_json_records():
    provider = JiraMCPProvider(server_url="http://mcp.test")

    with pytest.raises(ValueError, match="JSON object or array"):
        provider._extract_records("not-json")


@pytest.mark.asyncio
async def test_jira_mcp_provider_calls_tool_with_text_content(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({"engineers": [{"id": "eng-1"}]}),
                        }
                    ]
                }
            }

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, json):
            captured["url"] = url
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr("app.providers.data.jira.httpx.AsyncClient", FakeAsyncClient)
    provider = JiraMCPProvider(server_url="http://mcp.test")

    result = await provider._call_tool("jira_get_current_sprint", {})

    assert result == {"engineers": [{"id": "eng-1"}]}
    assert captured["url"] == "http://mcp.test"
    assert captured["json"]["method"] == "tools/call"


@pytest.mark.asyncio
async def test_jira_mcp_provider_raises_on_tool_error(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"error": {"message": "tool failed"}}

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, json):
            return FakeResponse()

    monkeypatch.setattr("app.providers.data.jira.httpx.AsyncClient", FakeAsyncClient)
    provider = JiraMCPProvider(server_url="http://mcp.test")

    with pytest.raises(RuntimeError, match="Jira MCP tool"):
        await provider._call_tool("jira_get_current_sprint", {})
