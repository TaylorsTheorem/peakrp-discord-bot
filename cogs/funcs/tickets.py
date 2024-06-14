import interactions as ipy
from config import GUILD_ID, TICKET_CATEGORY_IDS, CHANNEL_IDS, ROLE_IDS, LOGO_URL
from datetime import datetime
import re
import cogs.funcs.db as db


# Collection of commands for ticket related tasks
class Tickets(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
    # Base command for ticket related tasks
    @ipy.slash_command(
        name='ticket',
        description='Master Ticket-Command'
    )
    async def ticket_base(self, ctx: ipy.SlashContext) -> None:
        pass
    

    # Subcommand for restarting the ticket system and send the Ticket Selection Menu to the ticket channel
    @ticket_base.subcommand(
        sub_cmd_name='restart',
        sub_cmd_description='Restart Ticket-Sytem'
    )
    async def ticket_restart(self, ctx: ipy.SlashContext) -> None:

        # Prepare the embed for the ticket selection menu
        embed = ipy.Embed(
            title='Peak Ticket-System',
            description='Um ein Ticket zu eröffnen, klicke einfach auf das Auswahl-Menü unten, mit deinem entsprechenden Anliegen. Unser Team steht bereit, um dir zu helfen!\n\nBitte habe etwas Geduld, sobald du ein Ticket erstellt hast. Unser Team wird sich so schnell wie möglich um dein Anliegen kümmern.\n',
            fields=[ipy.EmbedField(
                name='Wichtiger Hinweis',
                value='Die Ausnutzung dieses Systems für missbräuchliche Zwecke wird streng geahndet. Wir behalten uns das Recht vor, entsprechende Maßnahmen zu ergreifen.'
                )
            ],
            color=0xf9d900,
            thumbnail=LOGO_URL,
        )

        # Prepare the dropdown menu for the ticket selection
        dropdown = ipy.StringSelectMenu(
            [
                ipy.StringSelectOption(
                    label='Donator',
                    description='Ansprechpartner: Projektleitung',
                    emoji='💵',
                    value='donator'
                ),
                ipy.StringSelectOption(
                    label='Fraktion',
                    description='Ansprechpartner: Fraktionsverwaltung',
                    emoji='🏢',
                    value='fraktion'
                ),
                ipy.StringSelectOption(
                    label='Entbannung',
                    description='Ansprechpartner: Administration',
                    emoji='🆓',
                    value='entbannung'
                ),
                ipy.StringSelectOption(
                    label='Rückerstattung',
                    description='Ansprechpartner: Administration',
                    emoji='♻️',
                    value='rueckerstattung'
                ),
                ipy.StringSelectOption(
                    label='Streaming',
                    description='Ansprechpartner: Streamingverwaltung',
                    emoji='📽️',
                    value='streaming'
                ),
                ipy.StringSelectOption(
                    label='Allgemeiner Support',
                    description='Ansprechpartner: Supporter',
                    emoji='❓',
                    value='support'
                ),
                ipy.StringSelectOption(
                    label='Teambeschwerde',
                    description='Ansprechpartner: Teamverwaltung',
                    emoji='⛔',
                    value='beschwerde'
                ),
                ipy.StringSelectOption(
                    label='Teambewerbung',
                    description='Ansprechpartner: Teamverwaltung',
                    emoji='🗒️',
                    value='bewerbung'
                ),
            ],
            placeholder='Wähle dein Anliegen aus',
            custom_id='drop_ticket_select',
        )

        # Send the embed and dropdown menu to the ticket channel
        await self.bot.get_channel(CHANNEL_IDS['tickets']).send(embeds=embed, components=dropdown)
        await ctx.send(f'Ticket System restarted!')
    

    # Subcommand for adding a user to a ticket
    # Parameters:
    #   user: ipy.Member - The user to add to the ticket
    @ticket_base.subcommand(
        sub_cmd_name='add',
        sub_cmd_description='Füge jemanden ins Ticket hinzu'
    )
    @ipy.slash_option(
        name='user',
        description='Wer soll hinzugefügt werden?',
        opt_type=ipy.OptionType.USER,
        required=True
    )
    async def ticket_add(self, ctx: ipy.SlashContext, user: ipy.Member) -> None:

        # Check if the command was used in a ticket channel which is not in any ticket category
        if not ctx.channel.category in TICKET_CATEGORY_IDS.values():
            await ctx.send('Dieser Befehl kann nur in Ticket-Channels genutzt werden!', delete_after=10, ephemeral=True)
            return
        
        # Add the user to the ticket channel and set permissions
        await ctx.channel.set_permission(target=user, send_messages=True, attach_files=True, read_message_history=True, use_application_commands=True, view_channel=True)
        await ctx.channel.send(f'{user.mention} wurde in das Ticket hinzugefügt!')
    

    # Component callback for the ticket selection dropdown menu
    @ipy.component_callback('drop_ticket_select')
    async def drop_ticket_select(self, ctx: ipy.ComponentContext) -> None:
        type = ctx.values[0]

        # Get the ticket type, contact person, channel prefix and role to ping based on the selected ticket type
        match type:
            case 'donator':
                ticket_type = '💵 Donator'
                type_id = 3
                contact = 'die **Projektleitung**'
                channel_prefix = 'don-'
                role_to_ping = ROLE_IDS['pl']
            case 'fraktion':
                ticket_type = '🏢 Fraktion'
                type_id = 4
                contact = 'jemand aus der **Fraktionsverwaltung**'
                channel_prefix = 'frak-'
                role_to_ping = ROLE_IDS['fv']
            case 'entbannung':
                ticket_type = '🆓 Entbannung'
                type_id = 5
                contact = 'jemand aus der **Administration**'
                channel_prefix = 'unban-'
                role_to_ping = ROLE_IDS['admin']
            case 'rueckerstattung':
                ticket_type = '♻️ Rückerstattung'
                type_id = 6
                contact = 'jemand aus der **Administration**'
                channel_prefix = 'rueck-'
                role_to_ping = ROLE_IDS['admin']
            case 'streaming':
                ticket_type = '📽️ Streaming'
                type_id = 7
                contact = 'jemand aus der **Streamingverwaltung**'
                channel_prefix = 'stream-'
                role_to_ping = ROLE_IDS['sv']
            case 'support':
                ticket_type = '❓ Support'
                type_id = 8
                contact = 'ein **Supporter**'
                channel_prefix = 'sup-'
                role_to_ping = 'sup'
            case 'beschwerde':
                ticket_type = '⛔ Team-Beschwerde'
                type_id = 9
                contact = 'die **Teamleitung**'
                channel_prefix = 'beschw-'
                role_to_ping = ROLE_IDS['tl']
            case 'bewerbung':
                ticket_type = '🗒️ Team-Bewerbung'
                type_id = 10
                contact = 'die **Teamleitung**'
                channel_prefix = 'bew-'
                role_to_ping = ROLE_IDS['tl']
        
        # Create the main ticket embed and components
        embed = ipy.Embed(
            title=f'{ticket_type}-Ticket',
            color=0x00ffff,
            timestamp=datetime.now(),
            author=ipy.EmbedAuthor(name=f'{ctx.member.username} | {ctx.member.id}', icon_url=ctx.member.avatar_url),
            footer=ipy.EmbedFooter(text=f'Ticket nicht geclaimed'),
            thumbnail=LOGO_URL,
            fields=[
                ipy.EmbedField(name=f'Willkommen bei deinem {ticket_type[2:]}-Ticket!', value=f'Beschreibe schon mal dein Anliegen so genau wie nötig, {contact} meldet sich baldmöglichst bei dir!'),
                ipy.EmbedField(name='Wichtige Hinweise', value='Bitte behalte sämtlichen Inhalt von diesem Ticket vertraulich.\nWenn das Ticket fertig bearbeitet ist, schließe dein Ticket mit dem **roten Button**.'),
            ]
        )

        components: list[ipy.ActionRow] = ipy.spread_to_rows(
            # Buttons for claiming and closing ticket
            ipy.Button(
                custom_id='btn_ticket_claim',
                label='Claim',
                style=ipy.ButtonStyle.GREEN,
                emoji='✅'
            ),
            ipy.Button(
                custom_id='btn_ticket_close',
                label='Close',
                style=ipy.ButtonStyle.RED,
                emoji='🚫'
            )
        )

        # Create ticket channel and set permissions
        category_channel = self.bot.get_channel(TICKET_CATEGORY_IDS[type])
        ticket_channel = await category_channel.create_text_channel(name=f'{channel_prefix}{ctx.member.username}')
        await ticket_channel.set_permission(target=ctx.member, send_messages=True, attach_files=True, read_message_history=True, use_application_commands=True, view_channel=True)

        # Epemeral response to user to link to ticket channel
        await ctx.send(f'Ticket wurde erstellt:\n{ticket_channel.mention}', delete_after=15, ephemeral=True)

        # Write ticket to the database
        support_case_id = db.write_case(ctx.member.id, datetime.fromtimestamp(int(str(ctx.member.joined_at).strip("<t:>"))), type_id, title=f'Ticket: {ticket_type[2:]}')
        embed.set_author(name='' + embed.author.name + ' | ID: ' + str(support_case_id))

        await ticket_channel.send(embed=embed, components=components)

        # If the ticket type is support, ping all support roles
        if role_to_ping == 'sup':
            for i in range(3):
                role = self.bot.get_guild(GUILD_ID).get_role(ROLE_IDS[f'sup{i+1}'])
                await ticket_channel.send(role.mention, delete_after=1)
        # Else ping the specific role
        else:
            await ticket_channel.send(self.bot.get_guild(GUILD_ID).get_role(role_to_ping).mention, delete_after=1)
        await ticket_channel.send(ctx.author.mention, delete_after=1)


    # Component callback for the claim button
    @ipy.component_callback('btn_ticket_claim')
    async def btn_ticket_claim(self, ctx: ipy.ComponentContext) -> None:

        # Check if the user has the team role
        if not ctx.member.has_role(ROLE_IDS['team']):
            await ctx.send('Du kannst das Ticket nicht claimen!', delete_after=10)
            return
        await ctx.send(f'Das Ticket wurde von {ctx.member.mention} geclaimed!')

        # Get the first message (= ticket embed) in the ticket channel and set footer to claimed by supporter
        messages = await ctx.channel.fetch_messages()
        embed = messages[-1].embeds[0]
        embed.set_footer(text=f'Geclaimed von {ctx.member.nickname} | {ctx.member.id}')
        await messages[-1].edit(embed=embed)
        support_case_id = extract_last_integer(embed.author.name)

        # Update the database with the supporter id and set the supporter as primary
        db.update_support_case_supporter(support_case_id=support_case_id, column='supporter_id', value=ctx.member.id)
        db.update_support_case_supporter(support_case_id=support_case_id, column='is_primary', value=True)
    

    # Component callback for the close button
    @ipy.component_callback('btn_ticket_close')
    async def btn_ticket_close(self, ctx: ipy.ComponentContext) -> None:

        # Check if the user is the ticket owner
        messages = await ctx.channel.fetch_messages()
        if not (ctx.member.username == extract_first_string(messages[-1].embeds[0].author.name)):
            await ctx.send(f'{ctx.user.mention} Du kannst dieses Ticket nicht schließen!', delete_after=10, ephemeral=True)
            return
        
        # Check if user is sure to close the ticket
        components: list[ipy.ActionRow] = ipy.spread_to_rows(
            ipy.Button(
                custom_id='btn_ticket_close_yes',
                label='Ja',
                style=ipy.ButtonStyle.RED,
                emoji='👍'
            ),
            ipy.Button(
                custom_id='btn_ticket_close_no',
                label='Abbrechen',
                style=ipy.ButtonStyle.SECONDARY,
                emoji='❌'
            )
        )

        await ctx.send('Möchtest du dein Ticket wirklich schließen?', components=components)
    

    # Component callback for the yes button to close the ticket (= user confirmed to close the ticket)
    @ipy.component_callback('btn_ticket_close_yes')
    async def btn_ticket_close_yes(self, ctx: ipy.ComponentContext) -> None:

        # Get all messages in the ticket channel for transcript
        messages = await ctx.channel.fetch_messages(limit=100)

        await messages[0].delete()
        await ctx.channel.send('Ticket wurde geschlossen ✅')

        # Remove user permissions for the ticket channel and move it to the ticket logs category
        await ctx.channel.set_permission(target=ctx.member, view_channel=False, send_messages=False, read_message_history=False)
        await ctx.channel.edit(parent_id=TICKET_CATEGORY_IDS['ticket_logs'])

        # Disable all Claim and Close buttons
        comps = [setattr(comp, 'disabled', True) or comp for comp in messages[-1].components[0].components]
        await messages[-1].edit(components=comps)

        # Write the transcript to the database
        transcript = ''
        for message in reversed(messages[1:-1]):
            dt = datetime.fromtimestamp(message.created_at.timestamp()).strftime('%Y-%m-%d %H:%M:%S')
            transcript += f'{message.author.username} ({message.author.id}) | {dt}\n'
            transcript += f' > {message.content}\n\n'
        db.update_support_case(extract_last_integer(messages[-1].embeds[0].author.name), column='description', value=transcript)


    # Component callback for the drop down menu to rate the ticket
    # TODO: Implement rating system
    @ipy.component_callback('drop_ticket_rating')
    async def drop_ticket_rating(self, ctx: ipy.ComponentContext) -> None:
        dropdown = ipy.StringSelectMenu(
            [
                ipy.StringSelectOption(
                    label='Nein, danke.',
                    value=-1
                ),
                ipy.StringSelectOption(
                    label='⭐ - 1 Stern',
                    value=1
                ),
                ipy.StringSelectOption(
                    label='⭐⭐ - 2 Sterne',
                    value=2
                ),
                ipy.StringSelectOption(
                    label='⭐⭐⭐ - 3 Sterne',
                    value=3
                ),
                ipy.StringSelectOption(
                    label='⭐⭐⭐⭐ - 4 Sterne',
                    value=4
                ),
                ipy.StringSelectOption(
                    label='⭐⭐⭐⭐⭐ - 5 Sterne',
                    value=5
                )
            ],
            placeholder='Bitte wähle deine Bewertung aus.',
            custom_id='drop_ticket_rating',
        )

        embed = ipy.Embed(
            title='Peak Ticket-System',

        )
    

    # Component callback for the no button to close the ticket
    @ipy.component_callback('btn_ticket_close_no')
    async def btn_ticket_close_no(self, ctx: ipy.ComponentContext) -> None:
        messages = await ctx.channel.fetch_messages()
        await messages[0].delete()


# Helper functions for extracting information from strings
def extract_last_integer(string):
    match = re.search(r'\d+$', string)
    if match:
        return int(match.group())
    else:
        return None

def extract_middle_integer(string):
    match = re.search(r'\| (\d+) \|', string)
    if match:
        return int(match.group(1))
    else:
        return None
    
def extract_first_string(string):
    return string.split(' | ')[0].strip()