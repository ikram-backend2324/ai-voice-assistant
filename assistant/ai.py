import requests
import re

OPENROUTER_API_KEY = "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"

SYSTEM_PROMPT = """
Ты голосовой ассистент.
Отвечай всегда только на русском языке.
Кратко и по делу.
"""

def ask_ai(user_text):
    if not OPENROUTER_API_KEY:
        return "AI не настроен."

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-voice-assistant-psjj.onrender.com",
                "X-Title": "Voice Assistant"
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                "temperature": 0.3
            },
            timeout=10
        )

        data = response.json()
        print("AI RAW:", data)

        if "error" in data:
            return "AI временно недоступен."

        if "choices" not in data:
            return "Нет ответа от AI."

        text = data["choices"][0]["message"]["content"].strip()

        # фильтр английского
        if re.search(r'[a-zA-Z]{4,}', text):
            return "Пожалуйста, повторите запрос."

        return text

    except Exception as e:
        print("AI ERROR:", e)
        return "Ошибка AI."