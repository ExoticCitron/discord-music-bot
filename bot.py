import discord
from discord.ext import commands
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(name="https://divisionbot.space/"))
    await bot.tree.sync()
    print(f"Bot is ready. Logged in as {bot.user}")

async def load_extensions():
    await bot.load_extension("cogs.music")
    await bot.load_extension("cogs.volume")
    await bot.load_extension("cogs.queue")
    await bot.load_extension("cogs.help")
    #await bot.load_extension("cogs.youtube")  # beta feature, soon
    #await bot.load_extension("cogs.lyrics")  # beta feature, soon
    #await bot.load_extension("cogs.playlist")  # beta feature, soon
async def main():
    await load_extensions()
    await bot.start("")

if __name__ == "__main__":
    asyncio.run(main())





