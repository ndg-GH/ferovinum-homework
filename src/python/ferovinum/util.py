from psycopg2 import connect as _connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT as _ISOLATION_LEVEL_AUTOCOMMIT

from . import config as _config


class DatabaseConnection:

    def __init__(self, in_db=True):
        fields = (('host', 'PostgresHost'), ('port', 'PostgresPort'),
                  ('user', 'PostgresSuperUserName'), ('password', 'PostgresSuperUserPassword'))
        if in_db:
            fields += (('dbname', 'PostgresDatabaseName'),)
        self.__conn = _connect(' '.join(f"{field_name}='{_config[config_key]}'"
                                        for field_name, config_key in fields))
        self.__conn.set_isolation_level(_ISOLATION_LEVEL_AUTOCOMMIT)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__conn.close()

    def execute(self, query, vars=None):
        with self.__conn.cursor() as cursor:
            cursor.execute(query, vars=vars)
            if cursor.description is not None:
                columns = tuple(col.name for col in cursor.description)
                return tuple(dict(zip(columns, values)) for values in cursor.fetchall())

    def executemany(self, query, values):
        with self.__conn.cursor() as cursor:
            cursor.executemany(query, values)

    def close(self):
        self.__conn.close()
