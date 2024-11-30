import discord
from discord.ext import commands
from discord import app_commands

class Volume(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_volume = 1.0

    @app_commands.command(name="volume", description="Change the volume of the current song")
    async def volume(self, interaction: discord.Interaction, volume_level: int):
        if volume_level < 0 or volume_level > 100:
            setVolume = discord.Embed(description="Please enter a number between 0 and 100.", color=0xFF0000)
            await interaction.response.send_message(embed=setVolume, ephemeral=True)
            return

        vc = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if vc and vc.is_connected():
            self.current_volume = volume_level / 100.0
            if vc.is_playing() and isinstance(vc.source, discord.PCMVolumeTransformer):
                vc.source.volume = self.current_volume
            setVolume = discord.Embed(description=f"Volume set to {volume_level}%", color=0x32CD32)
        else:
            setVolume = discord.Embed(description="The bot is not connected to any voice channel.", color=0xFF0000)

        await interaction.followup.send(embed=setVolume, ephemeral=True)

    @app_commands.command(name="currentvolume", description="Show the current volume of the song")
    async def currentvolume(self, interaction: discord.Interaction):
        current_volume_percentage = int(self.current_volume * 100)
        currentVol = discord.Embed(description=f"Current volume is set to {current_volume_percentage}%.", color=0x7289da)
        currentVol.set_footer(text="https://exo-devs.tech/")
        await interaction.response.send_message(embed=currentVol)

async def setup(bot):
    await bot.add_cog(Volume(bot))

