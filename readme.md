# Jam Bottle
by Natalie Fearnley

A bot that announces new itch.io jam entries to a discord channel

## Requirements
python >= 3.8

## Installation
`pip install jambottle`

## Configuration
Configuration file location:
`"C:\Users\[username]\AppData\Local\Natalie Fearnley\jambottle\conf.json"` on Windows
`/home/[username]/.local/share/jambottle/conf.json` on Linux

Open the file and add a `jamurl` and `webhookurl`.

Optionally you can set a `delay` to the number of minutes you want jambottle to wait between checking for new entries.

An example [conf.json](/examples/conf.json) is available in the examples directory.


## Running
To run the bot just type `jambottle` in the command line.

The bot will check for new entries (by default, every 5 minutes) and then post any new entries in the webhook channel you have provided.

When the bot first runs, it will skip any previous entries, and start posting entries as they are added.

If you stop and restart the bot, it will keep track of where it last left off and continue posting entries from there.

If you'd like to repost all entries from the beginning, just run `jambottle --catchup` to reset the entry tracking.
