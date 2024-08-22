from abc import ABC, abstractmethod
from app.repositories.base import BaseAIRepository
from typing import AsyncGenerator, Optional

class BaseAIStrategy(ABC):
    @abstractmethod
    async def execute(self, repository: BaseAIRepository, prompt: str, model: str, max_tokens: int, parameters: dict) -> Optional[str]:
        pass

    @abstractmethod
    def stream(self, repository: BaseAIRepository, prompt: str, model: str, max_tokens: int, parameters: dict) -> AsyncGenerator[Optional[str], None]:
        pass
