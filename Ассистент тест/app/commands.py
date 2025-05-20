import os
import subprocess
import pyautogui
import sys
import time
import psutil
import winreg
from app.database import Database
from app.speech import Speech

class CommandHandler:
    def __init__(self):
        self.db = Database()
        self.speech = Speech()
        self.is_active = False
        self.trigger_words = ["джеб", "глеб", "глеба", "глебас"]
        self.app_paths = {
        "browser.exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "steam.exe": r"C:\Program Files (x86)\Steam\steam.exe",
        "yandexmusic.exe": os.path.expanduser(r"~\AppData\Local\Programs\YandexMusic\Яндекс Музыка.exe")
    }
    def _log_command(self, command_text: str, status: str):
        """Логирование команды в базу данных"""
        try:
            self.db.cursor.execute(
                "INSERT INTO command_logs (command_text, status) VALUES (?, ?)",
                (command_text, status)
            )
            self.db.conn.commit()
        except Exception as e:
            print(f"Ошибка логирования команды: {e}")

    def _get_command_from_db(self, text: str):
        """Получает команду из базы данных по тексту"""
        try:
            self.db.cursor.execute(
                "SELECT action_type, action_target FROM commands WHERE ? LIKE '%' + trigger_phrase + '%'",
                (text.lower(),)
            )
            return self.db.cursor.fetchone()
        except Exception as e:
            print(f"Ошибка поиска команды в БД: {e}")
            return None

    def _get_installed_app_path(self, app_name: str) -> str:
        """Получает путь к приложению из реестра"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\\" + app_name) as key:
                return winreg.QueryValue(key, None)
        except:
            return None

    def _close_app(self, process_name: str) -> bool:
        """Упрощенное закрытие приложения по имени процесса"""
        try:
            target_name = process_name.lower().replace(".exe", "") + ".exe"
            
            closed = False
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == target_name:
                    try:
                        print(f"Пытаюсь закрыть процесс: {proc.info['name']} (PID: {proc.pid})")
                        proc.terminate()
                        time.sleep(0.5)
                        if proc.is_running():
                            proc.kill()
                        closed = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        print(f"Ошибка при закрытии процесса: {e}")
                        continue
            
            return closed
        except Exception as e:
            print(f"Общая ошибка при закрытии приложения: {e}")
            return False

    def _launch_app(self, path: str) -> bool:
        try:
            app_name = os.path.basename(path).lower()
            full_path = self.app_paths.get(app_name, path)

            if os.path.exists(full_path):
                subprocess.Popen(full_path, shell=True)
                return True
            
            reg_path = self._get_installed_app_path(app_name)
            if reg_path and os.path.exists(reg_path):
                subprocess.Popen(reg_path, shell=True)
                return True
            
            print(f"[ERROR] Не удалось найти путь для {app_name}")
            return False
        
        except Exception as e:
            print(f"Ошибка запуска приложения: {e}")
            return False
        
    def _control_media(self, action: str) -> bool:
        """Управление медиа через глобальные горячие клавиши"""
        try:
            if action == 'playpause':
                pyautogui.press('playpause')
            elif action == 'nexttrack':
                pyautogui.press('nexttrack')
            elif action == 'prevtrack':
                pyautogui.press('prevtrack')
            return True
        except Exception as e:
            print(f"Ошибка управления медиа: {e}")
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
            if any(cmd in text.lower() for cmd in ["хватит", "стоп", "заверши"]):
                self.speech.speak("Завершаю работу")
                sys.exit()

            # Получаем команду из БД
            command = self._get_command_from_db(text)
            if not command:
                self.speech.speak("Команда не распознана")
                return False

            action_type, action_target = command
            status = "success"
            result = False

            # Выполняем действие
            if action_type == 'launch_app':
                if self._launch_app(action_target):
                    app_name = os.path.basename(action_target).split('.')[0]
                    self.speech.speak(f"{app_name} запускается")
                    result = True
                else:
                    self.speech.speak("Не удалось запустить приложение")
                    status = "failed"
            
            elif action_type == 'media_control':
                if self._control_media(action_target):
                    if action_target == 'playpause':
                        self.speech.speak("Музыка приостановлена")
                    elif action_target == 'nexttrack':
                        self.speech.speak("Следующий трек")
                    elif action_target == 'prevtrack':
                        self.speech.speak("Предыдущий трек")
                    result = True
                else:
                    self.speech.speak("Не удалось управлять медиа")
                    status = "failed"
            
            elif action_type == 'close_app':
                if self._close_app(action_target):
                    self.speech.speak(f"Приложение {action_target} закрыто")
                    result = True
                else:
                    self.speech.speak(f"Не удалось закрыть {action_target}")
                    status = "failed"
            
            self._log_command(text, status)
            return result
        
            

        except Exception as e:
            print(f"Критическая ошибка: {e}")
            return False