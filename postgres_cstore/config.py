import configparser
from dataclasses import dataclass

# Load configurations
_config = configparser.ConfigParser()
_config.read('conf/system.ini')


@dataclass
class Config:
    # Set container settings.
    name: str = _config.get('CONTAINER', 'name')
    image: str = _config.get('CONTAINER', 'image')
    version: str = _config.get('CONTAINER', 'version')
    volume: str = _config.get('CONTAINER', 'volume')

    # Set connection settings.
    user: str = _config.get('CONNECTION', 'user')
    password: str = _config.get('CONNECTION', 'password')
    host: str = _config.get('CONNECTION', 'host')
    port: str = _config.get('CONNECTION', 'port')
    database: str = _config.get('CONNECTION', 'database')

    # Set system settings.
    data_dir: str = _config.get('SYSTEM', 'data_dir')
    temporary_dir: str = _config.get('SYSTEM', 'temporary_dir')
