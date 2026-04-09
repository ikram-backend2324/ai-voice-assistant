import requests
import os

OPENROUTER_API_KEY = "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"

SYSTEM_PROMPT = """
Ты голосовой ассистент.
Отвечай ВСЕГДА только на русском языке.
Никогда не используй английский.
Отвечай кратко, понятно и по делу.
Без markdown, без списков, без форматирования.
"""

def ask_ai(user_text):
    if not OPENROUTER_API_KEY:
        return "AI не настроен."

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.3
            },
            timeout=10
        )

        data = response.json()

        text = data["choices"][0]["message"]["content"].strip()

        # 💥 ЖЁСТКИЙ ФИЛЬТР ОТ АНГЛИЙСКОГО
        if any(word in text.lower() for word in ["the", "and", "is", "are", "you"]):
            return "Пожалуйста, повторите запрос."

        return text

    except Exception as e:
        print("AI ERROR:", e)
        return "Ошибка AI."