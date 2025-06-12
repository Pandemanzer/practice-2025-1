import webbrowser
from utils import speak

# Обработка поисковых команд
def handle(query):
    if "найди" in query or "гугли" in query or "зайди" in query:
        # Извлекаем поисковую фразу
        search = query.replace("найди", "").replace("гугли", "").replace("зайди", "").strip()

        # Формируем URL и открываем в браузере
        url = f"https://www.google.com/search?q={search.replace(' ', '+')}"
        webbrowser.open_new_tab(url)

        speak(f"Ищу {search} в интернете.")
        return True

    return False  # Команда не распознана этим модулем
