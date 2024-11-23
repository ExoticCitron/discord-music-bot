import discord
from discord.ext import commands
from discord import app_commands
from spotipy import Spotify # pip install spotipy to resolve dependency issues
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp as youtube_dl
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG) # not needed unless ur devving it

intents = discord.Intents.all()
client = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
current_volume = 1.0

@client.event
async def on_ready():
    await client.tree.sync()
    print(f"Bot is ready. Logged in as {client.user}")

#add api keys here
SPOTIFY_CLIENT_ID = ""
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

# global song queue XD, if ur using a bigger server(s) switch to a db package liek tinydb
song_queue = {}

async def play_next_song(guild_id):
    """Plays the next song in the queue for the specified guild."""
    vc = discord.utils.get(client.voice_clients, guild__id=guild_id)

    if not vc or not vc.is_connected():
        print(f"Bot is not connected to a voice channel in guild {guild_id}")
        return

    if guild_id in song_queue and song_queue[guild_id]:
        next_song = song_queue[guild_id].pop(0)
        song_url = next_song["url"]
        song_title = next_song["title"]

        try:
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(song_url, **ffmpeg_options)
            )
            source.volume = current_volume

            def after_playing(error):
                if error:
                    print(f"Error during playback: {error}")
                future = asyncio.run_coroutine_threadsafe(play_next_song(guild_id), client.loop)
                try:
                    future.result()
                except Exception as e:
                    print(f"Error running next song coroutine: {e}")

            vc.play(source, after=lambda e: after_playing(e))
            print(f"Now playing: {song_title}")
        except Exception as e:
            print(f"Failed to play song '{song_title}': {e}")
            await play_next_song(guild_id)  
    else:
        print(f"Queue is empty in guild {guild_id}.")
        if not vc.is_playing():
            await vc.disconnect()

async def search_youtube(query):
    """Search YouTube for the given query and return the audio URL and title."""
    try:
        info = ytdl.extract_info(query, download=False)
        if info and 'entries' in info:
            entry = info['entries'][0]
            return entry['url'], entry['title']
        return (info['url'], info['title']) if 'url' in info else (None, None)
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return None, None

async def get_spotify_track_url(spotify_url):
    """Convert Spotify track, album, or playlist URL into a list of YouTube search queries."""
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

@client.tree.command(name="play", description="Play a Spotify song or playlist in a voice channel.")
async def play_command(interaction: discord.Interaction, url: str):
    if not interaction.user.voice:
        await interaction.response.send_message("You must be in a voice channel to use this command.", ephemeral=True)
        return

    await interaction.response.defer()  

    voice_channel = interaction.user.voice.channel
    vc = discord.utils.get(client.voice_clients, guild=interaction.guild)

    if not vc or not vc.is_connected():
        vc = await voice_channel.connect()
    elif vc.channel != voice_channel:
        await vc.move_to(voice_channel)

    guild_id = interaction.guild.id

    if guild_id not in song_queue:
        song_queue[guild_id] = []

    try:
        # extrat Spotify track queries
        queries = await get_spotify_track_url(url)
        for query in queries:
            yt_url, yt_title = await search_youtube(query)
            if yt_url:
                song_queue[guild_id].append({"url": yt_url, "title": yt_title})
            else:
                print(f"Could not find YouTube URL for query: {query}")

        if not vc.is_playing() and song_queue[guild_id]:
            current_song = song_queue[guild_id][0] if song_queue[guild_id] else None
            if current_song:
                await interaction.followup.send(f"Now playing: {current_song['title']}")
            await play_next_song(guild_id)
        else:
            await interaction.followup.send(f"Queued {len(queries)} track(s) from Spotify.")
    except Exception as e:
        await interaction.followup.send(f"Error: {e}")

@client.tree.command(name="volume", description="Change the volume of the current song")
async def volume(interaction: discord.Interaction, volume: int):
    global current_volume
    if volume < 0 or volume > 100:
        await interaction.response.send_message("Volume must be between 0 and 100.")
        return
    current_volume = volume / 100
    vc = discord.utils.get(client.voice_clients, guild=interaction.guild)
    if vc and vc.is_playing() and isinstance(vc.source, discord.PCMVolumeTransformer):
        vc.source.volume = current_volume
        await interaction.response.send_message(f"Volume set to {volume}%.")
    else:
        await interaction.response.send_message("No song is currently playing, but the volume has been updated for the next playback.")

@client.tree.command(name="currentvolume", description="Show the current volume of the song")
async def currentvolume(interaction: discord.Interaction):
    current_volume_percentage = int(current_volume * 100)
    await interaction.response.send_message(f"Current volume is set to {current_volume_percentage}%.")

@client.tree.command(name="skip", description="Skip the current song or stop playback if the queue is empty.")
async def skip_command(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    vc = discord.utils.get(client.voice_clients, guild__id=guild_id)

    if not vc or not vc.is_playing():
        await interaction.response.send_message("Nothing is currently playing.", ephemeral=True)
        return

    vc.stop()
    await interaction.response.send_message("Skipped to the next song.")
    
    if guild_id in song_queue and song_queue[guild_id]:
        await play_next_song(guild_id)
    else:
        print(f"Queue is empty after skip in guild {guild_id}.")
        if not vc.is_playing():
            await vc.disconnect()



client.run("bottokenXD")
