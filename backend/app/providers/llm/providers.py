import os
import httpx
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.url = "https://api.openai.com/v1/chat/completions"

    async def generate_recommendation(self, prompt: str) -> str:
        if not self.api_key:
            return "OpenAI API Key not configured."

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": "You are an engineering resource optimization expert."},
                         {"role": "user", "content": prompt}]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=payload, headers=headers)
            result = response.json()
            return result["choices"][0]["message"]["content"]

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.model = os.getenv("OLLAMA_MODEL", "gemma4:31b-cloud")
        self.url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "120"))

    async def generate_recommendation(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(f"{self.url}/api/generate", json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "No response from Ollama.")
            except httpx.TimeoutException:
                return f"Ollama request timed out after {self.timeout:g}s. Check that model '{self.model}' is loaded and responding."
            except httpx.HTTPStatusError as e:
                return f"Ollama returned HTTP {e.response.status_code}: {e.response.text}"
            except Exception as e:
                return f"Ollama connection error: {str(e)}"
