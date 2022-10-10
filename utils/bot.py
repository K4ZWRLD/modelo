import logging
import logging.handlers
from aiohttp import ClientSession
import os
from dotenv import load_dotenv
import datetime
from .db import Database
import topgg
db = Database()

load_dotenv()

from typing import Dict, List, Optional

import discord
from discord.ext import commands, tasks

class ModMail(commands.Bot):
    def __init__(
        self,
        *args,
        initial_cogs: List[str],
        client: ClientSession,
        debug: bool = False,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.client = client
        self.debug = debug
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_cogs

    async def setup_hook(self) -> None:

        for extension in self.initial_extensions:
            await self.load_extension(f"cogs.{extension}")

        # if debug is enabled, then don't sync slash commands
        if not self.debug:
            print("Syncing slash commands...")
            await self.tree.sync()
            print("Slash commands synced!")
        else:
            pass

    async def on_message(self, message):
        if message.author.bot:
            return
        # check debug mode
        devs = [542798185857286144, 321750582912221184]
        if self.debug:
            # check if the message is from a developer
            if message.author.id not in devs:
                embed = discord.Embed(title='Debug', description=f'Please wait till the bot is out of debug mode\n\n', color=0xff00c8)
                embed.add_field(
                name="‎",
                value=f"[Github](https://github.com/DeveloperJosh/ModMail) | [Support Server](https://discord.gg/TeSHENet9M) | [Old Bot](https://github.com/DeveloperJosh/MailHook)",
                inline=False
                 )
                await message.channel.send(embed=embed)
                return
            elif message.author.id in devs:
                await self.process_commands(message)
        else:
            await self.process_commands(message)

async def main():

    logging.basicConfig(level=logging.INFO)
    # log to file
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    time = datetime.datetime.now()
    handler = logging.handlers.RotatingFileHandler(
        # save to logs folder
        filename=f"logs/{time.strftime('%Y-%m-%d')}.log",
        encoding="utf-8", 
        mode="a", 
        maxBytes=10 * 1024 * 1024, 
        backupCount=5
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.emojis = True
    intents.emojis_and_stickers = True
    intents.bans = True
    intents.webhooks = True
    ext = ['modmail', 'errors', 'developer', 'config', 'snippet', 'help', 'info']
    async with ClientSession() as server_client:
     async with ModMail(command_prefix="?", allowed_mentions=discord.AllowedMentions(everyone=False, roles=True, users=True, replied_user=True),  activity=discord.Game("DM for support"), owner_ids=[542798185857286144, 321750582912221184], help_command=None, client=server_client, debug=False, intents=intents, testing_guild_id=884470177176109056, initial_cogs=ext) as bot:
      token = os.getenv("DISCORD_TOKEN")
      await bot.start(f"{token}", reconnect=True)