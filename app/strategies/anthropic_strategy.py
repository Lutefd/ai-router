from .base import BaseAIStrategy
from app.repositories.base import BaseAIRepository
from typing import AsyncGenerator, Optional

class AnthropicStrategy(BaseAIStrategy):
    async def execute(self, repository: BaseAIRepository, prompt: str, model: str, max_tokens: int, parameters: dict) -> Optional[str]:
        return await repository.generate_response(prompt, model, max_tokens, parameters)

    def stream(self, repository: BaseAIRepository, prompt: str, model: str, max_tokens:int, parameters: dict) -> AsyncGenerator[Optional[str], None]:
        return repository.stream_response(prompt, model, max_tokens, parameters)
