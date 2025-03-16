import interactions as ipy
from config import INTENTS, BOT_STATUS, BOT_ACTIVITY
import cogs.funcs.db as db


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

# Load extensions
bot.load_extension('cogs.events.bot.ready')

bot.load_extension('cogs.events.message.message_reaction_add')
bot.load_extension('cogs.events.message.message_reaction_remove')

bot.load_extension('cogs.events.voice.voice_user_mute')
bot.load_extension('cogs.events.voice.voice_user_deafen')

bot.load_extension('cogs.funcs.cfx_api')
bot.load_extension('cogs.funcs.cheaterstats')
bot.load_extension('cogs.funcs.loa')
bot.load_extension('cogs.funcs.mod')
bot.load_extension('cogs.funcs.send')
bot.load_extension('cogs.funcs.support')
bot.load_extension('cogs.funcs.tickets')
bot.load_extension('cogs.funcs.user')
# bot.load_extension('cogs.funcs.help')

# bot.load_extension('cogs.sentinel.presence_update')
# bot.load_extension('cogs.sentinel.typing_start')

# Setup database if not exists and create database connection
db.setup_database()
db.create_connection()

# Start bot
bot.start()