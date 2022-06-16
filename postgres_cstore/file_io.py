import glob
import os
import pandas as pd
from postgres_cstore.config import Config


class FileIO(object):
    """FileIO class.
    """
    def __init__(self, config: Config) -> None:
        """Initialize FileIO.
        :param config: postgres_cstore.config.Config.
        """
        self.config = config

    def lst_fil(self, pattern):
        """List all files matching a pattern from self.conf.data_dir.
        :param pattern: str. A pattern listed from self.conf.data.dir.
        :return: (list, int).
        """
        files = []
        for root, _, _ in os.walk(self.config.data_dir):
            files = files + glob.glob(os.path.join(root, pattern))
        return files, len(files)

    def ext_dat(self, pattern: str, **kwargs) -> pd.DataFrame:
        """Extract all data in a file list. The file in the list is matching a pattern,
        and read from self.conf.data_dir.
        :param pattern: str. A pattern extracted from self.conf.data_dir.
        :param kwargs: dict. Keyword arguments passed to pd.read_csv.
        :return: pd.DataFrame.
        """
        # List all files matching a pattern from self.conf.data_dir
        files, length = self.lst_fil(pattern=pattern)

        # Iterate over files.
        universe = []
        for i, f in enumerate(files):
            # Extract data from csv files and append pandas.Dataframe.
            universe.append(pd.read_csv(f, **kwargs))
            # Print progress.
            print("{current}/{length} {file} done.".format(current=str(i+1), length=length, file=f))

        # Concatenate all dataframes.
        return pd.concat(universe, sort=False)

    def cat_dat(self, pattern, temporary_file_name, **kwargs):
        """Concatenate all data in a file list. The data is saved as a temporary file.
        :param pattern: str. A pattern extracted from self.conf.data_dir.
        :param temporary_file_name: str. Temporary file name saved in the self.conf.temporary_dir.
        :param kwargs: dict. Keyword arguments passed to pd.read_csv.
        :return: str.
        """
        os.makedirs(self.config.temporary_dir, exist_ok=True)
        temporary_file_path = os.path.join(self.config.temporary_dir, temporary_file_name)
        self.ext_dat(pattern, **kwargs).to_csv(temporary_file_path)
        return temporary_file_path
