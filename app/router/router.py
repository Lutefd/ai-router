from app.repositories.openai_repo import OpenAIRepository
from app.repositories.anthropic_repo import AnthropicRepository
from app.strategies.openai_strategy import OpenAIStrategy
from app.strategies.anthropic_strategy import AnthropicStrategy
from app.config import config
from typing import AsyncGenerator, Optional, Dict, Any

class AIRouter:
    def __init__(self):
        self.repositories = {
            'openai': OpenAIRepository(),
            'anthropic': AnthropicRepository()
        }
        self.strategies = {
            'openai': OpenAIStrategy(),
            'anthropic': AnthropicStrategy()
        }

    async def route_request(self, provider: str, prompt: str, model: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        if provider not in self.repositories:
            raise ValueError(f"Unsupported provider: {provider}")

        if model is None:
            model = config.get_default_model(provider)

        if parameters is None:
            parameters = {}

        repository = self.repositories[provider]
        strategy = self.strategies[provider]

        return await strategy.execute(repository, prompt, model, parameters)

    def stream_request(self, provider: str, prompt: str, model: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None) -> AsyncGenerator[Optional[str], None]:
        if provider not in self.repositories:
            raise ValueError(f"Unsupported provider: {provider}")

        if model is None:
            model = config.get_default_model(provider)

        if parameters is None:
            parameters = {}

        repository = self.repositories[provider]
        strategy = self.strategies[provider]

        return strategy.stream(repository, prompt, model, parameters)
