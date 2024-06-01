import sqlite3


class DbHandler:
    def __init__(self, db_file):
        # Ініціалізується підключення до бази даних SQLite.
        self.con = sqlite3.connect(db_file)
        # Встановлює зворотний виклик трасування для виводу всіх SQL-запитів.
        # self.con.set_trace_callback(print)

    def prepare_db(self):
        # Створюєьться нова таблиця якщо її не існує 'users' з полями
        # chat_id, state, pictures_amount, color, orientation.
        self.con.execute("""CREATE TABLE  IF NOT EXISTS users(
                                chat_id integer unique,
                                state integer default(0),
                                pictures_amount integer,
                                color,
                                orientation
                             );""")
        # Зберігаються зміни в базі даних.
        self.con.commit()

    def create_user(self, user_id):
        # Спроба додати нового користувача з значеннями за замовчуванням у таблицю 'users'.
        try:
            self.con.execute(f'INSERT INTO users VALUES (?, 0, 1, "", "");', [user_id])
            self.con.commit()
        except sqlite3.DatabaseError as e:
            # Відкатуються зміни у транзакції, якщо виникла помилка.
            self.con.rollback()
            # Виводиться помилка у консоль
            print("[Error] - ", e)

    def get_current_state(self, user_id):
        # Спроба отримати поточний стан користувача з таблиці 'users'.
        try:
            res_raw = self.con.execute("SELECT state FROM users WHERE chat_id=?;", [user_id])
            res = res_raw.fetchone()
            # Якщо користувач не існує, створюється новий користувач і повертається стан за замовчуванням (0).
            if res is None:
                self.create_user(user_id)
                return 0
            else:
                return int(res[0])
        except sqlite3.DatabaseError as e:
            self.con.rollback()
            print("[Error] - ", e)

    def set_column_value(self, chat_id, column, value):
        # Спроба оновити значення зазначеної колонки для даного користувача в таблиці 'users'.
        try:
            self.con.execute(f"UPDATE users SET {column}=? WHERE chat_id=?", (value, chat_id))
            # Фіксує зміни, якщо оновлення успішне.
            self.con.commit()
        except sqlite3.OperationalError as e:
            # Відміняє транзакцію, якщо виникла помилка.
            self.con.rollback()
            print("[Error] - ", e)

    def set_state(self, chat_id, state):
        # Спроба встановити значення стану для даного користувача.
        try:
            entry = self.con.execute("SELECT state FROM users WHERE chat_id=?;", [chat_id]).fetchone()
            # Якщо користувач існує, оновлює значення стану.
            if entry is not None:
                self.set_column_value(chat_id, "state", state)
            else:
                # Якщо користувач не існує, створює нового користувача і встановлює значення стану.
                self.create_user(chat_id)
                self.set_state(chat_id, state)
        except sqlite3.OperationalError as e:
            # Відміняє транзакцію, якщо виникла помилка.
            self.con.rollback()
            print("[Error] - ", e)

    def get_column_value(self, user_id, column):
        # Спроба отримати значення зазначеної колонки для даного користувача.
        try:
            res_raw = self.con.execute(f"SELECT {column} FROM users WHERE chat_id=?;", [user_id])
            res = res_raw.fetchone()[0]
            return res
        except sqlite3.DatabaseError as e:
            # Відміняє транзакцію, якщо виникла помилка.
            self.con.rollback()
            print("[Error] - ", e)
