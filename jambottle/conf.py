import json
from pathlib import Path

import appdirs

from jambottle.bottles import Jam


def getdatadir():
    appname = "jambottle"
    appauthor = "Natalie Fearnley"
    datadir = Path(appdirs.user_data_dir(appname, appauthor))
    return datadir


conf_path = getdatadir() / "conf.json"


class Config():
    def __init__(self, discord_token=None, jams=None):
        self.discord_token = discord_token or ""
        self.jams = jams or []

    def save(self):
        conf_path.parent.mkdir(parents=True, exist_ok=True)
        conf_path.write_text(json.dumps(self.to_json(), indent=4))

    def to_json(self):
        return {
            "discord_token": self.discord_token,
            "jams": [jam.to_json() for jam in self.jams]
        }

    @classmethod
    def load(cls):
        try:
            conf = cls.from_json(json.loads(conf_path.read_text()))
        except FileNotFoundError:
            # use default configuration
            conf = cls()
            conf.save()
        return conf

    @classmethod
    def from_json(cls, j):
        discord_token = j["discord_token"]
        jams = [Jam.from_json(jam) for jam in j.get("jams")]
        return cls(discord_token, jams)
