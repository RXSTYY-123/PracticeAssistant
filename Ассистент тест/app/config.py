import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'driver': os.getenv('DB_DRIVER', 'ODBC Driver 18 for SQL Server'),
    'server': os.getenv('DB_SERVER', 'localhost'),
    'database': os.getenv('DB_NAME', 'VoiceAssistantDB'),
}

# Настройки VK
VK_TOKEN = os.getenv('vk1.a.68aPh3mwZJqlMsHjreqpp1WC00dETBUGfWiqHpa0ZiAH1vfbP_KHsMhG_W3BRW1OKUI6baOQ18sz2l5JaaWy2U4evpFyQhnlx_RCz-fr-NtByPRkTUKw0UMOxfqlxL9ngDetQ-FSOSdPNlmkHVoZXrLsQM6S3B_IFhYtCnpJ-Ckgjc7cszjMpAtEZZGYl2Rh')

# Ключевые слова для активации
TRIGGER_WORDS = ['эй комп', 'компик', 'ассистент']