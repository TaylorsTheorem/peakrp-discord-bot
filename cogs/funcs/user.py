import interactions as ipy
from datetime import datetime
from config import LOGO_URL, ROLE_IDS
from cogs.funcs.utils import get_status
import cogs.funcs.db as db


# Collection of commands for user related tasks
class User(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
    # Base command for user related tasks
    @ipy.slash_command(
        name='user',
        description='Sämtliche Infos über einen User'
    )
    async def user_base(self, ctx: ipy.SlashContext):
        pass

    # Subcommand for general user information
    # Parameters:
    #   user (ipy.Member) - The user for which the information is requested
    @user_base.subcommand(
        sub_cmd_name='info',
        sub_cmd_description='Allgemeine Infos über einen User'
    )
    @ipy.slash_option(
        name='user',
        description='Von welchem User willst du Infos?',
        opt_type=ipy.OptionType.USER,
        required=True
    )
    async def user_info(self, ctx: ipy.SlashContext, user: ipy.Member) -> None:

        # Get user status, if not in cache (= changed presence since starting bot), try to find in gateway cache / fetch from API
        if isinstance(user.status, ipy.Missing):
            user_status = get_status(self.bot, user)
        else:
            # Result is a string like 'Status.ONLINE', so remove 'Status.' and make it lowercase
            user_status = str(user.status)[7:].lower()

        # Create and send embed with user information
        embed = ipy.Embed(
            title='User-Info | Allgemein',
            author=ipy.EmbedAuthor(name=f'{user.username} | {user.display_name}', icon_url=LOGO_URL),
            thumbnail=user.avatar_url,
            footer=ipy.EmbedFooter(f'Discord ID: {user.id}'),
            timestamp=datetime.now(),
            color=0x00ffff,
            fields=[
                ipy.EmbedField(name='DC Status', value=user_status, inline=True),
                ipy.EmbedField(name='Ist IC', value='???', inline=True),
                ipy.EmbedField(name='Hat Whitelist', value=str(user.has_role(ROLE_IDS['wl'])), inline=True),
                ipy.EmbedField(name='IC ID', value='187', inline=True),
                ipy.EmbedField(name='Ingame Money', value='1.000.000€', inline=True),
                ipy.EmbedField(name='Support-Fälle', value=str(db.get_user_cases_count(user.id)), inline=True),
                ipy.EmbedField(name='Discord ID', value=str(user.id), inline=True),
                ipy.EmbedField(name='Steam ID', value='5d50090f17876084', inline=True),
                ipy.EmbedField(name='License Key', value='5d50090f17876084', inline=True),
                ipy.EmbedField(name='XBOX ID', value='5d50090f17876084', inline=True),
                ipy.EmbedField(name='Hardware ID', value='5d50090f17876084', inline=True),
            ]
        )
        await ctx.send(embed=embed)