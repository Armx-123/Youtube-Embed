import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
from urllib.parse import urlparse, urlunparse
import os

# Bot setup
TOKEN = os.environ['TOKEN']

intents = discord.Intents.default()
intents.message_content = True  # Ensures on_ready and message-based interactions work properly

bot = commands.Bot(command_prefix="/", intents=intents)

# Function to get public video URL
def get_public_video_url(youtube_url):
    ydl_opts = {
        'quiet': True,
        'format': '18/best',  # Prioritize itag=18 (MP4, 360p)
        'cookiefile': os.path.abspath('cookies.txt')
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)

        # Get the direct video URL
        for fmt in info.get('formats', []):
            if fmt.get('format_id') == '18':  # itag=18 (MP4, 360p)
                original_url = fmt.get('url')
                break
        else:
            original_url = info.get('url')  # Fallback to general URL

        # Replace the domain with redirector.googlevideo.com
        parsed_url = urlparse(original_url)
        new_url = urlunparse(parsed_url._replace(netloc='redirector.googlevideo.com'))

        return new_url

# Slash command to get video URL
@bot.tree.command(name="get_video", description="Get the public video URL from a YouTube link.")
@app_commands.describe(youtube_url="The YouTube video URL")
async def get_video(interaction: discord.Interaction, youtube_url: str):
    await interaction.response.defer()
    try:
        public_url = get_public_video_url(youtube_url)
        await interaction.followup.send(f"Here is the public video URL: [video]({public_url})")
    except Exception as e:
        await interaction.followup.send(f"Error: {e}")

# Sync commands and run bot
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("Bot is ready!")
        print(f"Logged in as {bot.user}")
        if os.path.isfile("cookies.txt"):
            print("cookies.txt found!")
            with open("cookies.txt", "r") as f:
                print("First few lines of cookies.txt:")
                for i in range(5):
                    print(f.readline().strip())
        else:
            print("cookies.txt not found.")
    except Exception as e:
        print(f"Error in on_ready: {e}")

bot.run(TOKEN)
