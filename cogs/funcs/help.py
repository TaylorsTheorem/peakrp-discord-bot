import interactions as ipy
from interactions.ext.paginators import Paginator
from config import LOGO_URL, CMDS_PER_HELP_PAGE
from datetime import datetime

class Help(ipy.Extension):
    def __init__(self, bot):
        self.bot: ipy.Client = bot
    
    @ipy.listen()
    async def on_startup(self, event: ipy.events.Startup):
        self.help_commands: list[ipy.SlashCommand] = []

        sorted_cmds = sort_nested_dict(self.bot.interaction_tree[0])

        for cmd in sorted_cmds.values():
            self.create_cmd_recursive(cmd)
    
    @ipy.slash_command(
        name='help',
        description='Hilfe zu dem Bot und seinen Funktionen',
    )
    async def help(self, ctx: ipy.SlashContext):
        fields_list = []

        for cmd in self.help_commands:
            if cmd.is_enabled(ctx):
                if isinstance(cmd, ipy.SlashCommand):
                    name = str(cmd.name)
                    if cmd.group_name:
                        name += " " + str(cmd.group_name)
                    if cmd.sub_cmd_name:
                        name += " " + str(cmd.sub_cmd_name)

                    desc = str(cmd.description)
                    if cmd.group_name:
                        desc = str(cmd.group_description)
                    if cmd.sub_cmd_name:
                        desc = str(cmd.sub_cmd_description)

                    fields_list.append(ipy.EmbedField(name=f"/{name}", value=desc))
                else:
                    fields_list.append(ipy.EmbedField(name=f"{cmd.name}", value="Keine Beschreibung vorhanden."))

        # divide embed fields into lists of maximum N size
        chunked_fields_list = [fields_list[i : i + CMDS_PER_HELP_PAGE] for i in range(0, len(fields_list), CMDS_PER_HELP_PAGE)]
        embeds = []
        for i, fields_list in enumerate(chunked_fields_list):
            embed = ipy.Embed(
                title="Help Peak System",
                color=0x00ffff,
                footer=f"Seite {i+1}/{len(chunked_fields_list)} | Bei Fragen oder Problemen wende dich an Maestro!",
                timestamp=datetime.now(),
                thumbnail=LOGO_URL
            )
            embed.add_fields(*fields_list)
            embeds.append(embed)

        paginator = Paginator.create_from_embeds(self.bot, *embeds)
        await paginator.send(ctx)

    def create_cmd_recursive(self, cmd):
        if isinstance(cmd, ipy.SlashCommand):
            self.help_commands.append(cmd)
        elif isinstance(cmd, dict):
            for sub_cmd in cmd.values():
                self.create_cmd_recursive(sub_cmd)
        else:
            raise Exception(f"Unbekannter Command, schreibe /help: {type(cmd)}")
        
def sort_nested_dict(d):
    if not isinstance(d, dict):
        return d
    return {k: sort_nested_dict(v) for k, v in sorted(d.items())}