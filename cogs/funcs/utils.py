import interactions as ipy
import re

# Utility functions for various tasks
# Get the presence of a user from cache
def get_presence(bot: ipy.Client, user: ipy.Member) -> dict:
    for entry in bot.guilds[0].presences:
        if entry['user']['id'] == str(user.id):
            return entry
    return None

# Get the status (= online, dnd, idle, offline) of a user
def get_status(bot: ipy.Client, user: ipy.Member) -> str:
    try: 
        status = get_presence(bot=bot, user=user).get('status')
    except:
        status = 'No status found'
    return status

# Get integer from string between | and |
def extract_middle_integer(string):
    match = re.search(r'\| (\d+) \|', string)
    if match:
        return int(match.group(1))
    else:
        return None
    
# Get integer from string after last |
def extract_last_integer(string):
    match = re.search(r'\d+$', string)
    if match:
        return int(match.group())
    else:
        return None

# Get first string from string split by |
def extract_first_string(string):
    return string.split(' | ')[0].strip()