import httpx
import pytest

from app.providers.llm.providers import OllamaProvider, OpenAIProvider


@pytest.mark.asyncio
async def test_openai_provider_returns_configuration_message_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = await OpenAIProvider().generate_recommendation("balance team load")

    assert result == "OpenAI API Key not configured."


@pytest.mark.asyncio
async def test_openai_provider_posts_chat_completion(monkeypatch):
    captured = {}

    class FakeResponse:
        def json(self):
            return {
                "choices": [
                    {"message": {"content": "Move one ticket away from Sarah."}}
                ]
            }

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, json, headers):
            captured["url"] = url
            captured["json"] = json
            captured["headers"] = headers
            return FakeResponse()

    monkeypatch.setenv("OPENAI_API_KEY", "test-token")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")
    monkeypatch.setattr("app.providers.llm.providers.httpx.AsyncClient", lambda: FakeAsyncClient())

    result = await OpenAIProvider().generate_recommendation("prompt")

    assert result == "Move one ticket away from Sarah."
    assert captured["json"]["model"] == "gpt-test"
    assert captured["headers"]["Authorization"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_ollama_provider_returns_response(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"response": "Redistribute incident ownership."}

    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, json):
            assert url == "http://ollama.test/api/generate"
            assert json["stream"] is False
            return FakeResponse()

    monkeypatch.setenv("OLLAMA_URL", "http://ollama.test")
    monkeypatch.setenv("OLLAMA_MODEL", "gemma-test")
    monkeypatch.setattr("app.providers.llm.providers.httpx.AsyncClient", FakeAsyncClient)

    result = await OllamaProvider().generate_recommendation("prompt")

    assert result == "Redistribute incident ownership."


@pytest.mark.asyncio
async def test_ollama_provider_handles_timeout(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, json):
            raise httpx.TimeoutException("slow")

    monkeypatch.setenv("OLLAMA_MODEL", "gemma-test")
    monkeypatch.setenv("OLLAMA_TIMEOUT_SECONDS", "3")
    monkeypatch.setattr("app.providers.llm.providers.httpx.AsyncClient", FakeAsyncClient)

    result = await OllamaProvider().generate_recommendation("prompt")

    assert result == "Ollama request timed out after 3s. Check that model 'gemma-test' is loaded and responding."


@pytest.mark.asyncio
async def test_ollama_provider_handles_connection_error(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, timeout):
            self.timeout = timeout

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, json):
            raise RuntimeError("connection refused")

    monkeypatch.setattr("app.providers.llm.providers.httpx.AsyncClient", FakeAsyncClient)

    result = await OllamaProvider().generate_recommendation("prompt")

    assert result == "Ollama connection error: connection refused"
