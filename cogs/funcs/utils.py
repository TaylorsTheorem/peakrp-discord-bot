import interactions as ipy


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