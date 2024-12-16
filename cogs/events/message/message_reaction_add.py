import interactions as ipy
from config import ROLE_IDS

# Event for when a reaction is added to a message
class MessageReactionAdd(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
    # When accepting the rules
    @ipy.listen()
    async def rule_reaction_add(self, event: ipy.events.MessageReactionAdd) -> None:
        # Check if correct message
        if event.message.id == 1259573308676902975:
            # Check if correct emoji then add Bürger role
            if event.emoji.id == 1251982089621082193:
                await event.author.add_role(ROLE_IDS['citizen'])