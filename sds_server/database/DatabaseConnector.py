import json

from mysql.connector import connect, Error


class DatabaseConnector:
    def __init__(self):
        # Загрузка данных из файла конфигурации
        with open('config.json') as file:
            config = json.load(file)

        # Получение данных для подключения к БД
        self._host = config['DB_HOST']
        self._username = config['DB_USERNAME']
        self._password = config['DB_PASSWORD']
        self._database = config['DB_DATABASE']

        self._connection = None

    def connect(self):
        self._connection = connect(
            host=self._host,
            user=self._username,
            password=self._password,
            database=self._database
        )

    def disconnect(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def execute_query(self, query):
        if self._connection is None:
            raise Exception("Нет установленого соединения с сервером базы данных")

        with self._connection.cursor() as cursor:
            # Выполнение запроса к БД
            cursor.execute(query)
            # Получение имен столбцов результата
            columns = [column[0] for column in cursor.description]
            # Преобразование результа в коллекцию словарей
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return rows
