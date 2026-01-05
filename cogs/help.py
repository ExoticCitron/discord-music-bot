import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View

class HelpSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="🎵 Music Commands",
                description="Play, skip, queue commands",
                emoji="🎵"
            ),
            discord.SelectOption(
                label="🔊 Volume Commands", 
                description="Volume control commands",
                emoji="🔊"
            ),
            discord.SelectOption(
                label="ℹ️ Bot Info",
                description="Bot information and support",
                emoji="ℹ️"
            )
        ]
        super().__init__(
            placeholder="Choose a category...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="help_select"
        )

class HelpView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HelpSelect())

    async def callback(self, interaction: discord.Interaction):
        selected = self.children[0].values[0]
        
        if selected == "🎵 Music Commands":
            embed = discord.Embed(
                title="🎵 Music Commands",
                description="All music-related commands for the bot:",
                color=0x32CD32
            )
            embed.add_field(
                name="/play <song/url>",
                value="Play a song or add to queue. **Supports:**\n"
                      "• Plain text (e.g., 'never gonna give you up')\n"
                      "• Spotify track URLs\n"
                      "• Spotify playlist URLs (Public)\n"
                      "• Spotify album URLs (Public)\n"
                      "• YouTube URLs",
                inline=False
            )
            embed.add_field(
                name="/skip",
                value="Skip the current song and play the next one in queue",
                inline=False
            )
            embed.add_field(
                name="/skipto <number>",
                value="Skip to a specific song in the queue by its number",
                inline=False
            )
            embed.add_field(
                name="/queue",
                value="Display the current music queue with all songs",
                inline=False
            )
            
        elif selected == "🔊 Volume Commands":
            embed = discord.Embed(
                title="🔊 Volume Commands",
                description="Volume control commands:",
                color=0x32CD32
            )
            embed.add_field(
                name="/volume <0-100>",
                value="Set the bot volume (0-100%)",
                inline=False
            )
            
        else:  # Bot Info
            embed = discord.Embed(
                title="ℹ️ Bot Information",
                description="Division Interactive - Discord Music Bot",
                color=0x32CD32
            )
            embed.add_field(
                name="About",
                value="A powerful Discord music bot developed by Division Interactive that supports multiple platforms and provides seamless music playback.",
                inline=False
            )
            embed.add_field(
                name="Support",
                value="Need help? Message **@exoticcitron** on Discord\n"
                      "Visit: https://divisionbot.space/",
                inline=False
            )
            embed.add_field(
                name="Features",
                value="• Spotify & YouTube support\n"
                      "• Playlist processing\n"
                      "• Real-time queue updates\n"
                      "• Progress tracking\n"
                      "• Auto-playback",
                inline=False
            )
        
        embed.set_footer(text="https://divisionbot.space/")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/8423569505349468160/866815624923578368/music_note.png")
        
        await interaction.response.edit_message(embed=embed, view=self)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Display help menu with command categories.")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 Division Interactive Music Bot Help",
            description="Select a category below to see available commands:",
            color=0x32CD32
        )
        embed.add_field(
            name="Quick Start",
            value="• `/play 'song name'` - Search YouTube\n"
                  "• `/play 'spotify url'` - Play Spotify content\n"
                  "• `/queue` - View current queue\n"
                  "• `/skip` - Skip current song",
            inline=False
        )
        embed.set_footer(text="https://divisionbot.space/")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/8423569505349468160/866815624923578368/music_note.png")
        
        view = HelpView()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))
