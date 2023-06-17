import json

from mysql.connector import connect, Error


class DatabaseConnector:
    def __init__(self):
        # Загрузка данных из файла конфигурации
        with open('config.json') as file:
            config = json.load(file)

        # Получение данных для подключения к БД
        self.host = config['DB_HOST']
        self.username = config['DB_USERNAME']
        self.password = config['DB_PASSWORD']
        self.database = config['DB_DATABASE']

        self.connection = None

    def connect(self):
        self.connection = connect(
            host=self.host,
            user=self.username,
            password=self.password,
            database=self.database
        )

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def execute_query(self, query):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            # Получение имен столбцов
            columns = [column[0] for column in cursor.description]
            # Преобразование результатов в словари
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            return rows
