import webbrowser
import datetime
import os
import subprocess
from Head.mouth import speak
from Head.weather import weather_today
from Head.memory import remember, recall


WEATHER_KEYWORDS = (
    "weather",
    "temperature",
    "temp",
    "climate",
    "how hot",
    "how cold",
    "rain",
    "raining",
    "humidity",
    "wind",
)


def open_website(url):
    subprocess.Popen(["cmd", "/c", "start", url])


def is_weather_query(text):
    return any(keyword in text for keyword in WEATHER_KEYWORDS)


def is_developer_query(text):
    developer_words = (
        "developed",
        "developer",
        "created",
        "creator",
        "made",
        "built",
        "build",
    )
    assistant_words = (
        "you",
        "u",
        "your",
        "friday",
        "assistant",
        "ai",
    )
    return any(word in text for word in developer_words) and any(
        word in text for word in assistant_words
    )


def brain(text):
    text = text.lower()

    # 🌐 YouTube
    if "open youtube" in text:
        speak("Opening YouTube!")
        open_website("https://www.youtube.com")
        return True

    # 🌐 Instagram
    elif "open instagram" in text:
        speak("Opening Instagram!")
        open_website("https://www.instagram.com/_kim_anik_yang_/")
        return True

    # 🌐 Google
    elif "open google" in text:
        speak("Opening Google!")
        open_website("https://www.google.com")
        return True

    # 🌐 Facebook
    elif "open facebook" in text:
        speak("Opening Facebook!")
        open_website("https://www.facebook.com/RosnaMech77/")
        return True

    # 🌐 WhatsApp
    elif "open whatsapp" in text:
        speak("Opening WhatsApp!")
        open_website("https://web.whatsapp.com")
        return True

    # 🌐 Twitter
    elif "open twitter" in text:
        speak("Opening Twitter!")
        open_website("https://x.com/AnikMech25946 ")
        return True

    # 🌐 GitHub
    elif "open github" in text:
        speak("Opening GitHub!")
        open_website("https://github.com/anikmech")
        return True

    # 🔍 Search Google
    elif is_developer_query(text):
        speak("I was developed by Anik Mech.")
        return True

    elif "search" in text:
        query = text.replace("search", "").strip()
        speak(f"Searching {query}!")
        open_website(f"https://www.google.com/search?q={query}")
        return True

    # 🎵 Play YouTube
    elif "play" in text:
        query = text.replace("play", "").strip()
        speak(f"Playing {query} on YouTube!")
        open_website(f"https://www.youtube.com/results?search_query={query}")
        return True

    # ⏰ Time
    elif "time" in text:
        t = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {t} Mr Anik Mech!")
        return True

    # 📅 Date
    elif "date" in text:
        d = datetime.datetime.now().strftime("%d %B %Y")
        speak(f"Today is {d} Mr Anik Mech!")
        return True

    # 💻 Notepad
    elif "open notepad" in text:
        speak("Opening Notepad!")
        subprocess.Popen(["notepad.exe"])
        return True

    # 💻 Calculator
    elif "open calculator" in text:
        speak("Opening Calculator!")
        subprocess.Popen(["calc.exe"])
        return True

    # 😴 Exit
    elif "bye" in text or "sleep" in text:
        speak("Goodbye Mr Anik Mech!")
        exit()

    # Inside brain() function:
    elif is_weather_query(text):
        weather_today()
        return True

    elif "remember" in text:
        remember(text)
        return True

    elif "what am i doing" in text or "how old am i" in text or "what do you know" in text or "what do you remember" in text or "my notes" in text or "forget everything" in text or "what did i say" in text:
        recall(text)
        return True

    else:
        return False
