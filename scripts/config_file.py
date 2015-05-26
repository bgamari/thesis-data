import os.path
import copy
import json

class Config(object):
    def __init__(self, fname='config.json'):
        self.fname = fname

    def __enter__(self):
        self.config = json.load(open(self.fname)) if os.path.isfile(self.fname) else {}
        self.initial_config = copy.deepcopy(self.config)
        return self.config

    def __exit__(self, exc_type, exc, exc_tb):
        if self.initial_config != self.config:
            json.dump(self.config, open(self.fname, 'w'), indent=4, sort_keys=True)
