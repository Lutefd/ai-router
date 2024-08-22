import logging
from openai import AsyncOpenAI
from .base import BaseAIRepository
from app.config import config
from app.exceptions import AIGenerationException, ModelNotFoundException
from typing import AsyncGenerator, Optional

logger = logging.getLogger(__name__)

class OpenAIRepository(BaseAIRepository):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.openai_api_key)

    async def generate_response(self, prompt: str, model: str, max_tokens:int, parameters: dict) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                **parameters
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {e}")
            if "model not found" in str(e).lower():
                raise ModelNotFoundException(f"Model '{model}' not found for OpenAI")
            raise AIGenerationException(f"Failed to generate response from OpenAI: {e}")

    async def stream_response(self, prompt: str, model: str, max_tokens:int, parameters: dict) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                stream=True,
                **parameters
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error streaming response from OpenAI: {e}")
            if "model not found" in str(e).lower():
                raise ModelNotFoundException(f"Model '{model}' not found for OpenAI")
            raise AIGenerationException(f"Failed to stream response from OpenAI: {e}")
