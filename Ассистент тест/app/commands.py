import os
import subprocess
import pyautogui
import time
import psutil
import winreg
from app.speech import Speech


class CommandHandler:
    def __init__(self):
        self.speech = Speech()
        self.is_active = False
        self.trigger_words = ["эй компик", "компик", "ассистент"]

    def _get_installed_app_path(self, app_name: str) -> str:
        """Получает путь к приложению из реестра"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppPaths\\" + app_name) as key:
                return winreg.QueryValue(key, None)
        except:
            return None

    def _launch_app(self, app_name: str) -> bool:
        """Универсальный запуск приложений"""
        try:
            # Попробуем найти приложение в реестре
            path = self._get_installed_app_path(app_name + '.exe')
            
            if path and os.path.exists(path):
                subprocess.Popen(path, shell=True)
                return True
            
            # Альтернативные методы запуска
            if app_name.lower() == 'steam':
                os.system('start steam://')
                return True
            elif app_name.lower() == 'yandex music':
                os.system('start yandexmusic://')
                return True
            elif app_name.lower() == 'browser':
                os.system('start chrome')
                return True
                
            return False
        except Exception as e:
            print(f"Ошибка запуска {app_name}: {e}")
            return False

    def _control_yandex_music(self, action: str) -> bool:
        """Управление Яндекс.Музыкой"""
        try:
            # Проверяем, запущено ли приложение
            if "yandexmusic.exe" not in [p.name().lower() for p in psutil.process_iter()]:
                self._launch_app('yandex music')
                time.sleep(5)  # Ждём запуска

            # Активируем окно
            for window in pyautogui.getWindowsWithTitle("Яндекс.Музыка"):
                window.activate()
                time.sleep(1)
                break

            # Выполняем действие
            if action == 'playpause':
                pyautogui.press('space')
            elif action == 'nexttrack':
                pyautogui.press('media_nexttrack')
            elif action == 'prevtrack':
                pyautogui.press('media_prevtrack')
                
            return True
        except Exception as e:
            print(f"Ошибка управления Яндекс.Музыкой: {e}")
            return False

    def handle(self, text: str) -> bool:
        """Основной обработчик команд"""
        try:
            # Активация
            if not self.is_active:
                if any(trigger in text.lower() for trigger in self.trigger_words):
                    self.is_active = True
                    self.speech.speak("Слушаю вас")
                    return True
                return False

            # Деактивация
            if any(cmd in text.lower() for cmd in ["стоп", "хватит"]):
                self.is_active = False
                self.speech.speak("Режим ожидания")
                return True

            # Обработка команд
            text_lower = text.lower()
            
            if "запусти steam" in text_lower:
                if self._launch_app('steam'):
                    self.speech.speak("Steam запускается")
                else:
                    self.speech.speak("Не удалось запустить Steam")
                return True
            
            elif "открой браузер" in text_lower:
                if self._launch_app('browser'):
                    self.speech.speak("Браузер открывается")
                else:
                    self.speech.speak("Не удалось открыть браузер")
                return True
            
            elif "открой яндекс музыку" in text_lower:
                if self._launch_app('yandex music'):
                    self.speech.speak("Яндекс.Музыка открывается")
                else:
                    self.speech.speak("Не удалось открыть Яндекс.Музыку")
                return True
            
            elif any(cmd in text_lower for cmd in ["пауза", "стоп музыку"]):
                if self._control_yandex_music('playpause'):
                    self.speech.speak("Музыка приостановлена")
                else:
                    self.speech.speak("Не удалось управлять музыкой")
                return True
                
            elif "следующий трек" in text_lower:
                if self._control_yandex_music('nexttrack'):
                    self.speech.speak("Следующий трек")
                else:
                    self.speech.speak("Не удалось переключить трек")
                return True

            self.speech.speak("Команда не распознана")
            return False

        except Exception as e:
            print(f"Критическая ошибка: {e}")
            return False