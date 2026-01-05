import discord, logging
from discord.ui import View, Button, Select
from discord import SelectOption
import json

logging.basicConfig(level=logging.DEBUG)
# way better play command, you now get a clean embed with buttons and a dropdown, altho iull edit the dropdown later since it does the same as the buttons
# skipping a song will edit the song to the new embed

"""
with open("configs/embeds.json", "r") as file:
    config = json.load(file)
    disconnect_footer = config["disconnect"]["footer"]
    error_color = int(config["error"]["color"], 16)  # pushed next update on my github keep an eye out
"""
class MusicControl(View):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

    def user_in_same_vc(self, interaction: discord.Interaction) -> bool:
        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
        return interaction.user.voice and vc and interaction.user.voice.channel == vc.channel

    @discord.ui.button(emoji="🔉", style=discord.ButtonStyle.grey)
    async def decrease_volume(self, interaction: discord.Interaction, button: Button):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if not self.user_in_same_vc(interaction):
            embed = discord.Embed(description="You must be in the same voice channel to use this button.", color=0xFF0000)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        volume_cog = interaction.client.get_cog('Volume')
        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)

        if volume_cog.current_volume > 0.0:
            volume_cog.current_volume = max(0.0, volume_cog.current_volume - 0.1)
            if vc.is_playing() and isinstance(vc.source, discord.PCMVolumeTransformer):
                vc.source.volume = volume_cog.current_volume
            embed = discord.Embed(description=f"Volume decreased by 10%. Current volume: {int(volume_cog.current_volume * 100)}%", color=0x32CD32)
        else:
            embed = discord.Embed(description="Volume is already at the minimum (0%).", color=0xFF0000)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.grey)
    async def increase_volume(self, interaction: discord.Interaction, button: Button):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if not self.user_in_same_vc(interaction):
            embed = discord.Embed(description="You must be in the same voice channel to use this button.", color=0xFF0000)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        volume_cog = interaction.client.get_cog('Volume')
        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)

        if volume_cog.current_volume < 1.0:
            volume_cog.current_volume = min(1.0, volume_cog.current_volume + 0.1)
            if vc.is_playing() and isinstance(vc.source, discord.PCMVolumeTransformer):
                vc.source.volume = volume_cog.current_volume
            embed = discord.Embed(description=f"Volume increased by 10%. Current volume: {int(volume_cog.current_volume * 100)}%", color=0x32CD32)
        else:
            embed = discord.Embed(description="Volume is already at the maximum (100%).", color=0xFF0000)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(label="⏸️", style=discord.ButtonStyle.grey)
    async def pause(self, interaction: discord.Interaction, button: Button):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if not self.user_in_same_vc(interaction):
            embed = discord.Embed(description="You must be in the same voice channel to use this button.", color=0xFF0000)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)

        if vc and vc.is_playing():
            vc.pause()
            paused = discord.Embed(description="Music has been paused.", color=0x32CD32)
            await interaction.followup.send(embed=paused, ephemeral=True)
        else:
            nothingToPause = discord.Embed(description="There is no music playing to pause.", color=0xFF0000)
            await interaction.followup.send(embed=nothingToPause, ephemeral=True)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.grey)
    async def resume(self, interaction: discord.Interaction, button: Button):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if not self.user_in_same_vc(interaction):
            embed = discord.Embed(description="You must be in the same voice channel to use this button.", color=0xFF0000)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)

        if vc and vc.is_paused():
            vc.resume()
            resumed = discord.Embed(description="Music has been resumed.", color=0x32CD32)
            await interaction.followup.send(embed=resumed, ephemeral=True)
        else:
            nothingToResume = discord.Embed(description="There is no music paused to resume.", color=0xFF0000)
            await interaction.followup.send(embed=nothingToResume, ephemeral=True)
    
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button: Button):
        if not interaction.response.is_done():
            await interaction.response.defer()

        print(f"User {interaction.user.name} is trying to skip a song.") #debugging stuff XD

        if not self.user_in_same_vc(interaction):
            embed = discord.Embed(description="You must be in the same voice channel to skip a song.", color=0xFF0000)
            await interaction.followup.send(embed=embed, ephemeral=True)
            print(f"User {interaction.user.name} is NOT in the same voice channel. Action denied.")
            return
        
        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)

        if vc:
            print(f"Voice channel: {vc.channel.name}, User's voice channel: {interaction.user.voice.channel.name if interaction.user.voice else 'None'}")
        else:
            print("No voice channel is currently connected.")

        if vc and vc.is_playing():
            vc.stop()
            music_cog = interaction.client.get_cog('Music')
            await music_cog.play_next_song(interaction.guild.id, interaction.message)
            print(f"Song skipped by {interaction.user.name}.")
        else:
            noSongIsPlaying = discord.Embed(description="No song is currently playing", color=0xFF0000)
            noSongIsPlaying.set_footer(text="https://divisionbot.space/")
            await interaction.followup.send(embed=noSongIsPlaying)
            print("No song is currently playing to skip.")
    
    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.danger, row=2)
    async def disconnect(self, interaction: discord.Interaction, button: Button):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if interaction.user.id != self.user_id:
            embed = discord.Embed(description="You do not have permission to disconnect the bot.", color=0xFF0000)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if not self.user_in_same_vc(interaction):
            embed = discord.Embed(description="You must be in the same voice channel to disconnect the bot.", color=0xFF0000)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)

        if vc and vc.is_connected():
            await vc.disconnect()
            music_cog = interaction.client.get_cog('Music')
            music_cog.song_queue[interaction.guild.id] = []
            disconnxion = discord.Embed(description="Disconnected from the voice channel and cleared the queue", color=0x32CD32)
            disconnxion.set_footer(text=disconnect_footer)
            await interaction.followup.send(embed=disconnxion, ephemeral=True)
        else:
            er = discord.Embed(description="The bot is not connected to any voice channel.", color=0xFF0000)
            await interaction.followup.send(embed=er, ephemeral=True)
    
    @discord.ui.select(placeholder="Choose an action...", min_values=1, max_values=1, options=[
       SelectOption(label="Pause", description="Pause the current song", emoji="⏸️"),
       SelectOption(label="Resume", description="Resume the current song", emoji="▶️"),
       SelectOption(label="Skip", description="Skip the current song", emoji="⏭️"),
       SelectOption(label="Disconnect", description="Disconnect the bot", emoji="🔌")
   ])
    async def select_action(self, interaction: discord.Interaction, select: Select):
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        if not self.user_in_same_vc(interaction):
            embed = discord.Embed(description="You must be in the same voice channel to use this menu.", color=0xFF0000)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)

        if select.values[0] == "Pause":
            if vc and vc.is_playing():
                vc.pause()
                paused = discord.Embed(description="Music has been paused.", color=0x32CD32)
                await interaction.followup.send(embed=paused, ephemeral=True)
            else:
                nothingToPause = discord.Embed(description="There is no music playing to pause.", color=0xFF0000)
                await interaction.followup.send(embed=nothingToPause, ephemeral=True)
        elif select.values[0] == "Resume":
            if vc and vc.is_paused():
                vc.resume()
                resumed = discord.Embed(description="Music has been resumed.", color=0x32CD32)
                await interaction.followup.send(embed=resumed, ephemeral=True)
            else:
                nothingToResume = discord.Embed(description="There is no music paused to resume.", color=0xFF0000)
                await interaction.followup.send(embed=nothingToResume, ephemeral=True)
        elif select.values[0] == "Skip":
            if not self.user_in_same_vc(interaction):
                embed = discord.Embed(description="You must be in the same voice channel to skip a song.", color=0xFF0000)
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            if vc and vc.is_playing():
                vc.stop()
                music_cog = interaction.client.get_cog('Music')
                await music_cog.play_next_song(interaction.guild.id, interaction.message)
            else:
                noSongIsPlaying = discord.Embed(description="No song is currently playing", color=0xFF0000)
                noSongIsPlaying.set_footer(text="https://divisionbot.space/")
                await interaction.message.edit(embed=noSongIsPlaying)
        elif select.values[0] == "Disconnect":
            if interaction.user.id != self.user_id:
                noperms = discord.Embed(description="You do not have permission to disconnect the bot.", color=0xFF0000)
                await interaction.followup.send(embed=noperms, ephemeral=True)
                return
            if vc and vc.is_connected():
                await vc.disconnect()
                music_cog = interaction.client.get_cog('Music')
                
                music_cog.song_queue[interaction.guild.id] = []
                disconnxion = discord.Embed(description="Disconnected from the voice channel and cleared the queue", color=0x32CD32)
                disconnxion.set_footer(text=disconnect_footer)
                await interaction.followup.send(embed=disconnxion, ephemeral=True)
            else:
                er = discord.Embed(description="The bot is not connected to any voice channel.", color=0xFF0000)
                await interaction.followup.send(embed=er, ephemeral=True)

