import json
import os
import re
import urllib.error
import urllib.request

import speech_recognition as sr
from colorama import Fore, init

from Head.brain import brain
from Head.memory import add_to_history, get_context_for_groq
from Head.mouth import speak

init(autoreset=True)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")
OPENROUTER_KEY_FILE = os.path.join("Data", "openrouter_api_key.txt")
LISTEN_TIMEOUT = 5
PHRASE_TIME_LIMIT = 8
AMBIENT_NOISE_DURATION = 0.4
OPENROUTER_TIMEOUT = 20
MAX_RESPONSE_TOKENS = 80


def get_openrouter_api_key():
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if api_key:
        return api_key

    if os.path.exists(OPENROUTER_KEY_FILE):
        with open(OPENROUTER_KEY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()

    raise RuntimeError(
        "OpenRouter API key missing. Set OPENROUTER_API_KEY or put the key in Data/openrouter_api_key.txt."
    )


def normalize_assistant_response(response):
    return re.sub(r"\bsahab\b", "sir", response, flags=re.IGNORECASE)


def ask_jarvis(text):
    system_context = get_context_for_groq()
    payload = {
        "model": OPENROUTER_MODEL,
        "max_tokens": MAX_RESPONSE_TOKENS,
        "messages": [
            {"role": "system", "content": system_context},
            {"role": "user", "content": text}
        ],
    }

    request = urllib.request.Request(
        OPENROUTER_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {get_openrouter_api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Friday Jarvis",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=OPENROUTER_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter API error {e.code}: {error_body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"OpenRouter connection error: {e.reason}") from e

    try:
        response = data["choices"][0]["message"]["content"].strip()
        return normalize_assistant_response(response)
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected OpenRouter response: {data}") from e


def listen():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 250
    recognizer.pause_threshold = 0.6
    recognizer.non_speaking_duration = 0.4

    with sr.Microphone(device_index=None) as source:
        recognizer.adjust_for_ambient_noise(source, duration=AMBIENT_NOISE_DURATION)
        print(Fore.LIGHTGREEN_EX + "I am Listening...")
        while True:
            try:
                audio = recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT
                )

                recognized_txt = recognizer.recognize_google(audio).lower()
                if recognized_txt:
                    print(Fore.BLUE + "Mr Anik Mech : " + recognized_txt)
                    add_to_history("Mr Anik Mech", recognized_txt)

                    task_done = brain(recognized_txt)

                    if not task_done:
                        response = ask_jarvis(recognized_txt)
                        print(Fore.YELLOW + "Friday : " + response)
                        speak(response)
                        add_to_history("Friday", response)

                    print(Fore.LIGHTGREEN_EX + "I am Listening...")

            except sr.UnknownValueError:
                pass
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    listen()
