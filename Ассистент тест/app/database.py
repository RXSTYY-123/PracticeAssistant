import pyodbc
from app.config import DB_CONFIG

class Database:
    def __init__(self):
        try:
            self.conn = pyodbc.connect(
                f"Driver={{{DB_CONFIG['driver']}}};" 
                f"Server={DB_CONFIG['server']};"
                f"Database={DB_CONFIG['database']};"
                "Trusted_Connection=yes;"
                "Encrypt=yes;"
                "TrustServerCertificate=yes;"
            )
            self.cursor = self.conn.cursor()
            print("Успешное подключение к SQL Server!")
        except pyodbc.Error as e:
            print(f"Ошибка подключения: {e}")
            raise

    def get_command(self, trigger_phrase: str):
        try:
            self.cursor.execute(
                "SELECT action_type, action_target FROM commands WHERE trigger_phrase = ?", 
                trigger_phrase
            )
            return self.cursor.fetchone()
        except pyodbc.Error as e:
            print(f"Ошибка при поиске команды: {e}")
            return None

    def log_command(self, command_text: str, status: str):
        try:
            self.cursor.execute(
                "INSERT INTO command_logs (command_text, status, timestamp) VALUES (?, ?, GETDATE())",
                command_text, status
            )
            self.conn.commit()
        except pyodbc.Error as e:
            print(f"Ошибка при логировании команды: {e}")

    def close(self):
        if hasattr(self, 'conn'):
            self.conn.close()