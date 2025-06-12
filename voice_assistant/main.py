import os
os.environ["VOSK_LOG_LEVEL"] = "-1"

from tray_tkinter import TrayIconTk
import threading
from utils import listen, speak
from skills import system, browser, applications

# === Настройки
ASSISTANT_NAME = "веста"
assistant_names = ["веста", "vesta", "место", "вест", "вес"]
handlers = [system.handle, browser.handle, applications.handle]

# === Фразы помощи
help_phrases = [
    "что ты умеешь", "что ты можешь", "помощь",
    "возможности", "список команд", "какие функции"
]

def explain_features():
    speak("Вот что я умею:")
    speak("Запускать программы по голосу.")
    speak("Открывать сайты и выполнять поиск в интернете.")
    speak("Управлять компьютером: выключать, перезагружать, блокировать.")
    speak("Работать как онлайн, так и офлайн.")
    speak("Запоминать и забывать ярлыки для быстрого запуска.")
    speak("Показывать список найденных программ и давать выбор.")
    speak("Чтобы активировать меня, скажите Веста. Чтобы отключить — скажите стоп.")

# === Основной класс, запускаемый из GUI
def assistant_logic(tray):
    active = False
    tray.set_idle()
    speak("Голосовой помощник запущен. Скажите 'Веста', чтобы активировать.")

    while True:
        query = listen().strip()
        if not query:
            continue

        if any(name in query for name in assistant_names):
            if "выключение программы" in query:
                speak("Выключаюсь. До свидания.")
                tray.root.quit()
                break

            elif "стоп" in query and active:
                speak("Переход в режим ожидания.")
                active = False
                tray.set_idle()
                continue

            elif not active:
                speak("Я вас слушаю.")
                active = True
                tray.set_active()
                continue

        # 🎙 Если пользователь просит помощь
        if active and any(phrase in query for phrase in help_phrases):
            explain_features()
            continue

        if active:
            for handler in handlers:
                if handler(query):
                    break

# === Запуск
if __name__ == "__main__":
    tray = TrayIconTk()
    logic_thread = threading.Thread(target=assistant_logic, args=(tray,), daemon=True)
    logic_thread.start()
    tray.run()
