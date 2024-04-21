import datetime
import os
import sys
import tempfile
from pathlib import Path

from bot.utils.config_reader import config


PG_RESTORE_COMMAND_TEMPLATE = "pg_restore --clean -U {user} -p {port} -h {host} {database}  {filename}"
PG_DUMP_COMMAND_TEMPLATE = "pg_dump -U {user} -Fc  -p {port} -h {host} {database} > {filename}"
SQLDUMP_FILENAME_TEMPLATE = "server_prod_{now}.bak"
FILENAME_DATETIME_FORMAT = "%Y_%m_%d_%H_%M_%S"


def create_dump_postgres(now):
    now = now.strftime(FILENAME_DATETIME_FORMAT)
    dump_filename = SQLDUMP_FILENAME_TEMPLATE.format(now=now)
    dump_filepath = "dumps/created/" + dump_filename
    command = PG_DUMP_COMMAND_TEMPLATE.format(
        user=config.POSTGRES_USER,
        database=config.POSTGRES_DB,
        port=config.POSTGRES_PORT,
        filename=dump_filepath,
        host=config.POSTGRES_HOST,
    )
    os.environ["PGPASSWORD"] = config.POSTGRES_PASSWORD.get_secret_value()
    result = os.system(command)

    return dump_filepath if result == 0 else False


create_dump_postgres(datetime.datetime.utcnow())


def restore_dump_postgres(file_path):
    PG_PASSWORD = config.POSTGRES_PASSWORD.get_secret_value()
    PG_HOST = config.POSTGRES_HOST
    PG_PORT = config.POSTGRES_PORT
    PG_DB = config.POSTGRES_DB
    PG_USER = config.POSTGRES_USER

    command = f"pg_restore -c -d postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB} -Fc {file_path}"

    # os.environ["PGPASSWORD"] = config.POSTGRES_PASSWORD.get_secret_value()
    result = os.system(command)
    return True if result == 0 else False