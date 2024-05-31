import sqlite3


class DbHandler:
    def __init__(self, db_file):
        self.con = sqlite3.connect(db_file)
        self.con.set_trace_callback(print)

    def prepare_db(self):
        # self.con.execute("CREATE TABLE IF NOT EXISTS users("
        #                  "chat_id integer unique,"
        #                  "state integer default(0),"
        #                  "pictures_amount integer,"
        #                  "color,"
        #                  "orientation"
        #                  ")")

        self.con.execute("DROP TABLE IF EXISTS users;")

        self.con.execute("""CREATE TABLE users(
                                chat_id integer unique,
                                state integer default(0),
                                pictures_amount integer,
                                color,
                                orientation
                             );""")
        self.con.commit()

    def create_user(self, user_id):
        try:
            self.con.execute(f'INSERT INTO users VALUES (?, 0, 1, "", "");', [user_id])
            self.con.commit()
        except sqlite3.DatabaseError as e:
            self.con.rollback()
            print("[Error] - ", e)

    def get_current_state(self, user_id):
        try:
            res_raw = self.con.execute("SELECT state FROM users WHERE chat_id=?;", [user_id])
            res = res_raw.fetchone()
            if res is None:
                self.create_user(user_id)
                return 0
            else:
                return int(res[0])
        except sqlite3.DatabaseError as e:
            self.con.rollback()
            print("[Error] - ", e)

    def set_column_value(self, chat_id, column, value):
        try:
            self.con.execute(f"UPDATE users SET {column}=? WHERE chat_id=?", (value, chat_id))
            self.con.commit()
        except sqlite3.OperationalError as e:
            self.con.rollback()
            print("[Error] - ", e)

    def set_value(self, chat_id, value):
        try:
            entry = self.con.execute("SELECT state FROM users WHERE chat_id=?;", [chat_id]).fetchone()
            if entry is not None:
                self.set_column_value(chat_id, "state", value)
            else:
                self.create_user(chat_id)
                self.set_value(chat_id, value)
        except sqlite3.OperationalError as e:
            self.con.rollback()
            print("[Error] - ", e)

    def get_column_value(self, user_id, column):
        try:
            res_raw = self.con.execute(f"SELECT {column} FROM users WHERE chat_id=?;", [user_id])
            res = res_raw.fetchone()[0]
            return res
        except sqlite3.DatabaseError as e:
            self.con.rollback()
            print("[Error] - ", e)
