import requests, json

url = "https://servers-frontend.fivem.net/api/servers/single/avjqp3"

headers = {
    "User-agent": 'Mozilla',
}
data = requests.get(url, headers=headers)


print(data.json())

import interactions as ipy

class Cfx_API(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
    # @ipy.command(name='cfx')
    # async def cfx(self, ctx: ipy.Context):
    #     data = requests.get(url, headers=headers)
    #     await ctx.send(data.json())
    
    # @ipy.command(name='cfx.status')
    # async def cfx_status(self, ctx: ipy.Context):
    #     data = requests.get(url, headers=headers)
    #     status = data.json().get('Data').get('Data').get('clients').get('online')
    #     await ctx.send(f"Status: {status}")
    
    # @ipy.command(name='cfx.players')
    # async def cfx_players(self, ctx: ipy.Context):
    #     data = requests.get(url, headers=headers)
    #     players = data.json().get('Data').get('Data').get('clients').get('online')
    #     await ctx.send(f"Players: {players}")
    
    # @ipy.command(name='cfx.max_players')
    # async def cfx_max_players(self, ctx: ipy.Context):
    #     data = requests.get(url, headers=headers)
    #     max_players = data.json().get('Data').get('Data').get('sv_maxclients')
    #     await ctx.send(f"Max Players: {max_players}")
    
    # @ipy.command(name='cfx.name')
    # async def cfx_name(self, ctx: ipy.Context):
    #     data = requests.get(url, headers=headers)
    #     name = data.json().get('Data').get('Data').get('hostname')
    #     await ctx.send(f"Server Name: {name}")
    
    # @ipy.command(name='cfx.ip')
    # async def cfx_ip(self, ctx: ipy.Context):
    #     data = requests.get(url, headers=headers)
    #     ip = data.json().get('Data').get('Data').get('connectEndPoints')[0]
    #     await ctx.send(f"Server IP: {ip}")
    
    # @ipy.command(name='cfx.port')
    # async def cfx_port(self, ctx: ipy.Context):
    #     data = requests.get(url, headers=headers)
    #     port = data.json().get('Data').get('Data').get('connectEndPoints')[1]
    #     await ctx.send(f"Server Port: {port}")
    
    # @ipy.command(name='cfx.version')

    @ipy.slash_command(
        name='cfx',
        description='Get FiveM server information',
    )
    async def cfx(self, ctx: ipy.SlashContext):
        pass
    
    @cfx.subcommand(
        sub_cmd_name='players',
        sub_cmd_description='Get the number of players on the server',
    )
    @ipy.slash_option(
        name='server',
        description='The server ID',
        required=True,
        opt_type=ipy.OptionType.STRING
    )
    async def cfx_players(self, ctx: ipy.SlashContext, server: str):
        url = f"https://servers-frontend.fivem.net/api/servers/single/{server}"

        headers = {
            "User-agent": 'Mozilla',
        }
        try:
            response = requests.get(url, headers=headers)
        except:
            await ctx.send("Server not found")
            return

        data = response.json()
        players = data.get('Data').get('players')
        
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)

        from interactions.ext.paginators import Paginator
        paginator = Paginator.create_from_string(self.bot, players, page_size=1000)
        await paginator.send(ctx)