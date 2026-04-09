import requests
import time

OPENROUTER_API_KEY = "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"

last_call = 0

def rate_limit():
    global last_call
    now = time.time()
    if now - last_call < 2:
        time.sleep(2 - (now - last_call))
    last_call = time.time()

def ask_ai(user_text):
    rate_limit()

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
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "Отвечай на русском языке."},
                    {"role": "user", "content": user_text}
                ]
            },
            timeout=10
        )

        if response.status_code != 200:
            print("HTTP ERROR:", response.status_code, response.text)
            return "Сервис временно недоступен."

        data = response.json()
        print("AI RAW:", data)

        if "error" in data:
            return "AI временно недоступен."

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("AI ERROR:", e)
        return "Ошибка AI."