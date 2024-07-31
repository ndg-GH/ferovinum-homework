from csv import DictReader
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlmodel import Session, SQLModel

from ferovinum import config, logger
from ferovinum.database import engine, Client, Product, create_order


class DatabaseConnection:

    def __init__(self, in_db=True):
        fields = (('host', 'PostgresHost'), ('port', 'PostgresPort'),
                  ('user', 'PostgresSuperUserName'), ('password', 'PostgresSuperUserPassword'))
        if in_db:
            fields += (('dbname', 'PostgresDatabaseName'),)
        self.__conn = connect(' '.join(f"{field_name}='{config[config_key]}'"
                                       for field_name, config_key in fields))
        self.__conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

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


def strip_percent(stg):
    if not stg.endswith('%'):
        raise Exception('UnexpectedFormat', stg)
    return stg[:-1]


with DatabaseConnection(in_db=False) as db_conn:
    if db_conn.execute(f"SELECT COUNT(*) FROM pg_database WHERE datname='{config['PostgresDatabaseName']}'")[0]['count'] != 0:
        logger.info('Database is present')
    else:
        logger.info('Creating database')
        db_conn.execute(f"CREATE DATABASE {config['PostgresDatabaseName']}")
        db_conn.execute(f"GRANT ALL PRIVILEGES ON DATABASE {config['PostgresDatabaseName']} TO {config['PostgresSuperUserName']}")

        # create database tables
        SQLModel.metadata.create_all(engine)

        # load database entries
        data_dir_path = Path(__file__).parents[3] / 'data'
        with Session(engine) as session:
            with open(data_dir_path / 'Clients.csv', mode='r') as file_obj:
                for obj_dict in DictReader(file_obj):
                    session.add(Client(id=obj_dict['clientId'], fee=Decimal(strip_percent(obj_dict['fee'])).scaleb(-2)))
            with open(data_dir_path / 'Products.csv', mode='r') as file_obj:
                for obj_dict in DictReader(file_obj):
                    session.add(Product(id=obj_dict['productId'], price=obj_dict['price']))
            session.commit()
        with open(data_dir_path / 'Orders.csv', mode='r') as file_obj:
            for obj_dict in DictReader(file_obj):
                create_order(obj_dict['clientId'], obj_dict['productId'],
                             datetime.strptime(obj_dict['timestamp'], '%Y-%m-%dT%H:%M:%SZ'),
                             obj_dict['type'], int(obj_dict['quantity']))
