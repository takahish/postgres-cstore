from datetime import datetime
from hashlib import md5
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

    def exe(self, sql: str) -> str:
        """Execute sql.
        :param sql: str.
        :return: str.
        """
        cmd = "psql \"{uri}\" -c \"{sql}\""
        return Process.run(cmd=cmd.format(uri=self.psql_uri, sql=sql))

    def exe_fm_fil(self, sql_file: str) -> str:
        """Execute sql that is written in file.
        :param sql_file: str.
        :return: str.
        """
        cmd = "psql \"{uri}\" -f \"{sql_file}\""
        return Process.run(cmd=cmd.format(uri=self.psql_uri, sql_file=sql_file))

    def exe_fm_tpl(self, sql_template: str, **kwargs: dict) -> str:
        """Execute sql that is written in a template with keyword arguments.
        :param sql_template: str.
        :param kwargs: dict.
        :return: str
        """
        with open(sql_template, 'r') as tpl:
            sql = tpl.read().format(**kwargs)
            return self.exe(sql=sql)

    @staticmethod
    def make_query_id() -> str:
        """
        :return: str.
        """
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        return md5(timestamp.encode()).hexdigest()

    def ext(self, query_id: str, sql: str) -> pd.DataFrame:
        """Extract data from output of sql as pandas.DataFrame.
        :param query_id: str.
        :param sql: str.
        :return: pandas.DataFrame.
        """
        os.makedirs(self.config.out_dir, exist_ok=True)
        out_file = os.path.join(self.config.out_dir, "{query_id}.csv.gz".format(query_id=query_id))
        if os.path.isfile(out_file):
            return pd.read_csv(out_file)
        else:
            tmp_file = os.path.join(self.config.out_dir, os.path.splitext(os.path.basename(out_file))[0])
            cmd = "psql \"{uri}\" -c \"{sql}\" -A --csv -o {tmp_file} && gzip {tmp_file}"
            _ = Process.run(cmd=cmd.format(uri=self.psql_uri, sql=sql, tmp_file=tmp_file))
            return pd.read_csv(out_file, compression='gzip')

    def ext_fm_fil(self, query_id: str, sql_file: str) -> pd.DataFrame:
        """Extract data from output of sql as pandas.DataFrame. The sql is written in file.
        :param query_id: str.
        :param sql_file: str.
        :return: pandas.DataFrame.
        """
        os.makedirs(self.config.out_dir, exist_ok=True)
        out_file = os.path.join(self.config.out_dir, "{query_id}.csv.gz".format(query_id=query_id))
        if os.path.isfile(out_file):
            return pd.read_csv(out_file, compression='gzip')
        else:
            tmp_file = os.path.join(self.config.out_dir, os.path.splitext(os.path.basename(out_file))[0])
            cmd = "psql \"{uri}\" -f \"{sql_file}\" -A --csv -o {tmp_file} && gzip {tmp_file}"
            _ = Process.run(cmd=cmd.format(uri=self.psql_uri, sql_file=sql_file, tmp_file=tmp_file))
            return pd.read_csv(out_file, compression='gzip')

    def ext_fm_tpl(self, query_id: str, sql_template: str, **kwargs: dict) -> pd.DataFrame:
        """Extract data from output of sql as pandas.DataFrame.
        The sql is written in template with keyword arguments.
        :param query_id: str.
        :param sql_template: str.
        :param kwargs: dict.
        :return: pandas.DataFrame
        """
        with open(sql_template, 'r') as tpl:
            sql = tpl.read().format(**kwargs)
            return self.ext(query_id=query_id, sql=sql)

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
