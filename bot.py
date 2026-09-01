import os

import discord
from discord import app_commands

from dotenv import load_dotenv

load_dotenv()

token: str | None = os.getenv("DISCORD_TOKEN")

if not token:
    raise ValueError("DISCORD_TOKEN environment variable is not set.")

class SimpleMMOCollectorBot(discord.Client):
    def __init__(self):
        intents: discord.Intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        commands = await self.tree.sync()
        print(f"Synced {len(commands)} commands.")

    async def on_ready(self):
        print(f"Logged in as {self.user}")

bot = SimpleMMOCollectorBot()



bot.run(token)