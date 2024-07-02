import requests, json, re
import interactions as ipy
from config import LOGO_URL


# Collection of commands for cfx api interaction
class Cfx_API(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot


    # Base command for cfx api interaction
    @ipy.slash_command(
        name='cfx',
        description='Get FiveM server information',
    )
    async def cfx_base(self, ctx: ipy.SlashContext):
        pass


    # Subcommand for getting the server information
    # Parameters:
    #   - server_id: str (cfx server id)
    @cfx_base.subcommand(
        sub_cmd_name='info',
        sub_cmd_description='Get the server information',
    )
    @ipy.slash_option(
        name='server_id',
        description='The server ID',
        required=True,
        opt_type=ipy.OptionType.STRING
    )
    async def cfx_info(self, ctx: ipy.SlashContext, server_id: str):
        data = get_server_data(server_id)  # Retrieve data from the server info API

        # Save data to a file, this is just for testing purposes
        # with open('data.json', 'w') as f:
        #     json.dump(data, f, indent=4)

        image_url = f'https://servers-frontend.fivem.net/servers/icon/{server_id}/{data.get("Data").get("iconVersion")}.png'    # Server icon URL

        # Create and send an embed with the server information
        embed = ipy.Embed(
            author=ipy.EmbedAuthor(name=get_host_name(data), icon_url=LOGO_URL, url=f"https://servers.fivem.net/servers/detail/{server_id}"),
            title=f'Server Informationen',
            color=0x00ffff,
            fields=[
                ipy.EmbedField(name='Display Name', value=get_display_name(data)),
                ipy.EmbedField(name='ID', value=server_id, inline=True),
                ipy.EmbedField(name='Players', value=f'{data.get("Data").get("clients")} / {data.get("Data").get("sv_maxclients")}', inline=True),
                ipy.EmbedField(name='Resources', value=f'{len(data.get("Data").get("resources"))}', inline=True),
                ipy.EmbedField(name='IP', value=data.get("Data").get("connectEndPoints")[0], inline=True),
                ipy.EmbedField(name='Game Version', value=data.get("Data").get("vars").get("sv_enforceGameBuild"), inline=True),
                ipy.EmbedField(name='Pure Level', value=data.get("Data").get("vars").get("sv_pureLevel"), inline=True),
                ipy.EmbedField(name='Owner', value=f'{data.get("Data").get("ownerName")} - ID: {data.get("Data").get("ownerID")}')
            ],
            images=[data.get('Data').get('vars').get('banner_detail#original_url')],
            thumbnail=image_url
        )

        await ctx.send(embed=embed)
    

    # Subcommand for getting a list of players on a server
    # Parameters:
    #   - server_id: str (cfx server id)
    @cfx_base.subcommand(
        sub_cmd_name='players',
        sub_cmd_description='Get the number of players on the server',
    )
    @ipy.slash_option(
        name='server_id',
        description='The server ID',
        required=True,
        opt_type=ipy.OptionType.STRING
    )
    async def cfx_players(self, ctx: ipy.SlashContext, server_id: str):
        data = get_server_data(server_id)    # Retrieve data from the server info API

        # Extract player data from the response, filter for relevant information
        player_data = [
            {
                'id': item['id'],
                'identifiers': item['identifiers'],
                'name': item['name'],
                'ping': item['ping'],
            }
            for item in data.get('Data').get('players')
        ]
        
        # Save data to a file, this is just for testing purposes, enable if needed
        # with open('data.json', 'w') as f:
        #     json.dump(data, f, indent=4)
        # with open('players.json', 'w') as f:
        #     json.dump(player_data, f, indent=4)

        # Create a string for the paginator
        paginator_string = f'## Aktuelle Spieler auf:\n### {get_host_name(data)}\n({server_id})\n\n'

        # Add player data to the paginator string
        for player in player_data:
            paginator_string += f"**{player['name']}**\n{player['identifiers']}\nID: {player['id']}, Ping:{player['ping']}ms\n\n"

        # Create a paginator from the string and send it
        from interactions.ext.paginators import Paginator
        paginator = Paginator.create_from_string(self.bot, paginator_string, page_size=1000)
        await paginator.send(ctx)


    # Subcommand for getting a list of resources on a server
    # Parameters:
    #   - server_id: str (cfx server id)
    @cfx_base.subcommand(
        sub_cmd_name='resources',
        sub_cmd_description='Get the resources on the server',
    )
    @ipy.slash_option(
        name='server_id',
        description='The server ID',
        required=True,
        opt_type=ipy.OptionType.STRING
    )
    async def cfx_resources(self, ctx: ipy.SlashContext, server_id: str):
        data = get_server_data(server_id)  # Retrieve data from the server info API

        # Extract resources list from the response
        resources = data.get('Data').get('resources')

        # Create a string for the paginator
        paginator_string = f'## Aktuelle Ressourcen auf:\n### {get_host_name(data)}\n({server_id})\n\n'

        # Add resources to the paginator string
        for resource in resources:
            paginator_string += f"{resource}\n"
        
        # Create a paginator from the string and send it
        from interactions.ext.paginators import Paginator
        paginator = Paginator.create_from_string(self.bot, paginator_string, page_size=500)
        await paginator.send(ctx)


# Helper functions

# Get the data from the server info API
def get_server_data(server_id: str):
    url = f"https://servers-frontend.fivem.net/api/servers/single/{server_id}"  # Server info API URL

    # Send a request to the server info API and save data
    headers = {
        "User-agent": 'Mozilla',
    }
    try:
        response = requests.get(url, headers=headers)
    except:
        return None

    data = response.json()
    return data

# Get the hostname (in data: 'sv_projectName') from the server data (and clean the string) 
def get_host_name(data) -> str:
    # Regex to remove ^1, ^2, etc. color codes and leading spaces
    host_name = re.sub(r'(\^\d|\s*^\s*)', '', data.get('Data').get('vars').get('sv_projectName'))
    return host_name

# Get the display name (in data: 'hostname') from the server data (and clean the string)
def get_display_name(data) -> str:
    # Regex to remove ^1, ^2, etc. color codes
    display_name = re.sub(r'\^\d', '', data.get('Data').get('hostname'))
    return display_name