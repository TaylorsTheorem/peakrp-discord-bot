import interactions as ipy
from datetime import datetime


# Collection of commands for sending messages, embeds and direct messages
class Send(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
    
    # Command for sending a message to a specified channel
    @ipy.slash_command(
        name='send_message',
        description='Sende eine normale Nachricht in einen Channel',
    )
    @ipy.slash_option(
        name='channel',
        description='In welchen Channel soll die Nachricht gesendet werden?',
        opt_type=ipy.OptionType.CHANNEL,
        required=True,
    )
    @ipy.slash_option(
        name='message',
        description='Was soll in der Nachricht stehen?',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    async def send_message(self, ctx: ipy.SlashContext, channel: ipy.BaseChannel, message: str) -> None:
        await channel.send(message)
        await ctx.send(f'Folgendes wurde in {channel.mention} gesendet:\n\n>>> {message}')


    # Command for sending an embed message to a specified channel
    @ipy.slash_command(
        name='send_embed',
        description='Sende eine Embed Nachricht in einen Channel',
    )
    @ipy.slash_option(
        name='channel',
        description='In welchen Channel soll die Nachricht gesendet werden?',
        opt_type=ipy.OptionType.CHANNEL,
        required=True
    )
    @ipy.slash_option(
        name='title',
        description='Was soll als Titel stehen?',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    @ipy.slash_option(
        name='description',
        description='Was soll als Beschreibung stehen?',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    @ipy.slash_option(
        name='color',
        description='Welche Farbe soll die Embed Nachricht haben?',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    @ipy.slash_option(
        name='footer',
        description='Was soll als Footer stehen?',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    @ipy.slash_option(
        name='thumbnail',
        description='Welches Bild soll als Thumbnail verwendet werden?',
        opt_type=ipy.OptionType.STRING,
        required=False
    )
    @ipy.slash_option(
        name='image',
        description='Welches Bild soll als Bild verwendet werden?',
        opt_type=ipy.OptionType.STRING,
        required=False
    )
    async def send_embed(self,
                        ctx: ipy.SlashContext,
                        channel: ipy.BaseChannel,
                        title: str,
                        description: str,
                        color: str,
                        footer: str,
                        thumbnail: str = None,
                        image: str = None
                        ) -> None:
        embed = ipy.Embed(
            title=title,
            description=description,
            color=int(f'{color}', 16),
            footer=ipy.EmbedFooter(text=footer),
            author=ipy.EmbedAuthor(name=f'{ctx.member.user.username}', icon_url=ctx.member.user.avatar_url),
            timestamp=datetime.now()
        )

        # Add optional thumbnail and image, if provided
        if thumbnail != None:
            embed.set_thumbnail(url=thumbnail)
        if image != None:
            embed.set_image(url=image)

        # Send the embed message
        await channel.send(embeds=embed)
        await ctx.send(f'Folgendes wurde in {channel.mention} gesendet:\n\n>>> {embed}')    # Log
    

    # Command for sending a direct message to a user
    @ipy.slash_command(
        name='send_dm',
        description='Sende eine Privat-Nachricht an einen User',
    )
    @ipy.slash_option(
        name='user',
        description='An welchen User soll die Nachricht gesendet werden?',
        opt_type=ipy.OptionType.USER,
        required=True
    )
    @ipy.slash_option(
        name='message',
        description='Was soll in der Nachricht stehen?',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    async def send_dm(self, ctx: ipy.SlashContext, user: ipy.User, message: str) -> None:
        if ctx.user.id == self.bot.owner.id:   # If the user is the bot owner, don't add the log message
            await user.send(message)
        else:
            await user.send(message + f'\n\n_Gruß {ctx.user.mention}_')
        await ctx.send(f'Folgendes wurde an {user.mention} **privat** gesendet:\n\n>>> {message}')  # Log

    
    # Command for replying to a message
    @ipy.slash_command(
        name='reply',
        description='Antworte auf eine Nachricht',
    )
    @ipy.slash_option(
        name='message_id',
        description='Auf welche Nachricht soll geantwortet werden?',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    @ipy.slash_option(
        name='channel',
        description='In welchen Channel soll die Nachricht gesendet werden?',
        opt_type=ipy.OptionType.CHANNEL,
        required=True
    )
    @ipy.slash_option(
        name='message',
        description='Was soll in der Nachricht stehen?',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    async def reply(self, ctx: ipy.SlashContext, message_id: str, channel: ipy.BaseChannel, message: str) -> None:

        # Fetch the message and reply to it
        msg = await ctx.guild.get_channel(channel.id).fetch_message(message_id)
        await msg.reply(message)
        await ctx.send(f'Folgendes wurde in {channel.mention} gesendet:\n\n>>> {message}')  # Log