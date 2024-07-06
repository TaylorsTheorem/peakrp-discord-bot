import interactions as ipy
from config import INTENTS, BOT_STATUS, BOT_ACTIVITY
import cogs.funcs.db as db
import subprocess, signal, sys, time


# Get bot token from environment
import os
BOT_TOKEN = os.getenv('PEAK_BOT_TOKEN')

# Create bot instance
bot = ipy.Client(
    token=BOT_TOKEN,
    intents=INTENTS,
    status=BOT_STATUS,
    activity=BOT_ACTIVITY,
    disable_dm_commands=True,   # Disable commands in DMs
    fetch_members=True  # Fetch all members on startup
)

# Start Lavalink server
# command = ['java', '-jar', 'cogs/lavalink/Lavalink.jar', '--spring.config.location=file:cogs/lavalink/application.yml']
command = ['java', '-jar', 'Lavalink.jar']
lavalink_process = subprocess.Popen(command, cwd='cogs/lavalink')

# Wait for Lavalink server to start
time.sleep(5)

# Stop Lavalink server
def stop_lavalink(signum, frame):
    global lavalink_process
    if lavalink_process:
        lavalink_process.terminate()
        lavalink_process.wait()
    sys.exit(0)

# Stop Lavalink server when bot is stopped
signal.signal(signal.SIGINT, stop_lavalink)

# Load extensions
bot.load_extension('cogs.events.bot.ready')

bot.load_extension('cogs.events.voice.voice_user_mute')
bot.load_extension('cogs.events.voice.voice_user_deafen')

# bot.load_extension('cogs.funcs.cfx_api')
bot.load_extension('cogs.funcs.loa')
bot.load_extension('cogs.funcs.mod')
bot.load_extension('cogs.funcs.send')
bot.load_extension('cogs.funcs.support')
bot.load_extension('cogs.funcs.tickets')
bot.load_extension('cogs.funcs.user')

bot.load_extension('cogs.music.music')

# Setup database if not exists and create database connection
db.setup_database()
db.create_connection()

# Start bot
bot.start()