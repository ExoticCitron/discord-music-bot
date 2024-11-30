import discord
from discord.ext import commands
from discord import app_commands
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp as youtube_dl
import asyncio
from views.music_control import MusicControl
import json

# fetches spotify playlists in batches of 5 at a time for smoother experiences (wait a lot less and can playback without delay)

"""
with open("configs/embeds.json", "r") as file:
    config = json.load(file)
    disconnect_footer = config["disconnect"]["footer"]
    error_color = (config["error"]["color"], 16)
     # not needed now, will be pushed next update
"""

# Spotify API Setup
SPOTIFY_CLIENT_ID = "" # view git desc for more ingo
SPOTIFY_CLIENT_SECRET = ""

spotify = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

ytdl_format_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch1',
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.music_control_view = None 

    @app_commands.command(name="play", description="Play a Spotify song or playlist in a voice channel.")
    async def play_command(self, interaction: discord.Interaction, url: str):
        if not interaction.user.voice:
            notinVC = discord.Embed(description=f"{interaction.user.mention}, you must be in a **voice channel** to use this command!", color=0xFF0000)
            notinVC.set_footer(text="https://exo-devs.tech/")
            await interaction.response.send_message(embed=notinVC)
            return

        await interaction.response.defer()

        voice_channel = interaction.user.voice.channel
        vc = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if not vc or not vc.is_connected():
            vc = await voice_channel.connect()
        elif vc.channel != voice_channel:
            await vc.move_to(voice_channel)

        guild_id = interaction.guild.id

        if guild_id not in self.song_queue:
            self.song_queue[guild_id] = []

        try:
            queries = await self.get_spotify_track_url(url)

            if not self.song_queue[guild_id]: 
                first_query = queries.pop(0)
                yt_url, yt_title, yt_thumbnail, yt_duration = await self.search_youtube(first_query)
                if yt_url:
                    self.song_queue[guild_id].append({"url": yt_url, "title": yt_title, "thumbnail": yt_thumbnail, "duration": yt_duration})
                    await self.play_next_song(guild_id)
                    nowPlaying = discord.Embed(description=f"Now playing: **{yt_title}**", color=0x32CD32)
                    nowPlaying.set_footer(text="https://exo-devs.tech/")
                    nowPlaying.set_thumbnail(url=yt_thumbnail or (interaction.guild.icon.url if interaction.guild.icon else None))
                    duration = yt_duration
                    progress_bar = f"[{'▬' * 20}] 0:00 / {duration // 60}:{duration % 60:02}"
                    nowPlaying.add_field(name="Duration", value=progress_bar)
                    if self.music_control_view is None or not self.bot.voice_clients:
                        self.music_control_view = MusicControl(interaction.user.id)
                    await interaction.followup.send(embed=nowPlaying, view=self.music_control_view)
                else:
                    print(f"Could not find YouTube URL for query: {first_query}")

            else: 
                for query in queries:
                    yt_url, yt_title, yt_thumbnail, yt_duration = await self.search_youtube(query)
                    if yt_url:
                        self.song_queue[guild_id].append({"url": yt_url, "title": yt_title, "thumbnail": yt_thumbnail, "duration": yt_duration})

                added_tracks_message = discord.Embed(description=f"Added **{len(queries)}** tracks to the queue.", color=0x32CD32)
                await interaction.followup.send(embed=added_tracks_message)

            asyncio.create_task(self.fetch_remaining_tracks(guild_id, queries))

        except Exception as e:
            errorEm = discord.Embed(title=":x: ERROR :x:", description=f"```{e}```\n\nMessage **@exoticcitron** on discord to get this fixed...", color=0xFF0000)
            errorEm.set_footer(text="https://exo-devs.tech/")
            await interaction.followup.send(embed=errorEm)

    @app_commands.command(name="skip", description="Skip the current song or stop playback if the queue is empty.")
    async def skip_command(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            notinVC = discord.Embed(description=f"{interaction.user.mention}, you must be in a **voice channel** to use this command!", color=0xFF0000)
            notinVC.set_footer(text="https://exo-devs.tech/")
            await interaction.response.send_message(embed=notinVC)
            return

        guild_id = interaction.guild.id
        vc = discord.utils.get(self.bot.voice_clients, guild__id=guild_id)

        await interaction.response.defer()

        if vc and vc.is_playing():
            vc.stop()
            if self.song_queue[guild_id]:
                current_song = self.song_queue[guild_id][0]
                nowPlaying = discord.Embed(description=f"Now playing: **{current_song['title']}**", color=0x32CD32)
                nowPlaying.set_footer(text="https://exo-devs.tech/")
                
                if current_song.get('thumbnail'):
                    nowPlaying.set_thumbnail(url=current_song['thumbnail'])
                else:
                    nowPlaying.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
                
                duration = current_song['duration']
                progress_bar = f"[{'▬' * 20}] 0:00 / {duration // 60}:{duration % 60:02}"
                nowPlaying.add_field(name="Duration", value=progress_bar, inline=False)

                await interaction.followup.send(embed=nowPlaying)
                await self.play_next_song(guild_id)  
            else:
                noSongIsPlaying = discord.Embed(description="No song is currently playing", color=0xFF0000)
                noSongIsPlaying.set_footer(text="https://exo-devs.tech/")
                await interaction.followup.send(embed=noSongIsPlaying)
        else:
            noSongIsPlaying = discord.Embed(description="No song is currently playing", color=0xFF0000)
            noSongIsPlaying.set_footer(text="https://exo-devs.tech/")
            await interaction.followup.send(embed=noSongIsPlaying)

    @app_commands.command(name="skipto", description="Skip to a specific song in the queue by number.")
    async def skipto_command(self, interaction: discord.Interaction, song_number: int):
        if not interaction.user.voice:
            await interaction.response.send_message("You must be in a voice channel to use this command.", ephemeral=True)
            return

        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            await interaction.response.send_message("The bot is not currently in a voice channel.", ephemeral=True)
            return

        if interaction.user.voice.channel != vc.channel:
            await interaction.response.send_message("You must be in the same voice channel as the bot to use this command.", ephemeral=True)
            return

        guild_id = interaction.guild.id

        if guild_id not in self.song_queue or not self.song_queue[guild_id]:
            await interaction.response.send_message("The queue is currently empty.", ephemeral=True)
            return

        queue = self.song_queue[guild_id]
        if song_number < 1 or song_number > len(queue):
            await interaction.response.send_message(f"Please provide a valid song number between 1 and {len(queue)}.", ephemeral=True)
            return

        song_to_skip_to = queue[song_number - 1] 
        self.song_queue[guild_id] = queue[song_number - 1:]  

        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop() 

        await self.play_next_song(guild_id)

        await interaction.response.send_message(f"Skipped to **{song_to_skip_to['title']}**.", ephemeral=True)

    async def play_next_song(self, guild_id, message=None):
        vc = discord.utils.get(self.bot.voice_clients, guild__id=guild_id)

        if not vc or not vc.is_connected():
            print(f"Bot is not connected to a voice channel in guild {guild_id}")
            self.music_control_view = None  
            return

        if guild_id in self.song_queue and self.song_queue[guild_id]:
            next_song = self.song_queue[guild_id].pop(0)
            song_url = next_song["url"]
            song_title = next_song["title"]

            try:
                if not vc.is_playing():
                    source = discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(song_url, **ffmpeg_options)
                    )
                    source.volume = self.bot.get_cog('Volume').current_volume

                    def after_playing(error):
                        if error:
                            print(f"Error occurred: {error}")
                        asyncio.run_coroutine_threadsafe(self.play_next_song(guild_id, message), self.bot.loop)

                    vc.play(source, after=after_playing)
                    print(f"Now playing: {song_title}")

                    nowPlaying = discord.Embed(description=f"Now playing: **{song_title}**", color=0x32CD32)
                    nowPlaying.set_footer(text="https://exo-devs.tech/")
                    
                    if next_song.get('thumbnail'):
                        nowPlaying.set_thumbnail(url=next_song['thumbnail'])
                    else:
                        nowPlaying.set_thumbnail(url=vc.guild.icon.url if vc.guild.icon else None)
                    
                    duration = next_song['duration']
                    progress_bar = f"[{'▬' * 20}] 0:00 / {duration // 60}:{duration % 60:02}"
                    nowPlaying.add_field(name="Duration", value=progress_bar, inline=False)

                    if message:
                        await message.edit(embed=nowPlaying)
                else:
                    print(f"Already playing audio in guild {guild_id}.")
            except Exception as e:
                print(f"Failed to play song '{song_title}': {e}")
                await self.play_next_song(guild_id, message)
        else:
            print(f"Queue is empty in guild {guild_id}.")
            self.song_queue[guild_id] = []
            if not vc.is_playing():
                await vc.disconnect()
                self.song_queue[guild_id] = []

    async def search_youtube(self, query):
        loop = asyncio.get_event_loop()
        try:
            info = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
            if info and 'entries' in info:
                entry = info['entries'][0]
                return entry['url'], entry['title'], entry['thumbnail'], entry['duration']
            return (info['url'], info['title'], info.get('thumbnail'), info.get('duration')) if 'url' in info else (None, None, None, None)
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None, None, None, None

    async def get_spotify_track_url(self, spotify_url):
        try:
            if "track" in spotify_url:
                track = spotify.track(spotify_url)
                return [f"{track['name']} {track['artists'][0]['name']}"]
            elif "playlist" in spotify_url:
                playlist = spotify.playlist(spotify_url)
                return [f"{item['track']['name']} {item['track']['artists'][0]['name']}" for item in playlist["tracks"]["items"]]
            elif "album" in spotify_url:
                album = spotify.album(spotify_url)
                return [f"{track['name']} {track['artists'][0]['name']}" for track in album["tracks"]["items"]]
            else:
                raise ValueError("Invalid Spotify URL")
        except Exception as e:
            print(f"Error processing Spotify URL: {e}")
            return []

    async def fetch_remaining_tracks(self, guild_id, queries):
        batch_size = 5
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            for query in batch:
                yt_url, yt_title, yt_thumbnail, yt_duration = await self.search_youtube(query)
                if yt_url:
                    self.song_queue[guild_id].append({"url": yt_url, "title": yt_title, "thumbnail": yt_thumbnail, "duration": yt_duration})
                    print(f"Added batch {i // batch_size + 1} to queue: {yt_title}")
                else:
                    print(f"Could not find YouTube URL for query: {query}")
            await asyncio.sleep(1)

    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user and before.channel is not None and after.channel is None:
            print("Bot has left the voice channel.")
            self.music_control_view = None  

async def setup(bot):
    await bot.add_cog(Music(bot))

