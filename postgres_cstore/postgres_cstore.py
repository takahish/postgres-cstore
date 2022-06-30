import json
import os
from collections import OrderedDict
from datetime import datetime
from hashlib import md5

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

    def execute(self, sql: str) -> str:
        """Execute sql.
        :param sql: str.
        :return: str.
        """
        cmd = "psql \"{uri}\" -c \"{sql}\""
        return Process.run(cmd=cmd.format(uri=self.psql_uri, sql=sql))

    def execute_from_file(self, sql_file: str) -> str:
        """Execute sql that is written in file.
        :param sql_file: str.
        :return: str.
        """
        with open(sql_file, 'r') as sql:
            return self.execute(sql=sql.read())

    def execute_from_template(self, sql_template: str, placeholder: dict) -> str:
        """Execute sql that is written in a template with keyword arguments.
        :param sql_template: str.
        :param placeholder: dict.
        :return: str
        """
        with open(sql_template, 'r') as tpl:
            sql = tpl.read().format(**placeholder)
            return self.execute(sql=sql)

    @staticmethod
    def make_query_id() -> str:
        """
        :return: str.
        """
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        return md5(timestamp.encode()).hexdigest()

    @staticmethod
    def json_dump(meta_file: str, dtype: dict) -> str:
        """
        :param meta_file:
        :param dtype:
        :return:
        """
        with open(meta_file, 'w') as f:
            json.dump(dtype, f)
        return meta_file

    @staticmethod
    def json_load(meta_file: str) -> dict:
        """
        :param meta_file:
        :return:
        """
        with open(meta_file, 'r') as f:
            dtype = json.load(f, object_pairs_hook=OrderedDict)
        return dtype

    def extract(self, sql: str, query_id: str, **kwargs) -> pd.DataFrame:
        """Extract data from output of sql as pandas.DataFrame.
        :param sql: str.
        :param query_id: str.
        :return: pandas.DataFrame.
        """
        query_dir = os.path.join(self.config.data_dir, 'query')
        os.makedirs(query_dir, exist_ok=True)
        query_file = os.path.join(query_dir, "{query_id}.csv.gz".format(query_id=query_id))
        meta_file = os.path.join(query_dir, "{query_id}.json".format(query_id=query_id))

        # It should be removed if a compression keyword argument is provided.
        # Because the duplicated keyword becomes a cause of an error when executing pd.read_csv.
        if 'compression' in kwargs:
            _ = kwargs.pop('compression')

        if os.path.isfile(query_file) and os.path.isfile(meta_file):
            # Here is dtype settings. the dtype is loaded from the meta file.
            # It should be removed if a dtype keyword argument is provided.
            # Because the duplicated keyword becomes a cause of an error when executing pd.read_csv.
            dtype = self.json_load(meta_file)
            if 'dtype' in kwargs:
                _ = kwargs.pop('dtype')
            return pd.read_csv(query_file, compression='gzip', dtype=dtype, **kwargs)

        else:
            tmp_file = os.path.join(query_dir, os.path.splitext(os.path.basename(query_file))[0])
            cmd = "psql \"{uri}\" -c \"{sql}\" -A --csv -o {tmp_file} && gzip {tmp_file}"
            _ = Process.run(cmd=cmd.format(uri=self.psql_uri, sql=sql, tmp_file=tmp_file))

            # Here is dtype settings. It gets dtype from kwargs if it is provided as an argument.
            # Otherwise, dtype is loaded from the result and saved as the meta file.
            if 'dtype' in kwargs:
                # It gets dtype from kwargs if it is provided as an argument.
                dtype = kwargs.pop('dtype')
                df = pd.read_csv(query_file, compression='gzip', dtype=dtype, **kwargs)
            else:
                # There is no dtype argument, dtype is defined from results.
                df = pd.read_csv(query_file, compression='gzip', **kwargs)
                dtype = OrderedDict([(i, str(df[i].dtype)) for i in df.columns])

            # Save dtype to meta_file.
            self.json_dump(meta_file, dtype)
            return df

    def extract_from_file(self, sql_file: str, query_id: str, **kwargs) -> pd.DataFrame:
        """Extract data from output of sql as pandas.DataFrame. The sql is written in file.
        :param sql_file: str.
        :param query_id: str.
        :return: pandas.DataFrame.
        """
        with open(sql_file, 'r') as sql:
            return self.extract(query_id=query_id, sql=sql.read(), **kwargs)

    def extract_from_template(self, sql_template: str, placeholder: dict, query_id: str, **kwargs: dict) -> pd.DataFrame:
        """Extract data from output of sql as pandas.DataFrame.
        The sql is written in template with keyword arguments.
        :param sql_template: str.
        :param placeholder: dict.
        :param query_id: str.
        :param kwargs: dict.
        :return: pandas.DataFrame
        """
        with open(sql_template, 'r') as tpl:
            sql = tpl.read().format(**placeholder)
            return self.extract(query_id=query_id, sql=sql, **kwargs)

    def load(self, csv_file: str, schema_name: str, table_name: str) -> str:
        """ Then load method loads data to the table.
        :param csv_file: str.
        :param schema_name: str.
        :param table_name: str.
        :return: str.
        """
        meta = "\\copy {schema_name}.{table_name} from '{csv_file}' with csv"
        return self.execute(sql=meta.format(schema_name=schema_name, table_name=table_name, csv_file=csv_file))
