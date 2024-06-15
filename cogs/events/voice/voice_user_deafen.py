import interactions as ipy
from config import USER_IDS


# Extension for the voice user deafen event
class VoiceUserDeafen(ipy.Extension):
    def __init__(self, bot):
        self.bot: ipy.Client = bot
    

    # Event for when a user gets deafened
    @ipy.listen()
    async def voice_user_deafen(self, event: ipy.events.VoiceUserDeafen):
        # Check if the user is the Maestro, Deltixx or the bot
        if event.author.id in [USER_IDS['deltixx'], self.bot.owner.id, self.bot.user.id]:
            # Undeafen the user
            await event.state.member.edit(deaf=False)