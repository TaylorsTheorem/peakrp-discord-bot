import interactions as ipy
from datetime import datetime
from config import CHANNEL_IDS, LOGO_URL

# Sentinel extension for TypingStart event
# Part of the broadband Peak Sentinel logging system

class TypingStart(ipy.Extension):
    def __init__(self, bot):
        self.bot: ipy.Client = bot
    
    @ipy.listen()
    async def on_presence_update(self, event: ipy.events.TypingStart):
        
        # Create embed
        embed = ipy.Embed(
            title=f"Typing Start",
            author=ipy.EmbedAuthor("Peak Sentinel", icon_url=LOGO_URL),
            color=0x7edcf8,
            timestamp=datetime.now(),
            footer=ipy.EmbedFooter(str(event.author.id)),
            thumbnail=event.author.avatar_url,
            fields=[
                ipy.EmbedField("User", f"{event.author.mention}"),
                ipy.EmbedField("Channel", f"{event.channel.mention}"),
                ipy.EmbedField("Timestamp", f"{event.timestamp}"),
            ],
        )

        # Send embed to sentinel log channel
        channel = await self.bot.fetch_channel(CHANNEL_IDS['typing_start'])
        await channel.send(embed=embed)