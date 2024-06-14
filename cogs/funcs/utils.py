import interactions as ipy


# Utility functions for various tasks
class Utils:
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
    # Get the presence of a user from cache
    def get_presence(self, user: ipy.Member) -> dict:
        for entry in self.bot.guilds[0].presences:
            if entry['user']['id'] == str(user.id):
                return entry
        return None
    
    # Get the status (= online, dnd, idle, offline) of a user
    def get_status(self, user: ipy.Member) -> str:
        try: 
            status = self.get_presence(user=user).get('status')
        except:
            status = 'No status found'
        return status