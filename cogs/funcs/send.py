import interactions as ipy
from datetime import datetime

# Collection of commands for sending messages, embeds and direct messages
# TODO: Implement
class Send(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
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
            color=int(f'{color}', 16)
        )
        embed.set_footer(text=footer)
        embed.set_author(name=f'{ctx.member.user.username}',
                        icon_url=ctx.member.user.avatar_url)
        if thumbnail != None:
            embed.set_thumbnail(url=thumbnail)
        if image != None:
            embed.set_image(url=image)
        embed.timestamp = datetime.now()
        await channel.send(embeds=embed)
        await ctx.send(f'Folgendes wurde in {channel.mention} gesendet:\n\n>>> {embed}')
    
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
        if ctx.user.id == 120073956924456960:
            await user.send(message)
        else:
            await user.send(message + f'\n\n_Gruß {ctx.user.mention}_')
        await ctx.send(f'Folgendes wurde an {user.mention} **privat** gesendet:\n\n>>> {message}')

    @ipy.slash_command(
        name='staff_recruit',
        description='FINGER WEG! Das ist nur für die Staff-Rekrutierung!',
    )
    async def staff_recruit(self, ctx: ipy.SlashContext) -> None:
        channel = self.bot.get_channel(1196563739319730289)

        embed = ipy.Embed(
            title='Wir suchen Samurai (m/w/d)!',
            color=0x1f8b4c,
        )
        embed.set_image(url='https://cdn.discordapp.com/attachments/1181584302736158862/1196577724664397854/uncle-sam-we-want-you1-kopie_1.webp?ex=65b822d8&is=65a5add8&hm=2c40e8f610b103f306a067176292fe6751597f631aae95615d9fb558ecc9a12e&')
        embed.description = 'Tenno, wir suchen Samurai, also Staff-Mitglieder, die uns bei der Verwaltung des Servers helfen.'
        embed.add_field(name='Was wir erwarten:', value='- Aktivität\n- Teamfähigkeit und Eigeninitiative\n- Regelmäßig Recruiting-Nachricht in den Ingame Recruiting-Chat posten\n- Onboarding von neuen Mitgliedern\n- Unterstützung von Clanmitgliedern bei Fragen sowohl im Discord als auch Ingame\n- Mindestalter von 16 Jahren\n- Keine Vorstrafen')
        embed.add_field(name='Was wir bieten:', value='- Eine tolle Discord-Rolle\n- Ein tolles Team\n- Möglichkeiten eigene Ideen im Clan besser umzusetzen\n- Ausgiebigen Vergütungsplan')
        embed.add_field(name='Interesse geweckt?', value='Dann klicke, falls du es ernst meinst, auf den Button unten und es wird sich zeitnah jemand bei dir melden!\n\nWir freuen uns auf dich!')

        button = ipy.Button(
            style=ipy.ButtonStyle.PRIMARY,
            label='Ich will dabei sein!',
            emoji='👍',
            custom_id='staff_recruit_button'
        )

        await channel.send(embeds=embed, components=button)
    
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
        msg = await ctx.guild.get_channel(channel.id).fetch_message(message_id)
        await msg.reply(message)
        await ctx.send(f'Folgendes wurde in {channel.mention} gesendet:\n\n>>> {message}')