import json
import os
import urllib.error
import urllib.parse
import urllib.request

from Head.mouth import speak

BASE_URL = "https://api.weatherapi.com/v1/current.json"
FALLBACK_URL = "https://wttr.in/?format=j1"
WEATHER_API_KEY_FILE = os.path.join("Data", "weather_api_key.txt")


def get_weather_api_key():
    api_key = os.getenv("WEATHER_API_KEY", "").strip()
    if api_key:
        return api_key

    if os.path.exists(WEATHER_API_KEY_FILE):
        with open(WEATHER_API_KEY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()

    raise RuntimeError(
        "Weather API key missing. Set WEATHER_API_KEY or put the key in Data/weather_api_key.txt."
    )


def fetch_weather_data(query="auto:ip"):
    params = {
        "key": get_weather_api_key(),
        "q": query,
        "aqi": "no",
    }
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "Friday-Jarvis/1.0"})

    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_fallback_weather_data():
    request = urllib.request.Request(
        FALLBACK_URL,
        headers={"User-Agent": "Friday-Jarvis/1.0"},
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def speak_weather_report(
    city_name,
    region,
    country,
    temp_c,
    feels_like,
    humidity,
    wind_kph,
    description,
    uv_index,
):
    weather_report = (
        f"Sir, your current location is {city_name}, {region}, {country}. "
        f"Temperature is {temp_c} degrees celsius. "
        f"Feels like {feels_like} degrees. "
        f"Humidity is {humidity} percent. "
        f"Wind speed is {wind_kph} kilometers per hour. "
        f"Sky condition is {description}. "
        f"UV index is {uv_index}."
    )

    print(weather_report)
    speak(weather_report)


def speak_weatherapi_report(data):
    speak_weather_report(
        city_name=data["location"]["name"],
        region=data["location"]["region"],
        country=data["location"]["country"],
        temp_c=data["current"]["temp_c"],
        feels_like=data["current"]["feelslike_c"],
        humidity=data["current"]["humidity"],
        wind_kph=data["current"]["wind_kph"],
        description=data["current"]["condition"]["text"],
        uv_index=data["current"]["uv"],
    )


def speak_fallback_weather_report(data):
    current = data["current_condition"][0]
    area = data["nearest_area"][0]

    speak_weather_report(
        city_name=area["areaName"][0]["value"],
        region=area["region"][0]["value"],
        country=area["country"][0]["value"],
        temp_c=current["temp_C"],
        feels_like=current["FeelsLikeC"],
        humidity=current["humidity"],
        wind_kph=current["windspeedKmph"],
        description=current["weatherDesc"][0]["value"],
        uv_index=current.get("uvIndex", "not available"),
    )


def parse_weatherapi_error(error_body):
    try:
        return json.loads(error_body).get("error", {})
    except json.JSONDecodeError:
        return {}


def get_weather():
    try:
        data = fetch_weather_data()

        if "error" in data:
            error_msg = data["error"]["message"]
            print(f"API Error: {error_msg}")
            speak("Sorry sir, could not get weather data!")
            return

        speak_weatherapi_report(data)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        weather_error = parse_weatherapi_error(error_body)

        if e.code == 401 and weather_error.get("code") == 2006:
            print("Weather API key is invalid. Using fallback weather service.")
            try:
                speak_fallback_weather_report(fetch_fallback_weather_data())
            except Exception as fallback_error:
                print(f"Fallback Weather Error: {fallback_error}")
                speak("Sorry sir, the WeatherAPI key is invalid and fallback weather also failed.")
            return

        print(f"Weather API Error {e.code}: {weather_error.get('message', error_body)}")
        speak("Sorry sir, the weather API returned an error!")
    except urllib.error.URLError as e:
        print(f"Weather Connection Error: {e.reason}")
        speak("Sorry sir, I could not connect to the weather API!")
    except Exception as e:
        print(f"Weather Error: {e}")
        speak("Sorry sir, there was a weather error!")


def weather_today():
    speak("Detecting your location and checking weather sir!")
    get_weather()
