import os
os.environ["VOSK_LOG_LEVEL"] = "-1"  # 🔇 отключение логов Vosk C++

import pyttsx3
import sys

# === Инициализация синтезатора речи ===
engine = pyttsx3.init()
engine.setProperty('rate', 180)

# === Озвучивание текста ===
def speak(text):
    engine.say(text)
    engine.runAndWait()

# === Онлайн-распознавание речи (Google) ===
def listen_online():
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎙️ Слушаю (онлайн)...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="ru-RU")
            print(f"Вы сказали: {text}")
            return text.lower()
    except Exception as e:
        print(f"[listen_online] Ошибка: {e}")
        return ""

# === Офлайн-распознавание речи (VOSK) ===
def listen_offline():
    from vosk import Model, KaldiRecognizer
    import pyaudio
    import json

    print("🎤 Слушаю (офлайн)...")
    model = Model("vosk-model-ru")
    recognizer = KaldiRecognizer(model, 16000)

    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000,
                      input=True, frames_per_buffer=8192)
    stream.start_stream()

    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").lower()
            if text:
                print(f"Вы сказали: {text}")
                return text

# === Универсальная функция прослушки ===
def listen():
    try:
        return listen_online() or listen_offline()
    except:
        return listen_offline()
