import logging
from app.repositories.openai_repo import OpenAIRepository
from app.repositories.anthropic_repo import AnthropicRepository
from app.strategies.openai_strategy import OpenAIStrategy
from app.strategies.anthropic_strategy import AnthropicStrategy
from app.config import config
from app.exceptions import ProviderNotFoundException, ModelNotFoundException
from typing import AsyncGenerator, Optional, Dict, Any

logger = logging.getLogger(__name__)

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

    def _validate_input(self, provider: str, model: Optional[str] = None) -> None:
        if provider not in self.repositories:
            raise ProviderNotFoundException(f"Unsupported provider: {provider}")

        if model is None:
            model = config.get_default_model(provider)
            if model is None:
                raise ModelNotFoundException(f"No default model configured for provider: {provider}")


    async def route_request(self, provider: str, prompt: str, model: Optional[str] = None, max_tokens: Optional[int] = None, parameters: Optional[Dict[str, Any]] = None) -> str:
        self._validate_input(provider, model)

        if model is None:
            model = config.get_default_model(provider)
        if max_tokens is None:
            max_tokens = config.get_default_max_tokens(provider)
        if max_tokens == 0:
            max_tokens = 1000
        if parameters is None:
            parameters = {}

        repository = self.repositories[provider]
        strategy = self.strategies[provider]

        logger.info(f"Routing request to {provider} using model {model}")
        return await strategy.execute(repository, prompt, model, max_tokens, parameters)

    async def stream_request(self, provider: str, prompt: str, model: Optional[str] = None, max_tokens: Optional[int] = None, parameters: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        self._validate_input(provider, model)

        if model is None:
            model = config.get_default_model(provider)

        if parameters is None:
            parameters = {}

        if max_tokens is None:
            max_tokens = config.get_default_max_tokens(provider)

        repository = self.repositories[provider]
        strategy = self.strategies[provider]

        logger.info(f"Streaming request to {provider} using model {model}")
        async for chunk in strategy.stream(repository, prompt, model, max_tokens, parameters):
            yield chunk
