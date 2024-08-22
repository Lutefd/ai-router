from .base import BaseAIStrategy
from app.repositories.base import BaseAIRepository
from typing import AsyncGenerator, Optional

class OpenAIStrategy(BaseAIStrategy):
    async def execute(self, repository: BaseAIRepository, prompt: str, model: str, parameters: dict) -> Optional[str]:
        return await repository.generate_response(prompt, model, parameters)

    def stream(self, repository: BaseAIRepository, prompt: str, model: str, parameters: dict) -> AsyncGenerator[Optional[str], None]:
        return repository.stream_response(prompt, model, parameters)
