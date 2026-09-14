import json
import os
import datetime
from Head.mouth import speak

# ================================
MEMORY_FILE = "Head/memory.json"
HISTORY_FILE = "Head/chat_history.json"
# ================================

# ─────────────────────────────────
# LOAD & SAVE
# ─────────────────────────────────
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# ─────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────
def add_to_history(role, message):
    history = load_history()
    history.append({
        "role": role,
        "message": message,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    # Keep last 50 conversations only
    if len(history) > 50:
        history = history[-50:]
    save_history(history)

def get_recent_history(count=10):
    history = load_history()
    return history[-count:]

def get_history_as_text():
    history = get_recent_history(10)
    if not history:
        return ""
    text = ""
    for h in history:
        text += f"{h['role']}: {h['message']}\n"
    return text

# ─────────────────────────────────
# AUTO CALCULATE AGE
# ─────────────────────────────────
def calculate_age(birth_year, birth_month=1, birth_day=1):
    today = datetime.datetime.now()
    age = today.year - birth_year
    # Check if birthday has passed this year
    if (today.month, today.day) < (birth_month, birth_day):
        age -= 1
    return age

def get_age():
    memory = load_memory()
    if "birth_year" in memory:
        birth_year = int(memory["birth_year"])
        birth_month = int(memory.get("birth_month", 1))
        birth_day = int(memory.get("birth_day", 1))
        age = calculate_age(birth_year, birth_month, birth_day)
        # Auto update age in memory
        memory["age"] = str(age)
        save_memory(memory)
        return age
    return None

# ─────────────────────────────────
# REMEMBER
# ─────────────────────────────────
def remember(text):
    memory = load_memory()
    try:
        # Name
        if "my name is" in text:
            name = text.split("my name is")[-1].strip()
            memory["name"] = name
            save_memory(memory)
            speak(f"I will remember your name is {name}!")

        # Birthday full "my birthday is 15 august 2006"
        elif "my birthday is" in text:
            info = text.split("my birthday is")[-1].strip()
            memory["birthday_raw"] = info
            # Try to extract year
            words = info.split()
            for word in words:
                if word.isdigit() and len(word) == 4:
                    memory["birth_year"] = int(word)
            # Try to extract month
            months = {
                "january": 1, "february": 2, "march": 3,
                "april": 4, "may": 5, "june": 6,
                "july": 7, "august": 8, "september": 9,
                "october": 10, "november": 11, "december": 12
            }
            for month, num in months.items():
                if month in info.lower():
                    memory["birth_month"] = num
            # Try to extract day
            for word in words:
                if word.isdigit() and 1 <= int(word) <= 31:
                    memory["birth_day"] = int(word)

            age = get_age()
            save_memory(memory)
            if age:
                speak(f"Birthday saved! You are currently {age} years old!")
            else:
                speak(f"Birthday saved!")

        # Birth year only
        elif "my birth year is" in text:
            year = text.split("my birth year is")[-1].strip()
            memory["birth_year"] = int(year)
            age = calculate_age(int(year))
            memory["age"] = str(age)
            save_memory(memory)
            speak(f"Got it! You were born in {year}, so you are {age} years old!")

        # Favourite color
        elif "my favourite color is" in text:
            color = text.split("my favourite color is")[-1].strip()
            memory["favourite_color"] = color
            save_memory(memory)
            speak(f"I will remember your favourite color is {color}!")

        # Favourite food
        elif "my favourite food is" in text:
            food = text.split("my favourite food is")[-1].strip()
            memory["favourite_food"] = food
            save_memory(memory)
            speak(f"I will remember your favourite food is {food}!")

        # City
        elif "my city is" in text:
            city = text.split("my city is")[-1].strip()
            memory["city"] = city
            save_memory(memory)
            speak(f"I will remember you live in {city}!")

        # Job
        elif "i am a" in text or "i work as" in text:
            job = text.split("i am a")[-1].strip() if "i am a" in text else text.split("i work as")[-1].strip()
            memory["job"] = job
            save_memory(memory)
            speak(f"Got it! I will remember you are a {job}!")

        # Current task
        elif "i am working on" in text or "i am doing" in text:
            task = text.split("i am working on")[-1].strip() if "i am working on" in text else text.split("i am doing")[-1].strip()
            memory["current_task"] = task
            memory["task_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_memory(memory)
            speak(f"Got it! I know you are working on {task}. I will help you with it!")

        # Custom note
        elif "remember that" in text:
            info = text.split("remember that")[-1].strip()
            notes = memory.get("notes", [])
            notes.append({
                "note": info,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            memory["notes"] = notes
            save_memory(memory)
            speak(f"Got it! I will remember that {info}!")

        else:
            speak("Please tell me clearly what to remember!")

    except Exception as e:
        print(f"Remember Error: {e}")
        speak("Sorry I could not save that!")

# ─────────────────────────────────
# RECALL
# ─────────────────────────────────
def recall(text):
    memory = load_memory()
    try:
        # Age — auto calculated!
        if "my age" in text or "how old am i" in text:
            age = get_age()
            if age:
                memory = load_memory()
                birthday = memory.get("birthday_raw", "")
                speak(f"You are currently {age} years old Mr Anik Mech! Your birthday is {birthday}.")
            else:
                speak("I don't know your birthday yet. Please tell me your birthday!")

        # Name
        elif "my name" in text:
            if "name" in memory:
                speak(f"Your name is {memory['name']}!")
            else:
                speak("I don't know your name yet!")

        # Current task
        elif "what am i doing" in text or "my current task" in text:
            if "current_task" in memory:
                task = memory["current_task"]
                task_time = memory.get("task_time", "")
                speak(f"You are working on {task} since {task_time}!")
            else:
                speak("I don't know what you are doing currently!")

        # All notes
        elif "my notes" in text:
            notes = memory.get("notes", [])
            if notes:
                speak(f"You have {len(notes)} notes. ")
                for i, note in enumerate(notes[-5:]):
                    speak(f"Note {i+1}: {note['note']}")
            else:
                speak("You have no notes saved!")

        # Recent history
        elif "what did i say" in text or "chat history" in text:
            history = get_recent_history(5)
            if history:
                speak(f"Here are your last {len(history)} messages!")
                for h in history:
                    speak(f"{h['role']} said: {h['message']}")
            else:
                speak("No chat history found!")

        # Everything
        elif "what do you know about me" in text or "what do you remember" in text:
            if memory:
                age = get_age()
                report = "Here is what I know about you Mr Anik Mech. "
                if "name" in memory:
                    report += f"Your name is {memory['name']}. "
                if age:
                    report += f"You are {age} years old. "
                if "city" in memory:
                    report += f"You live in {memory['city']}. "
                if "job" in memory:
                    report += f"You are a {memory['job']}. "
                if "favourite_food" in memory:
                    report += f"Your favourite food is {memory['favourite_food']}. "
                if "favourite_color" in memory:
                    report += f"Your favourite color is {memory['favourite_color']}. "
                if "current_task" in memory:
                    report += f"Currently you are working on {memory['current_task']}. "
                speak(report)
            else:
                speak("I don't know anything about you yet!")

        # Forget everything
        elif "forget everything" in text:
            save_memory({})
            save_history([])
            speak("I have cleared all memories and history Mr Anik Mech!")

    except Exception as e:
        print(f"Recall Error: {e}")
        speak("Sorry I could not recall that!")

# ─────────────────────────────────
# GET CONTEXT FOR GROQ
# ─────────────────────────────────
def get_context_for_groq():
    memory = load_memory()
    history = get_history_as_text()
    age = get_age()

    context = (
        "You are Friday, personal AI assistant of Mr Anik Mech. "
        "If asked who developed, created, made, or built you, answer exactly: I was developed by Anik Mech. "
        "Address the user as sir, never as sahab. "
    )

    if memory:
        context += "Here is what you know about the user: "
        if "name" in memory:
            context += f"Name is {memory['name']}. "
        if age:
            context += f"Age is {age} years old. "
        if "city" in memory:
            context += f"Lives in {memory['city']}. "
        if "job" in memory:
            context += f"Works as {memory['job']}. "
        if "current_task" in memory:
            context += f"Currently working on {memory['current_task']}. "

    if history:
        context += f"Recent conversation history: {history}"

    context += "Keep replies short and natural. Use this context to give smart personalized answers."

    return context
