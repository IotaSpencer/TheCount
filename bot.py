#! /home/ken/.virtualenvs/TheCount/bin/python3.12
from logger import logger
from config import Cfg
import discord
import asyncio
from discord import Game
from discord.ext import commands
from discord.ext.bridge import Bot
from discord.utils import get
import sys

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = Bot(command_prefix="cb!", intents=intents)
# "cogs.count",
startup_extensions = [ 'cogs.count']


async def on_ready():
    pass


@client.event
async def on_ready():
    await client.change_presence(activity=Game(name='a counting game. | cb!'))
    logger.info('---\nLogged in as \nUser: ' + client.user.name + '\nID: ' + str(client.user.id) + '\n---')

# Under maintenance auto-reply



# load cogs


@client.command()
async def load(ctx, string):
    if ctx.author.id not in Cfg().bot_config.bot.owner_ids: return
    string = 'cogs.' + string
    try:
        client.load_extension(string)
        logger.info('Loaded extension \"{}\"'.format(string))
        await ctx.message.channel.send('Loaded extension \"{}\"'.format(string))
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        logger.info('Failed to load extension \"{}\"\n{}'.format(string, exc))
        await ctx.message.channel.send('Failed to load extension \"{}\"'.format(string))


# unload cogs


@client.command()
async def unload(ctx, string):
    if ctx.author.id not in Cfg().bot_config.bot.owner_ids: return
    string = 'cogs.' + string
    try:
        client.unload_extension(string)
        logger.info('Unloaded extension \"{}\"'.format(string))
        await ctx.message.channel.send('Unloaded extension \"{}\"'.format(string))
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        logger.info('Failed to unload extension \"{}\"\n{}'.format(string, exc))


# reload cogs


@client.command()
async def reload(ctx, string):
    if ctx.author.id not in Cfg().bot_config.bot.owner_ids: return
    string = 'cogs.' + string
    try:
        client.unload_extension(string)
        logger.info('Unloaded extension \"{}\"'.format(string))
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        logger.info('Failed to unload extension \"{}\"\n{}'.format(string, exc))
    try:
        client.load_extension(string)
        logger.info('Loaded extension \"{}\"'.format(string))
        await ctx.message.channel.send('Reloaded extension \"{}\"'.format(string))
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        logger.info('Failed to load extension \"{}\"\n{}'.format(string, exc))
        await ctx.message.channel.send('Failed to load extension \"{}\"'.format(string))


# IMPORT EXTENSIONS/COGS
async def load_extensions():
    for extension in startup_extensions:
        try:
            client.load_extension(extension)
            logger.info('Loaded extension \"{}\"'.format(extension))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            logger.info('Failed to load extension \"{}\"\n{}'.format(extension, exc))


# DONE IMPORT EXTENSIONS/COGS


async def main():
    logger.info('\n')
    async with client:
        await load_extensions()
        await client.start(Cfg().bot_config.bot.token)


if __name__ == "__main__":
    asyncio.run(main())
