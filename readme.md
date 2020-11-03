# Jam Bottle
by Natalie Fearnley

A bot that announces new itch.io jam entries to a discord channel

## Requirements
python >= 3.8

## Installation
type `pip install jambottle`

## Configuration
The configuration file is at 
`"C:\Users\[username]\AppData\Local\Natalie Fearnley\jambottle\conf.json"` on Windows
and `/home/[username]/.local/share/jambottle/conf.json` on Linux

Open the file and add a `jamurl` and `webhookurl`.

Optionally you can set a `delay` to the number of minutes you want jambottle to wait between checks.

An example conf.json is available in the [/examples](/examples) directory.


## Running
To run the bot just type `jambottle` in the command line.

It will check for new entries (by default, every 5 minutes) and then post any new entries in the webhook channel you have provided.

Once the bot first runs, it will skip any previous entries, and only post new entries from that time going forward.

If you'd like to repost all entries from the beginning, run `jambottle --catch` to reset the entry tracking.
