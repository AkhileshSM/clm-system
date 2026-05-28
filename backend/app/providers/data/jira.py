import json
import os
from typing import Any, Dict, List

import httpx

from .base import SprintsDataProvider
from ...models.schemas import CurrentSprint, Engineer, SprintHistory, StructuralLoad, Ticket

class MockJiraProvider(SprintsDataProvider):
    def __init__(self, data_path: str):
        self.data_path = data_path

    async def _load_data(self) -> List[Engineer]:
        with open(self.data_path, 'r') as f:
            data = json.load(f)
            return [Engineer(**eng) for eng in data]

    async def get_engineers(self) -> List[Engineer]:
        return await self._load_data()

    async def get_engineer_by_id(self, engineer_id: str) -> Engineer:
        engineers = await self._load_data()
        for eng in engineers:
            if eng.id == engineer_id:
                return eng
        raise ValueError(f"Engineer {engineer_id} not found")

class JiraMCPProvider(SprintsDataProvider):
    """
    Data provider backed by a Jira MCP HTTP bridge.

    The MCP server is expected to expose tools that return either Engineer-shaped
    records directly or Jira issue records that can be normalized here.
    """
    def __init__(
        self,
        server_url: str | None = None,
        sprint_tool: str | None = None,
        engineer_tool: str | None = None,
        timeout_seconds: float = 15.0,
    ):
        self.server_url = (server_url or os.getenv("JIRA_MCP_URL", "")).rstrip("/")
        self.sprint_tool = sprint_tool or os.getenv("JIRA_MCP_SPRINT_TOOL", "jira_get_current_sprint")
        self.engineer_tool = engineer_tool or os.getenv("JIRA_MCP_ENGINEER_TOOL", "jira_get_engineer_workload")
        self.timeout_seconds = timeout_seconds

        if not self.server_url:
            raise ValueError("JIRA_MCP_URL is required when DATA_PROVIDER=jira_mcp")

    async def get_engineers(self) -> List[Engineer]:
        payload = await self._call_tool(self.sprint_tool, {})
        records = self._extract_records(payload)
        return [self._to_engineer(record) for record in records]

    async def get_engineer_by_id(self, engineer_id: str) -> Engineer:
        payload = await self._call_tool(self.engineer_tool, {"engineer_id": engineer_id})
        records = self._extract_records(payload)

        if isinstance(payload, dict) and payload.get("id"):
            return self._to_engineer(payload)

        for record in records:
            engineer = self._to_engineer(record)
            if engineer.id == engineer_id:
                return engineer

        raise ValueError(f"Engineer {engineer_id} not found")

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        request = {
            "jsonrpc": "2.0",
            "id": tool_name,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(self.server_url, json=request)
            response.raise_for_status()

        data = response.json()
        if "error" in data:
            raise RuntimeError(f"Jira MCP tool {tool_name} failed: {data['error']}")

        result = data.get("result", data)
        content = result.get("content") if isinstance(result, dict) else None
        if isinstance(content, list) and content:
            first = content[0]
            if isinstance(first, dict) and first.get("type") == "text":
                try:
                    return json.loads(first.get("text", ""))
                except json.JSONDecodeError:
                    return first.get("text")

        return result

    def _extract_records(self, payload: Any) -> List[Dict[str, Any]]:
        if isinstance(payload, list):
            return payload

        if not isinstance(payload, dict):
            raise ValueError("Jira MCP response must be a JSON object or array")

        for key in ("engineers", "assignees", "workloads", "issues"):
            value = payload.get(key)
            if isinstance(value, list):
                return value

        return [payload]

    def _to_engineer(self, record: Dict[str, Any]) -> Engineer:
        if "current_sprint" in record and "structural_load" in record:
            return Engineer(**record)

        assignee = record.get("assignee") or record.get("engineer") or {}
        engineer_id = str(record.get("id") or assignee.get("accountId") or assignee.get("emailAddress"))

        if not engineer_id or engineer_id == "None":
            raise ValueError("Jira MCP record is missing engineer id or assignee accountId")

        tickets = [
            Ticket(
                id=str(issue.get("id") or issue.get("key")),
                title=issue.get("title") or issue.get("summary") or "Untitled Jira issue",
                priority=issue.get("priority") or "Medium",
                points=int(issue.get("points") or issue.get("story_points") or 0),
                status=issue.get("status") or "Unknown",
            )
            for issue in record.get("tickets", record.get("issues", []))
        ]

        current_sprint = CurrentSprint(
            tickets=tickets,
            active_incidents=int(record.get("active_incidents", 0)),
            cross_team_dependencies=int(record.get("cross_team_dependencies", 0)),
            meetings_load_hours=int(record.get("meetings_load_hours", 0)),
            context_switching_factor=float(record.get("context_switching_factor", 0)),
        )

        structural_load = StructuralLoad(
            repos_owned=int(record.get("repos_owned", 0)),
            prod_support_responsibility=bool(record.get("prod_support_responsibility", False)),
            shared_services_ownership=record.get("shared_services_ownership", []),
            architectural_review_load=record.get("architectural_review_load", "Unknown"),
        )

        history = [
            SprintHistory(**item)
            for item in record.get("history", [])
        ]

        return Engineer(
            id=engineer_id,
            name=record.get("name") or assignee.get("displayName") or engineer_id,
            role=record.get("role", "Engineer"),
            team=record.get("team", "Unknown"),
            current_sprint=current_sprint,
            structural_load=structural_load,
            history=history,
        )
