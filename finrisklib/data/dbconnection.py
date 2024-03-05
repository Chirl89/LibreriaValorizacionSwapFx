"""
Este módulo está enfocado en la creación de conexiones a servidores SQL.
"""

import pandas as pd
from sqlalchemy import create_engine


class SQLConn:
    """Conexión SQL

    Se encarga de generar conexiones y ejecutar consultas a bases de datos

    :param ip: IP del servidor.
    :type ip: str.
    :param database: Nombre de la base de datos.
    :type database: str.
    :param username: Nombre de usuario. (default None)
    :type username: str.
    :param password: Password. (default None)
    :type password: str.
    """

    def __init__(self, ip: str, database: str, username: str = None, password: str = None):
        """Inicializador"""
        self.ip = ip
        self.database = database
        self.username = username
        self.password = password

    def get_conn_string(self) -> str:
        """Obtener cadena de conexión

        Genera una cadena de conexión standard utilizando los datos provistos. En caso no se haya provisto un nombre de
        usuario se genera una cadena por Trusted Connection.

        :return: Cadena de conexión
        """

        """if self.username is not None:
            conn_str = f'mssql+pyodbc://{self.username}:{self.password}@{self.ip }/{self.database}?driver=SQL+Server'
        else:
            conn_str = f'mssql+pyodbc://{self.ip}/{self.database}?driver=SQL+Server'
        """
        conn_str = f'mssql+pyodbc://{"USR_CMBB7434"}:{"123"}@{self.ip}/{self.database}?driver=SQL+Server'
        return conn_str

    def execute_query(self, query: str) -> pd.DataFrame:
        """Ejecutar Query

        Ejecuta la query proporcionada utilizando la conexión interna.

        :param query: Query a ser ejecutada.
        :type query: str.

        :return: Dataframe con resultado de la query
        """
        conn_string = self.get_conn_string()
        engine = create_engine(conn_string)
        return pd.read_sql(query, engine)

    def save_data(self, table_name: str, data: pd.DataFrame):
        """Guardar Datos

        Guarda los datos proporcionados en la tabla asignada.

        :param table_name: Nombre de la tabla donde se guardará la información.
        :type table_name: str
        :param data: Dataframe con datos a guardar.
        :type data: Dataframe
        """
        engine = create_engine(self.get_conn_string())
        data.to_sql(name=table_name, con=engine, schema='dbo', if_exists='append', index=False)

    @staticmethod
    def get_b08_conn():
        """Obtener conexión a servidor B08

        Obtiene la conexión a la base de Datos B08

        :return: SQLConn
        """
        ip = '10.181.139.41'
        database = 'Banco'
        return SQLConn(ip=ip, database=database)
