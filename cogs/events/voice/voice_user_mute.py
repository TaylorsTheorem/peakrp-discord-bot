import interactions as ipy
from config import USER_IDS


# Extension for the voice user mute event
class VoiceUserMute(ipy.Extension):
    def __init__(self, bot):
        self.bot: ipy.Client = bot
    

    # Event for when a user gets muted
    @ipy.listen()
    async def voice_user_mute(self, event: ipy.events.VoiceUserMute):
        # Check if the user is the Maestro, Deltixx or the bot
        if event.author.id in [USER_IDS['deltixx'], self.bot.owner.id, self.bot.user.id]:
            # Unmute the user
            await event.state.member.edit(mute=False)