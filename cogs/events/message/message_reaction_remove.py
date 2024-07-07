import interactions as ipy
from config import ROLE_IDS

# Event for when a reaction is removed from a message
class MessageReactionRemove(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
    # When accepting the rules
    @ipy.listen()
    async def rule_reaction_remove(self, event: ipy.events.MessageReactionRemove) -> None:
        # Check if correct message
        if event.message.id == 1259557055845503026:
            # Check if correct emoji then add Bürger role
            if event.emoji.name == '✅':
                await event.author.remove_role(ROLE_IDS['buerger'])