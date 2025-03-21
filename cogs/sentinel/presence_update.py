import interactions as ipy
from datetime import datetime
from config import CHANNEL_IDS, LOGO_URL
import cogs.funcs.tracked_users as tracked_users

# Sentinel extension for PresenceUpdate event
# Part of the broadband Peak Sentinel logging system

class PresenceUpdate(ipy.Extension):
    def __init__(self, bot):
        self.bot: ipy.Client = bot
    
    @ipy.listen()
    async def on_presence_update(self, event: ipy.events.PresenceUpdate):

        if not tracked_users.is_tracked(event.user.id):
            return

        # Extract image urls from users activities if activity is present
        large_images = [activity.assets.large_image for activity in event.activities if activity.assets and activity.assets.large_image]
        image_urls = []
        # Extract image urls from discords external links
        for image_url in large_images if large_images else []:
            if image_url.startswith("mp:external/"):
                extracted_url = image_url.replace('mp:external/', 'https://media.discordapp.net/external/')
                image_urls.append(extracted_url)
        
        # Define colors for user status
        user_status_colors = {
            "online": 0x43B581,
            "offline": 0x7c7c7c,
            "idle": 0xFAA61A,
            "dnd": 0x982929,
        }

        # Create embed
        embed = ipy.Embed(
            title=f"Presence Update",
            author=ipy.EmbedAuthor("Peak Sentinel", icon_url=LOGO_URL),
            color=user_status_colors[event.status],
            timestamp=datetime.now(),
            footer=ipy.EmbedFooter(str(event.user.id)),
            thumbnail=event.user.avatar_url,
            fields=[
                ipy.EmbedField("User Status", f"{event.user.mention} is now {event.status}"),
                # Create embed fields for each key value pair in the client status dictionary (all currently logged in devices)
                ipy.EmbedField("Current devices", "\n".join([f"{key}: {value}" for key, value in event.client_status.items()])),
                # Create embed fields for each activity in the users activity list
                ipy.EmbedField("Activities", "\n".join([f"- {activity.name} ({activity.state}) {activity.details} {activity.created_at} {activity.timestamps}" for activity in event.activities]))
            ],
        )

        # Add images to embed
        if image_urls:
            embed.set_images(*image_urls)

        # Send embed to sentinel log channel
        channel = await self.bot.fetch_channel(CHANNEL_IDS['presence_update'])
        await channel.send(embed=embed)