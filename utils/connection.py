import sqlite3

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = sqlite3.connect("database.sqlite", check_same_thread=False)
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    @classmethod
    def close(cls):
        if cls._instance is not None:
            cls._instance.connection.close()
            cls._instance = None
