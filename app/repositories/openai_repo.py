from openai import AsyncOpenAI
from .base import BaseAIRepository
from app.config import config
from typing import AsyncGenerator, Optional

class OpenAIRepository(BaseAIRepository):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.openai_api_key)

    async def generate_response(self, prompt: str, model: str, parameters: dict) -> Optional[str]:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **parameters
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response from OpenAI: {e}")
            return None

    def stream_response(self, prompt: str, model: str, parameters: dict) -> AsyncGenerator[Optional[str], None]:
        async def stream_generator():
            try:
                stream = await self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    **parameters
                )
                async for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
            except Exception as e:
                print(f"Error streaming response from OpenAI: {e}")
                yield None

        return stream_generator()
