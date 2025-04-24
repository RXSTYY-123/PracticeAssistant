from app.speech import Speech
from app.commands import CommandHandler

def main():
    speech = Speech()
    handler = CommandHandler()

    print("Ассистент запущен. Скажите 'Эй, Компик' для активации.")
    while True:
        text = speech.listen()
        if text == "выход":
            speech.speak("До свидания!")
            break
        handler.handle(text)

if __name__ == "__main__":
    main()