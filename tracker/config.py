import os
from os.path import expanduser, dirname, exists, join
from tinydb import TinyDB

def get_config_root() -> str:
    _root = expanduser('~/.config/tracker-cli')
    exists(_root) or os.makedirs(_root, exist_ok=True)  # type: ignore[func-returns-value]
    return _root

def get_data_file(create_file: bool = False):
    """
    Returns the path to the TinyDB JSON data file. Uses the TRACKER_DATA_FILE environment variable if set,
    otherwise defaults to ~/.config/tracker-cli/data.json. If the default file doesn't exist, create the directory first.
    """
    path = os.environ.get('TRACKER_DATA_FILE')

    if path is None:
        path = join(get_config_root(), 'data.json')

    if not exists(path) and create_file:
        with open(path, 'w') as f:
            f.write('')

    return path

class DB:
    def __init__(self):
        self.db = None

    def __enter__(self):
        self.db = TinyDB(get_data_file(True))
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db is not None:
            self.db.close()
