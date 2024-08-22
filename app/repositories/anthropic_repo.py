import logging
import anthropic
from anthropic import AsyncAnthropic
from .base import BaseAIRepository
from app.config import config
from app.exceptions import AIGenerationException, ModelNotFoundException
from typing import AsyncGenerator, Dict, Any

logger = logging.getLogger(__name__)

class AnthropicRepository(BaseAIRepository):
    def __init__(self):
        self.client = AsyncAnthropic(api_key=config.anthropic_api_key)

    async def generate_response(self, prompt: str, model: str, max_tokens:int, parameters: Dict[str, Any]) -> str:
        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **parameters
            )
            return response.content[0].text
        except anthropic.APIError as e:
            logger.error(f"Error generating response from Anthropic: {e}")
            if "model not found" in str(e).lower():
                raise ModelNotFoundException(f"Model '{model}' not found for Anthropic")
            raise AIGenerationException(f"Failed to generate response from Anthropic: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating response from Anthropic: {e}")
            raise AIGenerationException(f"Unexpected error generating response from Anthropic: {e}")

    async def stream_response(self, prompt: str, model: str, max_tokens:int, parameters: Dict[str, Any]) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True,
                **parameters
            )
            async for chunk in stream:
                logger.debug(f"Received chunk: {chunk}")
                text = self._extract_text_from_chunk(chunk)
                if text:
                    yield text
        except anthropic.APIError as e:
            logger.error(f"Error streaming response from Anthropic: {e}")
            if "model not found" in str(e).lower():
                raise ModelNotFoundException(f"Model '{model}' not found for Anthropic")
            raise AIGenerationException(f"Failed to stream response from Anthropic: {e}")
        except Exception as e:
            logger.error(f"Unexpected error streaming response from Anthropic: {e}")
            raise AIGenerationException(f"Unexpected error streaming response from Anthropic: {e}")

    def _extract_text_from_chunk(self, chunk: Any) -> str:
        if hasattr(chunk, 'delta'):
            return getattr(chunk.delta, 'text', '')
        elif hasattr(chunk, 'message'):
            if hasattr(chunk.message, 'content'):
                for content in chunk.message.content:
                    if getattr(content, 'type', None) == 'text':
                        return getattr(content, 'text', '')
        elif hasattr(chunk, 'content'):
            if isinstance(chunk.content, list):
                for content in chunk.content:
                    if getattr(content, 'type', None) == 'text':
                        return getattr(content, 'text', '')
            elif isinstance(chunk.content, str):
                return chunk.content

        logger.warning(f"Could not extract text from chunk: {chunk}")
        return ''
