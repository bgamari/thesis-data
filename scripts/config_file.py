import os.path
import json

class Config(object):
    def __init__(self, fname='config.json'):
        self.fname = fname

    def __enter__(self):
        self.config = json.load(open(self.fname)) if os.path.isfile(self.fname) else {}
        return self.config

    def __exit__(self, exc_type, exc, exc_tb):
        json.dump(self.config, open(self.fname, 'w'), indent=4, sort_keys=True)

