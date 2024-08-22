from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any, Optional

class BaseAIRepository(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, model: str, max_tokens: int, parameters: dict) -> Optional[str]:
        pass

    @abstractmethod
    def stream_response(self, prompt: str, model: str, max_tokens: int, parameters: dict) -> AsyncGenerator[Optional[str], None]:
        pass
