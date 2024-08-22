import anthropic
from .base import BaseAIRepository
from app.config import config
from typing import AsyncGenerator, Optional

class AnthropicRepository(BaseAIRepository):
    def __init__(self):
        self.client = anthropic.AsyncClient(api_key=config.anthropic_api_key)

    async def generate_response(self, prompt: str, model: str, parameters: dict) -> Optional[str]:
        try:
            response = await self.client.completions.create(
                model=model,
                prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                **parameters
            )
            return response.completion
        except Exception as e:
            print(f"Error generating response from Anthropic: {e}")
            return None

    def stream_response(self, prompt: str, model: str, parameters: dict) -> AsyncGenerator[Optional[str], None]:
        async def stream_generator():
            try:
                stream = await self.client.completions.create(
                    model=model,
                    prompt=f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}",
                    stream=True,
                    **parameters
                )
                async for chunk in stream:
                    if chunk.completion:
                        yield chunk.completion
            except Exception as e:
                print(f"Error streaming response from Anthropic: {e}")
                yield None

        return stream_generator()
