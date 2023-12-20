from config.config import Config
from aiogram import Bot
import psycopg2


class DataBase:
    def __init__(self, config: Config) -> None:
        self.user = config.user_db
        self.password = config.password_db
        self.database = config.database
        self.host = config.host_db

    def connect_to_db(self):
        connect = psycopg2.connect(
            dbname=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=5432
        )

        return connect

    def get_users(self):
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute("SELECT user_id FROM users;")
            user_ids = cursor.fetchall()
            return user_ids
        except Exception as e:
            print("Error with SELECT:", e)
        finally:
            cursor.close()
            connect.close()

    def add_users(self, user_id: int, date: str, active: int):
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(f"INSERT INTO users (user_id, active, date) VALUES ({user_id}, {active}, {date});")
            connect.commit()
        except Exception as e:
            print("Error with INSERT:", e)
        finally:
            cursor.close()
            connect.close()

    def user_exists(self, user_id) -> bool:
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(f"SELECT user_id FROM users WHERE user_id = {user_id};")
            user_id = cursor.fetchone()
            return True if user_id else False
        except Exception as e:
            print("Error with CHECK EXISTS:", e)
        finally:
            cursor.close()
            connect.close()

    def set_active(self, active: int, user_id: int):
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(f"UPDATE users SET active = {active} WHERE user_id = {user_id};")
            connect.commit()
        except Exception as e:
            print("Error with UPDATE:", e)
        finally:
            cursor.close()
            connect.close()

    def set_visitors(self):
        pass

    def get_statistics(self):
        pass
