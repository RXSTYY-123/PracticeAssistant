import os
import subprocess
import pyautogui
import time
import psutil
import webbrowser
from app.database import Database
from app.speech import Speech

class CommandHandler:
    def __init__(self):
        self.db = Database()
        self.speech = Speech()
        self.is_active = False
        self.trigger_words = ["эй компик", "компик", "ассистент"]
        
        self.app_paths = {
            'steam': r"C:\Program Files (x86)\Steam\steam.exe",
            'browser': r"C:\Program Files (x86)\Yandex\YandexBrowser\Application\browser.exe",
            'vk_music': "https://vk.com/audios"
        }

    def _launch_app(self, app_name: str) -> bool:
        path = self.app_paths.get(app_name)
        if not path or not os.path.exists(path):
            self.speech.speak(f"Не могу найти {app_name}")
            return False

        try:
            if app_name == 'browser':
                webbrowser.open(path)
            else:
                subprocess.Popen(path, shell=True)
            return True
        except Exception as e:
            print(f"Ошибка запуска {app_name}: {e}")
            return False

    def _control_media(self, action: str) -> bool:
        try:
            for _ in range(3):
                try:
                    browser_window = pyautogui.getWindowsWithTitle("VK Музыка")[0]
                    browser_window.activate()
                    time.sleep(1)
                    break
                except:
                    webbrowser.open(self.app_paths['vk_music'])
                    time.sleep(3)

            # Выполняем действие
            if action == 'playpause':
                pyautogui.press('space')
            elif action == 'nexttrack':
                pyautogui.hotkey('shift', 'n')
            elif action == 'prevtrack':
                pyautogui.hotkey('shift', 'p')
            return True
        except Exception as e:
            print(f"Ошибка управления медиа: {e}")
            return False

    def handle(self, text: str) -> bool:
        if not self.is_active:
            if any(trigger in text.lower() for trigger in self.trigger_words):
                self.is_active = True
                self.speech.speak("Слушаю вас")
                return True
            return False

        if any(cmd in text.lower() for cmd in ["стоп", "хватит"]):
            self.is_active = False
            self.speech.speak("Режим ожидания")
            return True

        try:
            text_lower = text.lower()
            
            if "запусти steam" in text_lower:
                if self._launch_app('steam'):
                    self.speech.speak("Steam запускается")
                return True
            
            elif "открой браузер" in text_lower:
                if self._launch_app('browser'):
                    self.speech.speak("Браузер открывается")
                return True
            
            elif any(cmd in text_lower for cmd in ["пауза", "стоп музыку"]):
                if self._control_media('playpause'):
                    self.speech.speak("Музыка приостановлена")
                return True
            
            # Логирование в БД
            self.db.log_command(text, 'success')
            return True

        except Exception as e:
            print(f"Критическая ошибка: {e}")
            self.speech.speak("Произошла ошибка")
            return False