import argparse
import asyncio
from pathlib import Path
import json
from itertools import islice

import appdirs
import arrow
import requests
from discord import Webhook, RequestsWebhookAdapter, Embed
from discord.utils import sleep_until


# https://stackoverflow.com/questions/3992735/python-generator-that-groups-another-iterable-into-groups-of-n/3992765
# https://stackoverflow.com/questions/31164731/python-chunking-csv-file-multiproccessing/31170795#31170795
# https://docs.python.org/3/library/functions.html#iter
def grouper(n, iterable):
    """
    >>> list(grouper(3, 'ABCDEFG'))
    [['A', 'B', 'C'], ['D', 'E', 'F'], ['G']]
    """
    iterable = iter(iterable)
    return iter(lambda: list(islice(iterable, n)), [])


def getdatadir():
    appname = "jambottle"
    appauthor = "Natalie Fearnley"
    datadir = Path(appdirs.user_data_dir(appname, appauthor))
    return datadir


since_path = getdatadir() / "since.json"
conf_path = getdatadir() / "conf.json"


def load_conf():
    try:
        data = conf_path.read_text()
    except FileNotFoundError:
        conf_path.parent.mkdir(parents=True, exist_ok=True)
        conf_path.write_text(json.dumps({"jamurl": "", "webhookurl": "", "delay": 5}, indent=4))
        return None, None
    j = json.loads(data)
    jamurl = j.get("jamurl")
    webhookurl = j.get("webhookurl")
    delay = j.get("delay")
    return jamurl, webhookurl, delay


def load_since():
    try:
        data = since_path.read_text()
    except FileNotFoundError:
        return arrow.utcnow()
    since = arrow.get(json.loads(data)["since"])
    return since


def save_since(since):
    since_path.parent.mkdir(parents=True, exist_ok=True)
    if since is None:
        since_path.unlink(missing_ok=True)
        return
    data = json.dumps({"since": since.timestamp}, indent=4)
    since_path.write_text(data)


class Entry():
    def __init__(self, created_at, title, author, author_url, url, colour, image_url, description):
        self.created_at = created_at
        self.title = title
        self.author = author
        self.author_url = author_url
        self.url = url
        self.colour = colour
        self.image_url = image_url
        self.description = description

    def to_embed(self):
        return (
            Embed(
                title=self.title,
                url=self.url,
                description=self.description,
                colour=self.colour,
                timestamp=self.created_at.datetime
            )
            .set_author(name=self.author, url=self.url)
            .set_image(url=self.image_url)
        )

    @classmethod
    def from_json(cls, j):
        created_at = arrow.get(j["created_at"])
        title = j["game"]["title"]
        author = j["game"]["user"]["name"]
        author_url = j["game"]["user"]["url"]
        url = j["game"]["url"]
        colour = int(j["game"]["cover_color"][1:], 16)
        image_url = j["game"]["cover"]
        description = j["game"]["short_text"]
        return cls(
            created_at=created_at,
            title=title,
            author=author,
            author_url=author_url,
            url=url,
            colour=colour,
            image_url=image_url,
            description=description
        )


def fetch_entries(jamurl, since=None):
    j = requests.get(jamurl).json()
    entries = [Entry.from_json(e) for e in j["jam_games"]]
    if since is not None:
        since = arrow.get(since)
        entries = [e for e in entries if e.created_at > since]
    since = arrow.get(j["generated_on"])
    return since, entries


def post_entries(webhookurl, entries):
    if not entries:
        return
    webhook = Webhook.from_url(webhookurl, adapter=RequestsWebhookAdapter())
    for chunk in grouper(entries, 10):
        webhook.send(embeds=[e.to_embed() for e in chunk])


def get_args():
    parser = argparse.ArgumentParser(description="A bot that announces new itch.io jam entries to a discord channel")
    parser.add_argument("--catchup", dest="catchup", action="store_const", const=True, default=False, help="Repost all previous entries")
    args = parser.parse_args()
    return args.catchup


async def main():
    catchup = get_args()

    jamurl, webhookurl, delay = load_conf()
    missing_conf = []
    if not jamurl:
        missing_conf.append("jamurl")
    if not webhookurl:
        missing_conf.append("webhookurl")
    if missing_conf:
        print(f"Please add {' and '.join(missing_conf)} to the config file: {conf_path}")
        return

    if catchup:
        since = None
    else:
        since = load_since()

    while True:
        print("Checking for new entries")
        since, entries = fetch_entries(jamurl, since)
        print(f"Found {len(entries)} new entries")
        post_entries(webhookurl, entries)
        save_since(since)
        next_time = since.shift(minutes=delay or 5)
        print(f"Next check is {next_time.humanize()}")
        await sleep_until(next_time)


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    print("Goodbye!")


if __name__ == "__main__":
    run()
