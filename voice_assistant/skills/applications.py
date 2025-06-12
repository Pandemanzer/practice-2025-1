import os
os.environ["VOSK_LOG_LEVEL"] = "-1"  # 🔇 отключение логов Vosk C++
import time
import json
import re
import asyncio
import pyautogui
from utils import speak, listen
from googletrans import Translator
from datetime import datetime, timedelta


translator = Translator()

ALIASES_FILE = "aliases.json"
CACHE_FILE = "program_cache.json"

# === Ярлыки ===
def load_aliases():
    try:
        with open(ALIASES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_aliases(aliases):
    with open(ALIASES_FILE, "w", encoding="utf-8") as f:
        json.dump(aliases, f, indent=4, ensure_ascii=False)

ALIASES = load_aliases()

# === Перевод русских названий
def translate_if_needed(query):
    try:
        if re.search(r'[а-яА-Я]', query):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            translated = loop.run_until_complete(translator.translate(query, src='ru', dest='en'))
            return translated.text.lower()
        else:
            return query.lower()
    except:
        return query.lower()

# === Приоритет: сначала англ., потом русское слово
def get_search_terms(query):
    translated = translate_if_needed(query)
    if translated != query:
        return [translated, query]
    return [query]

# === Поиск программ на диске
def search_application_on_disk(search_dirs):
    matches = {}
    for root_dir in search_dirs:
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file.lower().endswith((".exe", ".lnk")):
                    name = os.path.splitext(file)[0].lower()
                    if name not in matches:
                        matches[name] = os.path.join(root, file)
    return matches

# === Кэширование программ
def get_program_cache(search_dirs, max_age_days=3):
    if os.path.exists(CACHE_FILE):
        modified_time = datetime.fromtimestamp(os.path.getmtime(CACHE_FILE))
        if datetime.now() - modified_time < timedelta(days=max_age_days):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)

    # Кэш устарел или не существует — обновим
    speak("Обновляю список программ, подождите...")
    cache = search_application_on_disk(search_dirs)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4, ensure_ascii=False)
    speak("Список программ обновлён.")
    return cache


# === Меню Пуск
def open_with_start_menu(app_name):
    pyautogui.press("win")
    time.sleep(1)
    pyautogui.write(app_name, interval=0.1)
    time.sleep(1)
    pyautogui.press("enter")

# === Подтверждение
def confirm(prompt_text):
    speak(prompt_text)
    response = listen().strip().lower()

    yes_words = ["да", "ага", "верно", "подтверждаю", "давай", "ок", "угу", "точно"]
    no_words = ["нет", "не", "отмена", "не надо", "не хочу", "не подтверждаю", "отказ"]

    if response in yes_words:
        return True
    elif response in no_words:
        return False
    else:
        return confirm("Повторите, пожалуйста — да или нет?")

# === Сохранение ярлыка
def add_to_aliases(path):
    while True:
        speak("Как бы вы хотели назвать эту программу?")
        custom_name = listen().strip()
        if not custom_name:
            continue
        speak(f"Вы сказали: {custom_name}. Верно?")
        if confirm("Это верно?"):
            ALIASES[custom_name] = path
            save_aliases(ALIASES)
            speak(f"Сохранила как {custom_name}.")
            break
        else:
            speak("Хорошо, повторите название.")

# === Основная логика запуска
def open_application(app_name):
    username = os.getlogin()

    if app_name in ALIASES:
        path = ALIASES[app_name]
        if path.startswith("[START_MENU_SEARCH:"):
            name = path.replace("[START_MENU_SEARCH:", "").replace("]", "")
            open_with_start_menu(name)
            speak(f"Открываю {name} через меню Пуск.")
            return
        elif os.path.exists(path):
            os.startfile(path)
            speak(f"Открываю {app_name} из ярлыка.")
            return

    # === Папки для поиска
    search_dirs = [
        "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs",
        f"C:\\Users\\{username}\\Desktop",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        f"C:\\Users\\{username}\\AppData\\Local\\Programs",
        f"C:\\Users\\{username}\\AppData\\Local",
        f"C:\\Users\\{username}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs"
    ]

    # === Кэш программ
    program_cache = get_program_cache(search_dirs)

    # === Термины для поиска
    search_terms = get_search_terms(app_name)

    # === Совпадения
    found = []
    for term in search_terms:
        for key, path in program_cache.items():
            if term.lower() in key:
                found.append((key, path))

    # === Удаление дублей
    seen = set()
    matches = []
    for name, path in found:
        if path not in seen:
            seen.add(path)
            matches.append((name, path))

    # === Ничего не найдено
    if not matches:
        speak(f"Я не нашла {app_name}. Искать через меню Пуск?")
        if confirm("Поискать через меню Пуск?"):
            open_with_start_menu(app_name)
            speak(f"Пробую открыть {app_name}.")
            if confirm("Я правильно открыла?"):
                add_to_aliases(f"[START_MENU_SEARCH:{app_name}]")
        else:
            speak("Хорошо, не ищу.")
        return

    # === Точное совпадение — открыть сразу
    for name, path in matches:
        if name == app_name.lower():
            os.startfile(path)
            speak(f"Открываю {name}.")
            return

    # === Множественный выбор
    if len(matches) > 1:
        speak(f"Найдено {len(matches)} вариантов:")
        print("\n--- Найденные приложения ---")
        for i, (name, path) in enumerate(matches, 1):
            print(f"{i}. {name}")
            speak(f"{i}: {name}")
        speak("Скажите номер нужного или 'выход'.")

        response = listen().lower()
        if "выход" in response or "отмена" in response:
            speak("Выбор отменён.")
            return

        digit_map = {
            "один": 1, "первое": 1, "1": 1,
            "два": 2, "второе": 2, "2": 2,
            "три": 3, "третье": 3, "3": 3,
            "четыре": 4, "четвертое": 4, "4": 4,
            "пять": 5, "пятое": 5, "5": 5
        }

        for key, val in digit_map.items():
            if key in response and val <= len(matches):
                os.startfile(matches[val - 1][1])
                speak(f"Открываю {matches[val - 1][0]}.")
                return

        speak("Не поняла номер. Попробуйте снова.")
        return

    # === Один результат — просто открыть
    os.startfile(matches[0][1])
    speak(f"Открываю {matches[0][0]}.")

def handle(query):
    query = query.strip().lower()

    if "забудь ярлык" in query or "удали ярлык" in query:
        name = query.replace("забудь ярлык", "").replace("удали ярлык", "").strip()
        if name in ALIASES:
            speak(f"Вы уверены, что хотите забыть ярлык {name}?")
            if confirm("Удалить ярлык?"):
                del ALIASES[name]
                save_aliases(ALIASES)
                speak(f"Ярлык {name} удалён.")
            else:
                speak("Отмена удаления.")
        else:
            speak(f"Ярлык {name} не найден.")
        return True

    if "открой" in query or "запусти" in query:
        app_name = query.replace("открой", "").replace("запусти", "").strip()
        if app_name:
            open_application(app_name)
            return True

    return False

