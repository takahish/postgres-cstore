from datetime import datetime
import os
import pandas as pd
from postgres_cstore.config import Config
from postgres_cstore.process import Process


class PostgresCstore(object):
    """PostgresCstore class.
    """
    def __init__(self, config: Config) -> None:
        """Initialize container.
        :param config: Configuration of postgres-cstore.
        """
        # Set an instance attribution as a delegation.
        self.config = config

        # Set URI for command-line execution.
        self.psql_uri = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            user=self.config.user,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port,
            database=self.config.database
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

    def ext(self, sql: str) -> pd.DataFrame:
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

    def ext_from_file(self, sql_file: str) -> pd.DataFrame:
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
        """ Then load method loads data to the table.
        :param csv_file: str
        :param target_table: str
        :return: str
        """
        cmd = "psql \"{uri}\" -c \"{meta}\""
        meta = "\\copy {target_table} from '{csv_file}' with csv"
        return Process.run(cmd.format(uri=self.psql_uri,
                                      meta=meta.format(target_table=target_table, csv_file=csv_file)))
