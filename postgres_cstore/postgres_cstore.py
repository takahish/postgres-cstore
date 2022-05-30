import configparser
from datetime import datetime
import os
import pandas as pd
from postgres_cstore.process import Process

# Load configurations
config = configparser.ConfigParser()
config.read('conf/system.ini')


class PostgresCstore(object):
    """PostgresCstore class.
    """
    def __init__(self,
                 name=None, image=None, version=None, volume=None,  # Container settings.
                 user=None, password=None, host=None, port=None, database=None  # Connection settings.
                 ) -> None:
        """Initialize container.
        :param name: str. A container is created from a docker image specified by an image argument.
        :param image: str. An image is based by a container.
        :param version: str. It is a version of a docker image specified by an image argument.
        :param volume: str. It is a volume of a container.
        :param user: str. It is a user of postgres-cstore.
        :param password: str. It is password of a user.
        :param host:
        :param port: str. A port is used by postgres-cstore.
        :param database:
        """
        # Set container settings.
        self.name = name if name is not None else config.get('CONTAINER', 'name')
        self.image= image if image is not None else config.get('CONTAINER', 'image')
        self.version = version if version is not None else config.get('CONTAINER', 'version')
        self.volume = volume if volume is not None else config.get('CONTAINER', 'volume')

        # Set connection settings.
        self.user = user if user is not None else config.get('CONNECTION', 'user')
        self.password = password if password is not None else config.get('CONNECTION', 'password')
        self.host = host if host is not None else config.get('CONNECTION', 'host')
        self.port = port if port is not None else config.get('CONNECTION', 'port')
        self.database = database if database is not None else config.get('CONNECTION', 'database')

        # Set command-line execution.
        self.psql_uri = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )

    def exec(self, sql: str) -> str:
        """Execute sql.
        :param sql: str.
        :return: str.
        """
        cmd = "psql \"{uri}\" -c \"{sql}\""
        return Process.run(cmd=cmd.format(uri=self.psql_uri, sql=sql))

    def exec_from_file(self, sql_file: str) -> str:
        """Execute sql that is written in file.
        :param sql_file: str.
        :return: str.
        """
        cmd = "psql \"{uri}\" -f \"{sql_file}\""
        return Process.run(cmd=cmd.format(uri=self.psql_uri, sql_file=sql_file))

    def ext(self, sql: str) -> str:
        """Extract data from output of sql as pandas.DataFrame.
        :param sql: str
        :return: pandas.DataFrame.
        """
        tmp_dir = os.path.join(os.path.expanduser("~"), ".postgres_cstore", "tmp", "undefined")
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_file = os.path.join(tmp_dir,
                                "{timestamp}.csv".format(timestamp=datetime.now().strftime('%Y%m%d%H%M%S')))
        cmd = "psql \"{uri}\" -c \"{sql}\" -A --csv -o {tmp_file}"
        _ = Process.run(cmd=cmd.format(uri=self.psql_uri, sql=sql, tmp_file=tmp_file))
        return pd.read_csv(tmp_file)

    def ext_from_file(self, sql_file: str) -> str:
        """Extract data from output of sql as pandas.DataFrame. The sql is written in file.
        :param sql_file: str
        :return: pandas.DataFrame.
        """
        tmp_dir = os.path.join(os.path.expanduser("~"), ".postgres_cstore", "tmp",
                               os.path.splitext(os.path.basename(sql_file))[0])
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_file = os.path.join(tmp_dir,
                                "{timestamp}.csv".format(timestamp=datetime.now().strftime('%Y%m%d%H%M%S')))
        cmd = "psql \"{uri}\" -f \"{sql_file}\" -A --csv -o {tmp_file}"
        _ = Process.run(cmd=cmd.format(uri=self.psql_uri, sql_file=sql_file, tmp_file=tmp_file))
        return pd.read_csv(tmp_file)

    def load(self, csv_file: str, target_table: str) -> str:
        """
        :param csv_file:
        :param table:
        :return:
        """
        cmd = "psql \"{uri}\" -c \"{meta}\""
        meta = "\\copy {target_table} from '{csv_file}' with csv"
        return Process.run(cmd.format(uri=self.psql_uri,
                                      meta=meta.format(target_table=target_table, csv_file=csv_file)))
