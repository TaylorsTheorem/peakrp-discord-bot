import interactions as ipy
from datetime import datetime, timedelta

# Collection of commands for discord moderation purposes
class Mod(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    

    # Command for timing out a user
    # Parameters:
    #   user (ipy.Member) - User to be timed out
    #   time (int) - Time in minutes for the timeout
    #   reason (str) - Reason for the timeout
    @ipy.slash_command(
        name='timeout',
        description='Timeoute hiermit einen User'
    )
    @ipy.slash_option(
        name='user',
        description='Welcher User soll getimeouted werden?',
        opt_type=ipy.OptionType.USER,
        required=True
    )
    @ipy.slash_option(
        name='time',
        description='Wie lange soll der user getimeouted werden?',
        opt_type=ipy.OptionType.INTEGER,
        required=True,
        choices=[
            ipy.SlashCommandChoice(name='5 Minuten', value=5),
            ipy.SlashCommandChoice(name='30 Minuten', value=30),
            ipy.SlashCommandChoice(name='2 Stunden', value=120),
            ipy.SlashCommandChoice(name='24 Stunden', value=1440)
        ]
    )
    @ipy.slash_option(
        name='reason',
        description='Warum soll der User getimeouted werden?',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    async def timeout(self, ctx: ipy.SlashContext, user: ipy.Member, time: int, reason: str) -> None:
        await user.timeout(communication_disabled_until=datetime.now()+timedelta(minutes=time), reason=reason)
        await user.send(f'# Timeout\nDu wurdest für **{time}** Minuten vom Peak Roleplay Discord getimeouted.\nDer Grund des Timeouts ist:```{reason}```')
        await ctx.send(f'User: {user.mention} wurde für **{time}** Minuten von {ctx.user.mention} getimeouted.\nGrund: {reason}')