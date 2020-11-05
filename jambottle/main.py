from discord import Permissions
from discord.ext import commands, tasks
from discord.utils import oauth_url

from jambottle.conf import Config
from jambottle.bottles import Jam, scrape_jam, fetch_entries, post_entries

bot = commands.Bot(command_prefix=".jam ")
started = False


def on_first_ready():
    check_loop.start()
    print(f"{bot.user} has successfully logged in.")


@bot.event
async def on_ready():
    global started
    if not started:
        on_first_ready()
    started = True


@bot.command()
async def invite(ctx):
    url = oauth_url(bot.user.id, Permissions(read_messages=True, send_messages=True, embed_links=True))
    await ctx.send(url)


@bot.command()
async def watch(ctx, jamurl: str):
    conf = Config.load()
    jam_id, jam_title = scrape_jam(jamurl)
    jam = Jam(jam_id, ctx.channel.id)
    if jam in conf.jams:
        await ctx.send(f"Already watching {jam_title}")
        return
    conf.jams.append(jam)
    conf.save()
    await ctx.send(f"Now watching {jam_title}")


@bot.command()
async def unwatch(ctx, jamurl: str):
    conf = Config.load()
    jam_id, jam_title = scrape_jam(jamurl)
    jam = Jam(jam_id, ctx.channel.id)
    if jam not in conf.jams:
        await ctx.send(f"Not watching {jam_title}")
        return
    conf.jams.remove(jam)
    conf.save()
    await ctx.send(f"No longer watching {jam_title}")
    # TODO: Add `.jam unwatch`


@bot.command()
async def reset(ctx, jamurl):
    conf = Config.load()
    jam_id, jam_title = scrape_jam(jamurl)
    jam = Jam(jam_id, ctx.channel.id)
    if jam not in conf.jams:
        await ctx.send(f"Not watching {jam_title}")
        return
    jam = conf.jams[conf.jams.index(jam)]
    jam.reset()
    conf.save()
    await ctx.send(f"Reset {jam_title}")


@tasks.loop(minutes=5)
async def check_loop():
    conf = Config.load()
    print("Checking for new entries")
    for jam in conf.jams:
        entries = fetch_entries(jam)
        print(f"Found {len(entries)} new entries for jamid {jam.jamid}")
        channel = bot.get_channel(jam.channelid)
        await post_entries(channel, entries)
    conf.save()


def main():
    conf = Config.load()
    bot.run(conf.discord_token)


if __name__ == "__main__":
    main()
