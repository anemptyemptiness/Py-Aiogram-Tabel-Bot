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

    def add_users(self, user_id: int) -> None:
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute(f"INSERT INTO users (user_id) VALUES ({user_id});")
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

    def set_data(self, user_id: int, date: str, name: str, place: str, count: int) -> None:
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute("INSERT INTO visitors (user_id, date, name, place, count) "
                           f"VALUES ({user_id}, '{date}', '{name}', '{place}', {count});")
            connect.commit()
        except Exception as e:
            print("Error with INSERT:", e)
        finally:
            cursor.close()
            connect.close()

    def get_statistics(self, date_from: str, date_to: str):
        connect = self.connect_to_db()
        cursor = connect.cursor()

        try:
            cursor.execute("SELECT v.user_id, v.place, v.name, SUM(v.count) "
                           "FROM visitors AS v "
                           f"WHERE v.date BETWEEN '{date_from}' AND '{date_to}' "
                           "GROUP BY v.user_id, v.place, v.name "
                           "ORDER BY 2;")
            row = cursor.fetchall()
            return row
        except Exception as e:
            print("Error with statistics:", e)
            return ["-----"]
        finally:
            cursor.close()
            connect.close()
