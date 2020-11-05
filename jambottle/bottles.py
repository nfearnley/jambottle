from typing import List
import re

import arrow
import requests
from discord import Embed


class Jam():
    def __init__(self, jamid: int, channelid: int = None, since: arrow.Arrow = None):
        if since is None:
            since = arrow.utcnow()
        self.jamid = jamid
        self.channelid = channelid
        self.since = since

    @property
    def entries_url(self):
        return f"https://itch.io/jam/{self.jamid}/entries.json"

    def reset(self):
        self.since = arrow.get(0)

    def __eq__(self, other):
        return self.jamid == other.jamid and self.channelid == other.channelid

    def to_json(self):
        return {
            "jamid": str(self.jamid),
            "channelid": str(self.channelid),
            "since": str(self.since.timestamp)
        }

    @classmethod
    def from_json(cls, j):
        jamid = int(j["jamid"])
        channelid = int(j["channelid"])
        since = arrow.get(int(j["since"]))
        return cls(jamid, channelid, since)


def scrape_jam(url):
    RE_JAMURL = re.compile(r"(?:https://)?itch\.io/jam/([^/]+)")
    RE_JAMTITLE = re.compile(r'<meta content="([^"]+)" property="og:title"/>')
    RE_JAMID = re.compile(r",\"id\":(\d+)}")
    if not (m := RE_JAMURL.match(url)):
        raise ValueError("Bad URL")
    url = f"https://itch.io/jam/{m.group(1)}"
    page = requests.get(url).text
    if not (m := RE_JAMTITLE.search(page)):
        raise ValueError("Bad URL")
    jam_title = m.group(1)
    if not (m := RE_JAMID.search(page)):
        raise ValueError("Bad URL")
    jam_id = int(m.group(1))
    return jam_id, jam_title


def fetch_entries(jam) -> List["Entry"]:
    j = requests.get(jam.entries_url).json()
    entries = [Entry.from_json(e) for e in j["jam_games"]]
    entries = [e for e in entries if e.created_at > jam.since]
    entries.sort()
    jam.since = arrow.get(j["generated_on"])
    return entries


async def post_entries(channel, entries):
    if not entries:
        return
    for entry in entries:
        await channel.send(embed=entry.to_embed())


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
        e = Embed(
            title=self.title,
            url=self.url,
            description=self.description,
            timestamp=self.created_at.datetime
        )
        e.set_author(name=self.author, url=self.author_url)
        e.set_image(url=self.image_url)
        if self.colour is not None:
            e.colour = self.colour
        return e

    def __lt__(self, other):
        return self.created_at < other.created_at

    @classmethod
    def from_json(cls, j):
        created_at = arrow.get(j["created_at"])
        title = j["game"]["title"]
        author = j["game"]["user"]["name"]
        author_url = j["game"]["user"]["url"]
        url = j["game"]["url"]
        colour_hex = j["game"].get("cover_color")
        colour = int(colour_hex[1:], 16) if colour_hex else None
        image_url = j["game"]["cover"]
        description = j["game"].get("short_text", "")
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
