from ferovinum import config as _config, logger as _logger
from ferovinum.util import DatabaseConnection as _DatabaseConnection


with _DatabaseConnection(in_db=False) as db_conn:
    if db_conn.execute(f"SELECT COUNT(*) FROM pg_database WHERE datname='{_config['PostgresDatabaseName']}'")[0]['count'] != 0:
        _logger.info('Database is present')
    else:
        _logger.info('Creating database')
        db_conn.execute(f"CREATE DATABASE {_config['PostgresDatabaseName']}")
        db_conn.execute(f"GRANT ALL PRIVILEGES ON DATABASE {_config['PostgresDatabaseName']} TO {_config['PostgresSuperUserName']}")
