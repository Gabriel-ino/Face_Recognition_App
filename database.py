import sqlite3 as sql


class DataBase:
    def __init__(self):
        self.db_conn = sql.connect('profiles.db')
        self.cursor = self.db_conn.cursor()
        self.initialize()

    def initialize(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                            "name TEXT, password TEXT)")

    def verify_username(self, username) -> bool:
        self.cursor.execute("SELECT name FROM users")
        return True if username in self.cursor.fetchall()[0] else False

    def add_user(self, username, password):
        if self.verify_username(username):
            print("User already exists! Try again")
        else:
            self.cursor.execute("INSERT INTO users(name, password) VALUES(?,?)", (username, password))
            self.db_conn.commit()

    def check_login(self, username: str, password: str):
        self.cursor.execute("SELECT * FROM users")
        data = self.cursor.fetchall()
        for info in data:
            if username == info[1] and password == info[2]:
                return True

        return False

    def close_connection(self):
        self.cursor.close()
        self.db_conn.close()


class User:
    def __init__(self, name: str, password: str, trying_login: bool):
        self.name = name
        self.password = password
        self.trying_login = trying_login


