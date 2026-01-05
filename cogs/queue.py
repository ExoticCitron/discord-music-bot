import discord
from discord.ext import commands
from discord import app_commands

class Queue(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="queue", description="Display the current music queue.")
    async def queue_command(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        music_cog = self.bot.get_cog('Music')
        
        if not music_cog:
            error_embed = discord.Embed(title=":x: ERROR :x:", description="Music cog not found.", color=0xFF0000)
            error_embed.set_footer(text="https://divisionbot.space/")
            await interaction.response.send_message(embed=error_embed)
            return

        if guild_id not in music_cog.song_queue or not music_cog.song_queue[guild_id]:
            empty_embed = discord.Embed(description="The queue is currently empty.", color=0xFF0000)
            empty_embed.set_footer(text="https://divisionbot.space/")
            await interaction.response.send_message(embed=empty_embed)
            return

        queue_list = music_cog.song_queue[guild_id]
        queue_text = ""
        
        for i, song in enumerate(queue_list, 1):
            # Format duration
            duration = song.get('duration', 0)
            if duration:
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            queue_text += f"**{i}.** {song['title']} - `{duration_str}`\n"
            
            # Limit to 20 songs to avoid embed size issues
            if i >= 20:
                remaining = len(queue_list) - 20
                queue_text += f"\n... and {remaining} more songs"
                break

        queue_embed = discord.Embed(
            title="🎵 Music Queue",
            description=queue_text,
            color=0x32CD32
        )
        queue_embed.set_footer(text=f"Total songs: {len(queue_list)} | https://divisionbot.space/")
        
        await interaction.response.send_message(embed=queue_embed)

async def setup(bot):
    await bot.add_cog(Queue(bot))
