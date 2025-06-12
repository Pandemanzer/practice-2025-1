import os
import sys
from utils import speak

# Обработка системных команд
def handle(query):
    if "выключи" in query:
        speak("Выключаю компьютер.")
        os.system("shutdown /s /t 5")
        sys.exit()
        return True

    elif "перезагрузи" in query:
        speak("Перезагружаю компьютер.")
        os.system("shutdown /r /t 5")
        sys.exit()
        return True

    elif "заблокируй" in query:
        speak("Блокирую компьютер.")
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return True

    return False  # Команда не распознана этим модулем
