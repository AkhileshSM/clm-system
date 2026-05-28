# Cognitive Load Management (CLM) System

## Overview
The CLM system is an enterprise-grade observability platform for monitoring engineering cognitive load. It transforms raw workload data into a "saturation score," allowing leadership to detect burnout risks and optimize resource distribution.

## Core Philosophy
Organizations monitor infrastructure CPU and memory utilization with precision, but rarely monitor human cognitive utilization — despite it being equally critical to delivery quality, operational stability, and employee retention.

## Quick Start

### 1. Clone and Navigate
```bash
cd clm-system
```

### 2. Environment Setup
Copy the example `.env` file and configure your provider:
```bash
DATA_PROVIDER=mock

# For local LLM (requires Ollama)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3

# For Cloud LLM
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

To read real sprint data from a Jira MCP server, switch the data provider:
```bash
DATA_PROVIDER=jira_mcp
JIRA_MCP_URL=http://localhost:3001/mcp
JIRA_MCP_SPRINT_TOOL=jira_get_current_sprint
JIRA_MCP_ENGINEER_TOOL=jira_get_engineer_workload
```

See `docs/jira-mcp-integration.md` for the expected MCP tool contract.

### 3. Launch
To start the system with only the backend and frontend:
```bash
docker-compose up
```

To start with the local AI (Ollama) container:
```bash
docker-compose --profile ai up
```

## Key Features
- **Real-time Saturation Scoring**: Weighted metrics for tickets, incidents, and ownership.
- **AI-Powered Redistribution**: Automatic suggestions to balance load across the team.
- **Human Observability Dashboard**: High-contrast "DevOps" style UI for rapid risk detection.
- **Incident Simulation**: Trigger fake spikes to see the system react in real-time.

## Architecture
- **Backend**: Python FastAPI with a Provider pattern for data and AI.
- **Frontend**: React + TypeScript + Tailwind CSS + Recharts.
- **Data**: Mocked JIRA sprint data (ready for MCP integration).
