import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel(settings.model_name)

async def complete(prompt: str) -> str:
    response = await model.generate_content_async(prompt)
    return response.text