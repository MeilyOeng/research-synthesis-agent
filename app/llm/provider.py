import anthropic
from app.core.config import settings


client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

async def complete(messages):

    response = await client.messages.create(
        model=settings.model_name,
        max_tokens=settings.max_tokens,
        messages=messages
    )

    text = response.content[0].text

    return text