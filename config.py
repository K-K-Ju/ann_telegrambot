from enum import Enum

TELEGRAM_TOKEN = "7026289899:AAHdbq8hr1fJR2UQ06lu4zK62ikBc-DLG4k"
UNSPLASH_URL = "https://api.unsplash.com/search/photos"
UNSPLASH_TOKEN = '5yndG8uj-iKcu-XqYjweEjpvUYsNoDdBbeZpC6VjfzM'
DB_FILE = "database.db"
# OPENAI_TOKEN = "sk-proj-FpDQxcC8lZtyLkLitNBvT3BlbkFJBVMWcQQChJjFHHUiA7Dy"


class States(Enum):
    S_FREE = 0
    S_ENTER_AMOUNT = 1
    S_SEND_PIC = 2
