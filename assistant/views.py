# assistant/views.py
from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime
import requests

from .ai import ask_ai
from dotenv import load_dotenv
import os

load_dotenv()
# ── helpers ────────────────────────────────────────────────

SITES = {
    "youtube":  "https://youtube.com",
    "google":   "https://google.com",
    "wikipedia":"https://ru.wikipedia.org",
    "вконтакте":"https://vk.com",
    "вк":       "https://vk.com",
    "телеграм": "https://web.telegram.org",
    "gmail":    "https://mail.google.com",
    "github":   "https://github.com",
}

WEEKDAYS = [
    "понедельник", "вторник", "среда",
    "четверг", "пятница", "суббота", "воскресенье"
]

MONTHS = [
    "января", "февраля", "марта", "апреля",
    "мая", "июня", "июля", "августа",
    "сентября", "октября", "ноября", "декабря"
]

def get_weather(city="Tashkent"):
    key = "2d1c493ec6de6f656d67745b7aff5036"
    if not key:
        return "Ключ погоды не настроен."

    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": key,
                "units": "metric",
                "lang": "ru"
            },
            timeout=5
        )

        data = r.json()

        if data.get("cod") != 200:
            return f"Не нашёл город {city}."

        desc  = data["weather"][0]["description"]
        temp  = round(data["main"]["temp"])
        feels = round(data["main"]["feels_like"])

        return f"В {city}: {desc}, {temp}°C, ощущается как {feels}°C."

    except Exception as e:
        print("WEATHER ERROR:", e)
        return "Ошибка получения погоды."

# ── views ──────────────────────────────────────────────────

def index(request):
    return render(request, 'index.html')

def process_command(request):
    text = request.GET.get('text', '').lower().strip()

    # ── greetings ─────────────────────────────────────────────
    if any(w in text for w in ["привет", "здравствуй", "hello", "hi"]):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "Доброе утро!"
        elif 12 <= hour < 18:
            greeting = "Добрый день!"
        elif 18 <= hour < 23:
            greeting = "Добрый вечер!"
        else:
            greeting = "Доброй ночи!"
        return JsonResponse({"response": f"{greeting} Я ваш голосовой ассистент. Чем могу помочь?"})

    # ── time ──────────────────────────────────────────────────
    elif any(w in text for w in ["время", "который час", "сколько времени", "time"]):
        now = datetime.now().strftime("%H:%M")
        return JsonResponse({"response": f"Сейчас {now}."})

    # ── date ──────────────────────────────────────────────────
    elif any(w in text for w in ["дата", "число", "какой день", "date", "today"]):
        now = datetime.now()
        day  = WEEKDAYS[now.weekday()]
        mon  = MONTHS[now.month - 1]
        return JsonResponse({"response": f"Сегодня {day}, {now.day} {mon} {now.year} года."})

    # ── weather ───────────────────────────────────────────────
    elif any(w in text for w in ["погода", "weather", "температура"]):
        # try to extract a city name after "в" / "in"
        city = "Tashkent"
        for prep in [" в ", " in "]:
            if prep in text:
                city = text.split(prep, 1)[1].strip().title()
                break
        return JsonResponse({"response": get_weather(city)})

    # ── open website ──────────────────────────────────────────
    elif any(w in text for w in ["открой", "запусти", "перейди", "open"]):
        for name, url in SITES.items():
            if name in text:
                return JsonResponse({
                    "response": f"Открываю {name.capitalize()}.",
                    "action": "open_url",
                    "url": url
                })
        return JsonResponse({"response": "Не знаю такого сайта."})

    # ── volume ────────────────────────────────────────────────
    # (volume is controlled client-side; backend just signals)
    elif any(w in text for w in ["громче", "volume up"]):
        return JsonResponse({"response": "Увеличиваю громкость.", "action": "volume_up"})

    elif any(w in text for w in ["тише", "volume down"]):
        return JsonResponse({"response": "Уменьшаю громкость.", "action": "volume_down"})

    elif any(w in text for w in ["без звука", "mute"]):
        return JsonResponse({"response": "Включаю режим без звука.", "action": "mute"})

    # ── goodbye ───────────────────────────────────────────────
    elif any(w in text for w in ["пока", "до свидания", "bye", "goodbye"]):
        return JsonResponse({"response": "До свидания! Обращайтесь."})

    # ── AI fallback ───────────────────────────────────────────
    else:
        ai_response = ask_ai(text)
        return JsonResponse({"response": ai_response})

print("WEATHER:", os.getenv("WEATHER_API_KEY"))
print("AI:", os.getenv("OPENROUTER_API_KEY"))