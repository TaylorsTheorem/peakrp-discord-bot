import interactions as ipy

# Simple implementation for a leave of absence command
class Loa(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
    @ipy.slash_command(
        name='abmelden',
        description='Melde dich hiermit für eine Zeit ab'
    )
    @ipy.slash_option(
        name='von',
        description='Datum ab dem du weg bist',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    @ipy.slash_option(
        name='bis',
        description='Datum zu dem du wieder da bist',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    @ipy.slash_option(
        name='grund',
        description='Grund für deine Abmeldung',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    async def loa(self, ctx: ipy.SlashContext, von: str, bis: str, grund: str) -> None:
        # Send a loa message with the information provided by the user
        await ctx.send(f'{ctx.user.mention}\n```Name: {ctx.member.nickname}\nVon: {von}\nBis: {bis}\nGrund: {grund}```')