import discord
from discord.ext import commands
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="https://exo-devs.tech/"))
    await bot.tree.sync()
    print(f"Bot is ready. Logged in as {bot.user}")

async def load_extensions():
    await bot.load_extension("cogs.music")
    await bot.load_extension("cogs.volume")
    # await bot.load_extension("cogs.queue") - also a beta, will be added in the next update
    #await bot.load_extension("cogs.youtube") - beta, will be added in the next update

async def main():
    await load_extensions()
    await bot.start("yourtoken")

if __name__ == "__main__":
    asyncio.run(main())





