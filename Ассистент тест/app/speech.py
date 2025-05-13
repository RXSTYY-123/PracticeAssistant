import speech_recognition as sr
import pyttsx3
from app.config import TRIGGER_WORDS

class Speech:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Скорость речи

    def listen(self) -> str:
        with sr.Microphone() as source:
            print("Слушаю...")
            audio = self.recognizer.listen(source, phrase_time_limit=5)

        try:
            text = self.recognizer.recognize_google(audio, language='ru-RU').lower()
            print(f"Распознано: {text}")
            return text
        except (sr.UnknownValueError, sr.RequestError):
            return ""

    def speak(self, text: str):
        print(f"Ассистент: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def is_trigger(self, text: str) -> bool:
        return any(trigger in text for trigger in TRIGGER_WORDS)