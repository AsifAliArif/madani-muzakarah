import json

import google.generativeai as genai
from openai import OpenAI

from app.auth.security import decrypt_value
from app.models.ai_settings import AISettings
from app.services.ai_formatting import parse_llm_json


async def call_llm(settings: AISettings, text: str) -> list[dict]:
    api_key = decrypt_value(settings.api_key_encrypted)
    if not api_key:
        return []

    prompt = f"{settings.system_prompt}\n\nAnalyze this text:\n{text}"

    llm_name = settings.llm_name.lower()
    try:
        if "gemini" in llm_name or "google" in llm_name:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(settings.llm_name.replace("google/", ""))
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            return parse_llm_json(response.text or "{}")
        else:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=settings.llm_name,
                messages=[
                    {"role": "system", "content": settings.system_prompt},
                    {"role": "user", "content": f"Analyze this text:\n{text}"},
                ],
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            return parse_llm_json(content)
    except Exception:
        return []
