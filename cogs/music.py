import discord
from discord.ext import commands
from discord import app_commands
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp as youtube_dl
import asyncio
from views.music_control import MusicControl
import json

#logging.basicConfig(level=logging.INFO) # uncomment for debugging
# fetches spotify playlists in batches of 5 at a time for smoother experiences (wait a lot less and can playback without delay)

"""
with open("configs/embeds.json", "r") as file:
    config = json.load(file)
    disconnect_footer = config["disconnect"]["footer"]
    error_color = (config["error"]["color"], 16)
     # not needed now, will be pushed next update
"""

# spotify API Setup
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

# playlist extraction
ytdl_playlist_options = {
    'format': 'bestaudio/best',
    'quiet': True,
    'extract_flat': True,
}
ytdl_playlist = youtube_dl.YoutubeDL(ytdl_playlist_options)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.music_control_view = None 
        self.now_playing_messages = {}  # update  
        # loop state tracking
        self.looped_songs = {}  # guild_id: song_info
        self.original_queues = {}  # guild_id: queue_copy
        self.current_song_info = {}  # guild_id: current_song_data

    @app_commands.command(name="play", description="Play a Spotify song/playlist or YouTube song/playlist in a voice channel.")
    async def play_command(self, interaction: discord.Interaction, url: str):
        if not interaction.user.voice:
            notinVC = discord.Embed(description=f"{interaction.user.mention}, you must be in a **voice channel** to use this command!", color=0xFF0000)
            notinVC.set_footer(text="https://divisionbot.space/")
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
            # check if it's a spotify URL - still here incase some people have spotify premium after the free tier abolishment 
            # to-do: add support for soundcloud, deezer, apple music, tidal, etc.
            if any(x in url.lower() for x in ["spotify.com", "open.spotify.com"]):
                queries = await self.get_spotify_track_url(url)
                if queries and len(queries) > 1:
                    first_query = queries.pop(0)
                    progress_message = discord.Embed(description=f"Adding **{len(queries)}** tracks to the queue...", color=0x32CD32)
                    progress_message.set_footer(text="https://divisionbot.space/")
                    msg = await interaction.followup.send(embed=progress_message)
                    asyncio.create_task(self.fetch_remaining_tracks(guild_id, queries, msg, len(queries)))
                    queries = [first_query]
            # check if it's a youtube playlist
            elif any(x in url.lower() for x in ["youtube.com/playlist", "youtu.be/"]) and "list=" in url.lower():
                first_track = await self.get_first_youtube_track(url)
                if first_track:
                    progress_message = discord.Embed(description="Extracting playlist and adding tracks to the queue...", color=0x32CD32)
                    progress_message.set_footer(text="https://divisionbot.space/")
                    msg = await interaction.followup.send(embed=progress_message)
                    asyncio.create_task(self.process_youtube_playlist_background(guild_id, url, msg))
                    queries = [first_track]
                else:
                    queries = []
            else:
                queries = [url]
                
            if not queries:
                errorEm = discord.Embed(title=":x: ERROR :x:", description="```Could not process your request. Please check the URL/search term and try again.```\n\nMessage **@exoticcitron** on discord to get this fixed...", color=0xFF0000)
                errorEm.set_footer(text="https://divisionbot.space/")
                await interaction.followup.send(embed=errorEm)
                return
                
            if not self.song_queue[guild_id] and not (vc and vc.is_playing()): 
                first_query = queries[0]
                yt_url, yt_title, yt_thumbnail, yt_duration = await self.search_youtube(first_query)
                if yt_url:
                    self.song_queue[guild_id].append({"url": yt_url, "title": yt_title, "thumbnail": yt_thumbnail, "duration": yt_duration})
                    await self.play_next_song(guild_id)
                    nowPlaying = discord.Embed(description=f"Now playing: **{yt_title}**", color=0x32CD32)
                    nowPlaying.set_footer(text="https://divisionbot.space/")
                    nowPlaying.set_thumbnail(url=yt_thumbnail or (interaction.guild.icon.url if interaction.guild.icon else None))
                    duration = yt_duration
                    progress_bar = f"[{'▬' * 20}] 0:00 / {duration // 60}:{duration % 60:02}"
                    nowPlaying.add_field(name="Duration", value=progress_bar)
                    nowPlaying.add_field(name="Links", value="[Discord](https://discord.gg/7kGnkGze2U)", inline=False)
                    if self.music_control_view is None or not self.bot.voice_clients:
                        self.music_control_view = MusicControl(interaction.user.id)
                    msg = await interaction.followup.send(embed=nowPlaying, view=self.music_control_view)
                    self.now_playing_messages[guild_id] = msg
                else:
                    print(f"Could not find YouTube URL for query: {first_query}")

            else: 
                for query in queries:
                    yt_url, yt_title, yt_thumbnail, yt_duration = await self.search_youtube(query)
                    if yt_url:
                        self.song_queue[guild_id].append({"url": yt_url, "title": yt_title, "thumbnail": yt_thumbnail, "duration": yt_duration})
                
                added_message = discord.Embed(description=f"Added **{len(queries)}** tracks to the queue!", color=0x32CD32)
                added_message.set_footer(text="https://divisionbot.space/")
                await interaction.followup.send(embed=added_message)

        except Exception as e:
            errorEm = discord.Embed(title=":x: ERROR :x:", description=f"```{e}```\n\nMessage **@exoticcitron** on discord to get this fixed...", color=0xFF0000)
            errorEm.set_footer(text="https://divisionbot.space/")
            await interaction.followup.send(embed=errorEm)

    @app_commands.command(name="skip", description="Skip the current song or stop playback if the queue is empty.")
    async def skip_command(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            notinVC = discord.Embed(description=f"{interaction.user.mention}, you must be in a **voice channel** to use this command!", color=0xFF0000)
            notinVC.set_footer(text="https://divisionbot.space/")
            await interaction.response.send_message(embed=notinVC)
            return

        guild_id = interaction.guild.id
        vc = discord.utils.get(self.bot.voice_clients, guild__id=guild_id)
        await interaction.response.defer()

        if vc and vc.is_playing():
            vc.stop()
            if guild_id in self.looped_songs:
                looped_song = self.looped_songs[guild_id]
                print(f"[DEBUG] Skip detected while looping: {looped_song['title']}")
                restart_embed = discord.Embed(
                    description=f"Restarting looped song: **{looped_song['title']}**",
                    color=0x32CD32
                )
                restart_embed.set_footer(text="https://divisionbot.space/")
                await interaction.followup.send(embed=restart_embed)
                return
            
            if self.song_queue[guild_id]:
                current_song = self.song_queue[guild_id][0]
                nowPlaying = discord.Embed(description=f"Now playing: **{current_song['title']}**", color=0x32CD32)
                nowPlaying.set_footer(text="https://divisionbot.space/")
                
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
                noSongIsPlaying.set_footer(text="https://divisionbot.space/")
                await interaction.followup.send(embed=noSongIsPlaying)
        else:
            noSongIsPlaying = discord.Embed(description="No song is currently playing", color=0xFF0000)
            noSongIsPlaying.set_footer(text="https://divisionbot.space/")
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

    @app_commands.command(name="loop", description="Loop a song from the queue or the currently playing song.")
    @app_commands.describe(song_number="The number of the song to loop (leave empty to loop current song)")
    async def loop_command(self, interaction: discord.Interaction, song_number: int = None):
        guild_id = interaction.guild.id
        vc = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        
        if not vc or not vc.is_connected():
            error_embed = discord.Embed(description="The bot is not connected to a voice channel.", color=0xFF0000)
            error_embed.set_footer(text="https://divisionbot.space/")
            await interaction.response.send_message(embed=error_embed)
            return

        if song_number is None:
            if not vc.is_playing():
                error_embed = discord.Embed(description="No song is currently playing.", color=0xFF0000)
                error_embed.set_footer(text="https://divisionbot.space/")
                await interaction.response.send_message(embed=error_embed)
                return
            
            if guild_id in self.current_song_info:
                song_info = self.current_song_info[guild_id]
                
                self.looped_songs[guild_id] = {
                    'title': song_info['title'],
                    'url': song_info['url'],
                    'thumbnail': song_info.get('thumbnail'),
                    'duration': song_info.get('duration'),
                    'is_current': True,  
                    'queue_position': None
                }
                
                self.original_queues[guild_id] = self.song_queue[guild_id].copy()
                
                print(f"[DEBUG] Started looping current song: {song_info['title']} in guild {guild_id}")
                
                success_embed = discord.Embed(
                    description=f"Now looping: **{song_info['title']}**",
                    color=0x32CD32
                )
                success_embed.set_footer(text="Use /unloop to stop looping | https://divisionbot.space/")
                await interaction.response.send_message(embed=success_embed)
                return
            
            error_embed = discord.Embed(description="Could not identify the currently playing song.", color=0xFF0000)
            error_embed.set_footer(text="https://divisionbot.space/")
            await interaction.response.send_message(embed=error_embed)
            return
        else:
            if guild_id not in self.song_queue or not self.song_queue[guild_id]:
                error_embed = discord.Embed(description="The queue is currently empty.", color=0xFF0000)
                error_embed.set_footer(text="https://divisionbot.space/")
                await interaction.response.send_message(embed=error_embed)
                return
            queue = self.song_queue[guild_id]
            if song_number < 1 or song_number > len(queue):
                error_embed = discord.Embed(
                    description=f"Please provide a valid song number between 1 and {len(queue)}.",
                    color=0xFF0000
                )
                error_embed.set_footer(text="https://divisionbot.space/")
                await interaction.response.send_message(embed=error_embed)
                return
            song = queue[song_number - 1]
            self.looped_songs[guild_id] = {
                'title': song['title'],
                'url': song['url'],
                'thumbnail': song.get('thumbnail'),
                'duration': song.get('duration'),
                'is_current': False,  
                'queue_position': song_number - 1  # 0-based index
            }
            
            self.original_queues[guild_id] = self.song_queue[guild_id].copy()
            
            print(f"[DEBUG] Started looping queue song at position {song_number}: {song['title']} in guild {guild_id}")
            
            success_embed = discord.Embed(
                description=f"Now looping: **{song['title']}**",
                color=0x32CD32
            )
            success_embed.set_footer(text="Use /unloop to stop looping | https://divisionbot.space/")
            await interaction.response.send_message(embed=success_embed)

    @app_commands.command(name="unloop", description="Stop looping the current song.")
    async def unloop_command(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id not in self.looped_songs:
            error_embed = discord.Embed(description="No song is currently being looped.", color=0xFF0000)
            error_embed.set_footer(text="https://divisionbot.space/")
            await interaction.response.send_message(embed=error_embed)
            return
        looped_song = self.looped_songs[guild_id]
        looped_title = looped_song['title']
        is_current = looped_song['is_current']
        del self.looped_songs[guild_id]
        vc = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        is_playing = vc and vc.is_playing()
        if guild_id in self.original_queues:
            if is_current and is_playing:
                self.song_queue[guild_id] = self.original_queues[guild_id].copy()
                print(f"[DEBUG] Restored original queue without current song for guild {guild_id}")
            else:
                self.song_queue[guild_id] = self.original_queues[guild_id].copy()
                print(f"[DEBUG] Restored original queue for guild {guild_id}")
                
            del self.original_queues[guild_id]
        
        print(f"[DEBUG] Stopped looping song: {looped_title} in guild {guild_id}")
        
        success_embed = discord.Embed(
            description=f"Stopped looping: **{looped_title}**",
            color=0x32CD32
        )
        success_embed.set_footer(text="https://divisionbot.space/")
        await interaction.response.send_message(embed=success_embed)

    async def play_next_song(self, guild_id):
        vc = discord.utils.get(self.bot.voice_clients, guild__id=guild_id)

        if not vc or not vc.is_connected():
            print(f"Bot is not connected to a voice channel in guild {guild_id}")
            self.music_control_view = None  
            return

        if guild_id in self.looped_songs:
            looped_song = self.looped_songs[guild_id]
            print(f"[DEBUG] Loop is active for guild {guild_id}, song: {looped_song['title']}")
            if looped_song['is_current']:
                song_url = looped_song['url']
                song_title = looped_song['title']
                song_thumbnail = looped_song.get('thumbnail')
                song_duration = looped_song.get('duration')
                
                try:
                    source = discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(song_url, **ffmpeg_options)
                    )
                    source.volume = self.bot.get_cog('Volume').current_volume

                    def after_playing(error):
                        if error:
                            print(f"Error occurred: {error}")
                        asyncio.run_coroutine_threadsafe(self.play_next_song(guild_id), self.bot.loop)

                    vc.play(source, after=after_playing)
                    print(f"[DEBUG] Replaying looped song: {song_title}")
                    
                    nowPlaying = discord.Embed(description=f"Now playing: **{song_title}** (Looped)", color=0x32CD32)
                    nowPlaying.set_footer(text="https://divisionbot.space/")
                    
                    if song_thumbnail:
                        nowPlaying.set_thumbnail(url=song_thumbnail)
                    else:
                        nowPlaying.set_thumbnail(url=vc.guild.icon.url if vc.guild.icon else None)
                    
                    if song_duration:
                        progress_bar = f"[{'▬' * 20}] 0:00 / {song_duration // 60}:{song_duration % 60:02}"
                        nowPlaying.add_field(name="Duration", value=progress_bar, inline=False)
                    
                    if guild_id in self.now_playing_messages:
                        try:
                            await self.now_playing_messages[guild_id].edit(embed=nowPlaying, view=self.music_control_view)
                        except:
                            msg = await vc.guild.text_channels[0].send(embed=nowPlaying, view=self.music_control_view)
                            self.now_playing_messages[guild_id] = msg
                    return
                except Exception as e:
                    print(f"[DEBUG] Error replaying looped song: {e}")
            else:
                queue_position = looped_song['queue_position']
                if queue_position < len(self.song_queue[guild_id]):
                    looped_queue_song = self.song_queue[guild_id][queue_position]
                    song_url = looped_queue_song["url"]
                    song_title = looped_queue_song["title"]
                    
                    try:
                        source = discord.PCMVolumeTransformer(
                            discord.FFmpegPCMAudio(song_url, **ffmpeg_options)
                        )
                        source.volume = self.bot.get_cog('Volume').current_volume

                        def after_playing(error):
                            if error:
                                print(f"Error occurred: {error}")
                            asyncio.run_coroutine_threadsafe(self.play_next_song(guild_id), self.bot.loop)

                        vc.play(source, after=after_playing)
                        print(f"[DEBUG] Replaying looped queue song: {song_title}")
                        
                        nowPlaying = discord.Embed(description=f"Now playing: **{song_title}** (Looped)", color=0x32CD32)
                        nowPlaying.set_footer(text="https://divisionbot.space/")
                        
                        if looped_queue_song.get('thumbnail'):
                            nowPlaying.set_thumbnail(url=looped_queue_song['thumbnail'])
                        else:
                            nowPlaying.set_thumbnail(url=vc.guild.icon.url if vc.guild.icon else None)
                        
                        duration = looped_queue_song['duration']
                        progress_bar = f"[{'▬' * 20}] 0:00 / {duration // 60}:{duration % 60:02}"
                        nowPlaying.add_field(name="Duration", value=progress_bar, inline=False)
                        
                        if guild_id in self.now_playing_messages:
                            try:
                                await self.now_playing_messages[guild_id].edit(embed=nowPlaying, view=self.music_control_view)
                            except:
                                msg = await vc.guild.text_channels[0].send(embed=nowPlaying, view=self.music_control_view)
                                self.now_playing_messages[guild_id] = msg
                        return
                    except Exception as e:
                        print(f"[DEBUG] Error replaying looped queue song: {e}")

        if guild_id in self.song_queue and self.song_queue[guild_id]:
            next_song = self.song_queue[guild_id].pop(0)
            song_url = next_song["url"]
            song_title = next_song["title"]
            
            self.current_song_info[guild_id] = {
                'title': song_title,
                'url': song_url,
                'thumbnail': next_song.get('thumbnail'),
                'duration': next_song.get('duration')
            }

            try:
                if not vc.is_playing():
                    source = discord.PCMVolumeTransformer(
                        discord.FFmpegPCMAudio(song_url, **ffmpeg_options)
                    )
                    source.volume = self.bot.get_cog('Volume').current_volume

                    def after_playing(error):
                        if error:
                            print(f"Error occurred: {error}")
                        asyncio.run_coroutine_threadsafe(self.play_next_song(guild_id), self.bot.loop)

                    vc.play(source, after=after_playing)
                    print(f"Now playing: {song_title}")

                    nowPlaying = discord.Embed(description=f"Now playing: **{song_title}**", color=0x32CD32)
                    nowPlaying.set_footer(text="https://divisionbot.space/")
                    
                    if next_song.get('thumbnail'):
                        nowPlaying.set_thumbnail(url=next_song['thumbnail'])
                    else:
                        nowPlaying.set_thumbnail(url=vc.guild.icon.url if vc.guild.icon else None)
                    
                    duration = next_song['duration']
                    progress_bar = f"[{'▬' * 20}] 0:00 / {duration // 60}:{duration % 60:02}"
                    nowPlaying.add_field(name="Duration", value=progress_bar, inline=False)
                    
                    nowPlaying.add_field(name="Links", value="[Discord](https://discord.gg/7kGnkGze2U)", inline=False)
                    if guild_id in self.now_playing_messages:
                        try:
                            await self.now_playing_messages[guild_id].edit(embed=nowPlaying, view=self.music_control_view)
                        except:
                            msg = await vc.guild.text_channels[0].send(embed=nowPlaying, view=self.music_control_view)
                            self.now_playing_messages[guild_id] = msg
                else:
                    print(f"Already playing audio in guild {guild_id}.")
            except Exception as e:
                print(f"Failed to play song '{song_title}': {e}")
                await self.play_next_song(guild_id)
        else:
            print(f"Queue is empty in guild {guild_id}.")
            self.song_queue[guild_id] = []
            if not vc.is_playing():
                await vc.disconnect()
                self.song_queue[guild_id] = []

    async def search_youtube(self, query):
        loop = asyncio.get_event_loop()
        try:
            print(f"Searching YouTube for: {query}")
            info = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
            if info and 'entries' in info:
                entry = info['entries'][0]
                print(f"Found YouTube video: {entry['title']}")
                return entry['url'], entry['title'], entry['thumbnail'], entry['duration']
            elif 'url' in info:
                print(f"Found YouTube video: {info['title']}")
                return info['url'], info['title'], info.get('thumbnail'), info.get('duration')
            return None, None, None, None
        except Exception as e:
            print(f"Error searching YouTube: {e}")
            return None, None, None, None

    async def get_first_youtube_track(self, playlist_url):
        """Get just the first track from a YouTube playlist for immediate playback"""
        loop = asyncio.get_event_loop()
        try:
            print(f"Getting first track from YouTube playlist: {playlist_url}")
            playlist_info = await loop.run_in_executor(
                None, 
                lambda: ytdl_playlist.extract_info(playlist_url, download=False)
            )
            
            if not playlist_info or 'entries' not in playlist_info or not playlist_info['entries']:
                print("Could not extract playlist information or playlist is empty")
                return None
                
            first_entry = playlist_info['entries'][0]
            if first_entry:
                first_video_url = f"https://www.youtube.com/watch?v={first_entry['id']}"
                print(f"Found first video: {first_video_url}")
                return first_video_url
            
            return None
        except Exception as e:
            print(f"Error extracting first YouTube track: {e}")
            return None

    async def process_youtube_playlist_background(self, guild_id, playlist_url, message):
        """Process the rest of the YouTube playlist in the background"""
        try:
            video_urls = await self.get_youtube_playlist_urls(playlist_url)
            
            if not video_urls:
                error_message = discord.Embed(description="❌ Could not extract any tracks from the playlist.", color=0xFF0000)
                error_message.set_footer(text="https://divisionbot.space/")
                await message.edit(embed=error_message)
                return
            
            progress_message = discord.Embed(description=f"Adding **{len(video_urls)}** tracks to the queue...", color=0x32CD32)
            progress_message.set_footer(text="https://divisionbot.space/")
            await message.edit(embed=progress_message)
            await self.fetch_remaining_tracks(guild_id, video_urls, message, len(video_urls))
            
        except Exception as e:
            print(f"Error in background playlist processing: {e}")
            error_message = discord.Embed(description=f"❌ Error processing playlist: {str(e)}", color=0xFF0000)
            error_message.set_footer(text="https://divisionbot.space/")
            await message.edit(embed=error_message)

    async def get_youtube_playlist_urls(self, playlist_url):
        """Extract all video URLs from a YouTube playlist"""
        loop = asyncio.get_event_loop()
        try:
            print(f"Extracting YouTube playlist: {playlist_url}")
            playlist_info = await loop.run_in_executor(
                None, 
                lambda: ytdl_playlist.extract_info(playlist_url, download=False)
            )
            
            if not playlist_info or 'entries' not in playlist_info:
                print("Could not extract playlist information")
                return []
                
            video_urls = []
            for i, entry in enumerate(playlist_info['entries']):
                if entry and i > 0:  
                    video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
            
            # limits to 49 more songs (50 total including the first one) - change if wanted
            if len(video_urls) > 49:
                video_urls = video_urls[:49]
                print(f"Limiting playlist to 49 more songs (50 total) out of {len(playlist_info['entries'])}")
            
            print(f"Found {len(video_urls)} additional videos in YouTube playlist")
            return video_urls
        except Exception as e:
            print(f"Error extracting YouTube playlist: {e}")
            return []

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

    async def fetch_remaining_tracks(self, guild_id, queries, message, total_tracks):
        batch_size = 5
        added_count = 0
        skipped_count = 0
        
        print(f"Starting to process {len(queries)} tracks in batches of {batch_size}")
        
        for i in range(0, len(queries), batch_size):
            batch = queries[i:i + batch_size]
            batch_added = 0
            
            print(f"Processing batch {i//batch_size + 1} with {len(batch)} tracks")
            
            for query in batch:
                yt_url, yt_title, yt_thumbnail, yt_duration = await self.search_youtube(query)
                if yt_url:
                    self.song_queue[guild_id].append({"url": yt_url, "title": yt_title, "thumbnail": yt_thumbnail, "duration": yt_duration})
                    added_count += 1
                    batch_added += 1
                    print(f"Added to queue: {yt_title}")
                else:
                    skipped_count += 1
                    print(f"Could not find YouTube URL for query: {query}")            
            if added_count > 0 or skipped_count > 0:
                if added_count < total_tracks or i + batch_size < len(queries):
                    progress_desc = f"Added **{added_count}** tracks to the queue..."
                    if skipped_count > 0:
                        progress_desc += f"\n⚠️ **{skipped_count}** tracks couldn't be found"
                    progress_message = discord.Embed(description=progress_desc, color=0x32CD32)
                    progress_message.set_footer(text="https://divisionbot.space/")
                    await message.edit(embed=progress_message)
            await asyncio.sleep(1)
        if added_count > 0:
            finished_desc = f"✅ Finished adding **{added_count}** songs from playlist!"
            if skipped_count > 0:
                finished_desc += f"\n⚠️ **{skipped_count}** tracks couldn't be found on YouTube"
            finished_message = discord.Embed(description=finished_desc, color=0x32CD32)
            finished_message.set_footer(text="https://divisionbot.space/")
            await message.edit(embed=finished_message)
        else:
            error_message = discord.Embed(description="❌ Could not find any valid tracks from the playlist.", color=0xFF0000)
            error_message.set_footer(text="https://divisionbot.space/")
            await message.edit(embed=error_message)

    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user and before.channel is not None and after.channel is None:
            print("Bot has left the voice channel.")
            self.music_control_view = None  

async def setup(bot):
    await bot.add_cog(Music(bot))