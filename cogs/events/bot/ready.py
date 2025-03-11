import interactions as ipy
from config import GUILD_ID


# Extension for the ready event
class Ready(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    

    # Event for when the bot is ready
    @ipy.listen()
    async def ready(self, event: ipy.events.Ready) -> None:
        # Fetch the guild and set the max presences to 10000
        guild = await self.bot.fetch_guild(GUILD_ID, force=True)
        await guild.gateway_chunk(wait=True, presences=True)

        print('Bot now launched! Ready for actions!')