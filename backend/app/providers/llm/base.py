from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def generate_recommendation(self, prompt: str) -> str:
        """Generate an AI-powered redistribution recommendation."""
        pass
