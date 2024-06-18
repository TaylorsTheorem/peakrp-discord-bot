import interactions as ipy
from interactions.ext.paginators import Paginator
from config import CHANNEL_IDS, LOGO_URL
from datetime import datetime
import cogs.funcs.db as db


# Collection of commands for support related tasks
class Support(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot


    # Base command for support related tasks
    @ipy.slash_command(
        name='support',
        description='Befehle für sämtliche Support-Angelegenheiten'
    )
    async def support_base(self, ctx: ipy.SlashContext) -> None:
        pass
    
    # Subcommand for moving the user with the longest waiting time to the user's voice channel
    @support_base.subcommand(
        sub_cmd_name='move',
        sub_cmd_description='Move den am längsten wartenden User'
    )
    async def support_move(self, ctx: ipy.SlashContext) -> None:
        # Check if user is in a voice channel
        if not ctx.member.voice:
            await ctx.send('Du bist in keinem Voice-Channel.\nKann niemanden zu dir moven!', delete_after=15, ephemeral=True)
            return
        # Check if user is in the support waiting channel
        support_waiting_channel = await self.bot.fetch_channel(CHANNEL_IDS['support_waiting'])
        support_queue = support_waiting_channel.voice_members

        if not support_queue:
            await ctx.send('Es wartet niemand im Support.', delete_after=15, ephemeral=True)
            return
        
        # Move user with longest waiting time to user's voice channel
        await support_queue[0].move(ctx.member.voice.channel.id)
        await ctx.send(f'{support_queue[0].mention} wurde in {ctx.member.voice.channel.mention} gemoved.')

    # Subcommand for logging a support case
    # Parameters: 
    #   ic_ooc (str) - If case is for an In Character or Out Of Character topic
    #   user (ipy.Member) - The user for which the support case is logged
    @support_base.subcommand(
        sub_cmd_name='log',
        sub_cmd_description='Logge einen Supportfall'
    )
    @ipy.slash_option(
        name='ic_ooc',
        description='War das ein IC oder OOC Thema?',
        opt_type=ipy.OptionType.STRING,
        required=True,
        choices=[
            ipy.SlashCommandChoice(name='IC', value='IC'),  # In Character
            ipy.SlashCommandChoice(name='OOC', value='OOC') # Out Of Character
        ]
    )
    @ipy.slash_option(
        name='user',
        description='Um welchen User geht es?',
        opt_type=ipy.OptionType.USER,
        required=True
    )
    async def support_log(self, ctx: ipy.SlashContext, ic_ooc: str, user: ipy.Member) -> None:

        # Create Modal for logging support case
        # Fields:
        #   - Title (ShortText)
        #   - Description (ParagraphText)
        #   - Team (ParagraphText)
        modal = ipy.Modal(
            ipy.ShortText(
                label='Titel',
                custom_id='modal_support_log_title',
                placeholder='Kurzer Titel',
                required=True,
                max_length=20
            ),
            ipy.ParagraphText(
                label='Beschreibung',
                custom_id='modal_support_log_desc',
                placeholder='Beschreibe die Situation so detailliert wie nötig',
                required=True
            ),
            ipy.ParagraphText(
                label='Unterstützende Teamler (DiscordIDs)',
                custom_id='modal_support_log_team',
                placeholder='Alle Teamler, die geholfen/zugehört haben\nFormat: DiscordID, DiscordID, DiscordID',
                required=False
            ),
            title=f'{ic_ooc} Support Log {user.display_name}',
            custom_id='modal_support_log',
        )

        # Send modal and wait for response
        await ctx.send_modal(modal=modal)
        modal_ctx: ipy.ModalContext = await ctx.bot.wait_for_modal(modal)

        title = modal_ctx.responses['modal_support_log_title']
        description = modal_ctx.responses['modal_support_log_desc']
        team_str = modal_ctx.responses.get('modal_support_log_team', '')

        # If IC, type_id = 1, if OOC, type_id = 2
        if ic_ooc == 'IC':
            type_id = 1
        else:
            type_id = 2
        
        # Write support case to database
        support_case_id = db.write_case(
            discord_id=user.id,
            user_first_seen=datetime.fromtimestamp(int(str(user.joined_at).strip("<t:>"))),
            type_id=type_id,
            supporter_id=ctx.member.id,
            supporter_first_seen=datetime.fromtimestamp(int(str(ctx.member.joined_at).strip("<t:>"))),
            title=f'{ic_ooc}: {title}',
            is_primary=True,
            transcript=description
        )

        # Write supporters to support_case_supporter table
        if team_str:
            supporter_ids = [int(id.strip()) for id in team_str.split(',') if id.strip().isdigit()]
            for supporter_id in supporter_ids:
                print(supporter_id)
                db.write_support_case_supporter(support_case_id=support_case_id, supporter_id=supporter_id, is_primary=False)

        await modal_ctx.send(f"Support log '{title}' / ID: {support_case_id} erstellt.")


    # Subcommand for retrieving information about a user and send paginated embed with support cases
    # Parameters:
    #   user (ipy.Member) - The user for which the information is retrieved
    @support_base.subcommand(
        sub_cmd_name='info',
        sub_cmd_description='Hole Infos über einen User'
    )
    @ipy.slash_option(
        name='user',
        description='Welchen User willst du nackig machen?',
        opt_type=ipy.OptionType.USER,
        required=True
    )
    async def support_info(self, ctx: ipy.SlashContext, user: ipy.Member) -> None:
        
        # Get user's support cases       
        user_cases = db.get_user_cases(user.id)

        page_embeds = []
        
        # Create embeds with max 5 cases for each page
        for i in range(0, len(user_cases), 5):
            
            fields = []
            for case in user_cases[i:i+5]:
                if not case:
                    continue
                dt = datetime.strptime(case[6], '%Y-%m-%d %H:%M:%S')
                fields.append(ipy.EmbedField(name=f'Case ID: {case[0]}', value=f'{case[3]}\nVom: {ipy.Timestamp.fromdatetime(dt)}'))

            embed = ipy.Embed(
                title='Support-Fälle',
                author=ipy.EmbedAuthor(name=f'{user.username} | {user.display_name}', icon_url=LOGO_URL),
                thumbnail=user.avatar_url,
                footer=ipy.EmbedFooter(f'Discord ID: {user.id}'),
                timestamp=datetime.now(),
                color=0x00ffff,
                fields=fields
            )
            page_embeds.append(embed)
        
        paginator = Paginator.create_from_embeds(self.bot, *page_embeds)
        await paginator.send(ctx)
    

    # Subcommand for retrieving information about a support case
    # Parameters:
    #   case_id (int) - The ID of the support case
    @support_base.subcommand(
        sub_cmd_name='case',
        sub_cmd_description='Infos über einen Support-Fall'
    )
    @ipy.slash_option(
        name='case_id',
        description='Welchen Support-Fall willst du sehen?',
        opt_type=ipy.OptionType.INTEGER,
        required=True
    )
    async def support_case(self, ctx: ipy.SlashContext, case_id: int) -> None:

        # Get support case from database
        case = db.get_support_case(case_id)[0]
        if not case:
            await ctx.send(f'Case ID {case_id} existiert nicht.', ephemeral=True, delete_after=15)
            return
        
        user = await ctx.guild.fetch_member(case[1])
        dt = datetime.strptime(case[6], '%Y-%m-%d %H:%M:%S')

        # Create embed with support case information
        embed = ipy.Embed(
            title=f'Support-Fall | Case ID: {case_id}',
            author=ipy.EmbedAuthor(name=f'{user.username} | {user.display_name}', icon_url=LOGO_URL),
            footer=ipy.EmbedFooter(f'Discord ID: {user.id}'),
            timestamp=datetime.now(),
            color=0x00ffff,
            fields=[
                ipy.EmbedField(name='Titel', value=case[3]),
                ipy.EmbedField(name='Rating', value='???'),
                ipy.EmbedField(name='Vom', value=str(ipy.Timestamp.fromdatetime(dt))),
                # ipy.EmbedField(name='Beschreibung', value=case[4]),
            ]
        )

        # If transcript is too long, create paginated embed, max 512 characters per page
        if len(case[4]) > 512:
            page_embeds = []
            for i in range(0, len(case[4]), 512):
                page_embed = ipy.Embed(
                    title=f'Support-Fall | Case ID: {case_id} | Transkript {i//512 + 1}',
                    author=ipy.EmbedAuthor(name=f'{user.username} | {user.display_name}', icon_url=LOGO_URL),
                    footer=ipy.EmbedFooter(f'Discord ID: {user.id}'),
                    timestamp=datetime.now(),
                    color=0x00ffff,
                    description=case[4][i:i+512],
                )
                page_embeds.append(page_embed)
            embed.add_field(name='Transkript', value='(Seitenweise)', inline=False)
            embed = [embed, *page_embeds]
        else:
            embed.add_field(name='Transkript', value=case[4], inline=False)

        if len(case[4]) > 512:
            paginator = Paginator.create_from_embeds(self.bot, *embed)
            await paginator.send(ctx)
            return
        await ctx.send(embed=embed)