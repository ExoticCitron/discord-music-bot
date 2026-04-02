import discord
from discord.ext import commands
from discord import app_commands

class Loop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.looped_songs = {}  # guild_id: song_info
        self.original_queues = {}  # guild_id: queue_copy

    @app_commands.command(name="loop", description="Loop a song from the queue or the currently playing song.")
    @app_commands.describe(song_number="The number of the song to loop (leave empty to loop current song)")
    async def loop_command(self, interaction: discord.Interaction, song_number: int = None):
        guild_id = interaction.guild.id
        music_cog = self.bot.get_cog('Music')
        
        if not music_cog:
            error_embed = discord.Embed(title=":x: ERROR :x:", description="Music cog not found.", color=0xFF0000)
            error_embed.set_footer(text="https://divisionbot.space/")
            await interaction.response.send_message(embed=error_embed)
            return

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
            
            if guild_id in music_cog.now_playing_messages:
                try:
                    msg = music_cog.now_playing_messages[guild_id]
                    embed = msg.embeds[0] if msg.embeds else None
                    
                    if embed and embed.description:
                        title = embed.description.split("**")[1] if "**" in embed.description else "Unknown"
                        
                        self.looped_songs[guild_id] = {
                            'title': title,
                            'is_current': True,  # flag to indicate this is the current playing song
                            'queue_position': None
                        }
                        
                        self.original_queues[guild_id] = music_cog.song_queue[guild_id].copy()
                        
                        print(f"[DEBUG] Started looping current song: {title} in guild {guild_id}")
                        
                        success_embed = discord.Embed(
                            description=f"Now looping: **{title}**",
                            color=0x32CD32
                        )
                        success_embed.set_footer(text="Use /unloop to stop looping | https://divisionbot.space/")
                        await interaction.response.send_message(embed=success_embed)
                        return
                except Exception as e:
                    print(f"[DEBUG] Error getting now playing message: {e}")
            
            error_embed = discord.Embed(description="Could not identify the currently playing song.", color=0xFF0000)
            error_embed.set_footer(text="https://divisionbot.space/")
            await interaction.response.send_message(embed=error_embed)
            return
        
        else:
            if guild_id not in music_cog.song_queue or not music_cog.song_queue[guild_id]:
                error_embed = discord.Embed(description="The queue is currently empty.", color=0xFF0000)
                error_embed.set_footer(text="https://divisionbot.space/")
                await interaction.response.send_message(embed=error_embed)
                return
            
            queue = music_cog.song_queue[guild_id]
            
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
                'is_current': False,  # this is a song from the queue
                'queue_position': song_number - 1  # 0-based index
            }
            
            self.original_queues[guild_id] = music_cog.song_queue[guild_id].copy()
            
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
        
        looped_title = self.looped_songs[guild_id]['title']
        
        del self.looped_songs[guild_id]
        
        if guild_id in self.original_queues:
            music_cog = self.bot.get_cog('Music')
            if music_cog:
                music_cog.song_queue[guild_id] = self.original_queues[guild_id].copy()
            del self.original_queues[guild_id]
        
        print(f"[DEBUG] Stopped looping song: {looped_title} in guild {guild_id}")
        
        success_embed = discord.Embed(
            description=f"Stopped looping: **{looped_title}**",
            color=0x32CD32
        )
        success_embed.set_footer(text="https://divisionbot.space/")
        await interaction.response.send_message(embed=success_embed)

    def is_looping(self, guild_id):
        """Check if a song is being looped in the specified guild"""
        return guild_id in self.looped_songs
    
    def get_looped_song(self, guild_id):
        """Get the looped song info for the specified guild"""
        return self.looped_songs.get(guild_id, None)

async def setup(bot):
    await bot.add_cog(Loop(bot))