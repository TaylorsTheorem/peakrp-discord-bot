import interactions as ipy
from interactions.ext.paginators import Paginator
import requests, os
from datetime import datetime
from config import LOGO_URL

url = 'http://cheaterstats.xyz/api/checkUser.php?'

api_token = os.getenv('CHEATERSTATS_TOKEN')
headers = {
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# Extension to access cheaterstats API
# https://cheaterstats.gitbook.io/cheaterstats
class Cheaterstats(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
    # Command to check for users on the API
    @ipy.slash_command(
        name='cheater',
        description='Checke einen User nach Cheating-Discords'
    )
    @ipy.slash_option(
        name='user',
        description='Der User, der gecheckt werden soll',
        opt_type=ipy.OptionType.USER,
        required=True
    )
    async def cheater(self, ctx: ipy.SlashContext, user: ipy.User) -> None:
        data = get_user_data(user)

        # if not data.get('data'):
        #     await ctx.send(content='No Cheating Discords found!')
        await ctx.send(embed=create_embed(ctx, data, user))

        if not data.get('data'):
            return
        
        server_data = [
            {
                'server_name': item['serverName'],
                'joined': item['joinedTimestamp'],
                'roles': [
                    {
                        'role_name': role_item['name'],
                        'role_date': role_item['roleDetected'],
                    }
                    for role_item in item['roles']
                ]
            }
            for item in data.get('data')
        ]

        paginator_string = '## Gefundene Cheater Discords\n'
        for server in server_data:
            try:
                dt = datetime.strptime(server['joined'], "%Y-%m-%d %H:%M:%S")
                unix_timestamp = int(dt.timestamp())
                discord_timestamp = f"<t:{unix_timestamp}:f>"
            except:
                discord_timestamp = 'Unbekannt'

            if server['roles']:
                roles_formatted = "".join(
                    f"\n{role['role_name']} <t:{int(datetime.strptime(role['role_date'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:f>"
                    for role in server['roles']
                )
            else:
                roles_formatted = "Keine Rollen gefunden."

            paginator_string += f"**Server-Name:** {server['server_name']}\nBeigetreten: {discord_timestamp}\nRollen:{roles_formatted}\n\n"
        paginator = Paginator.create_from_string(self.bot, paginator_string, page_size=1000)
        paginator.default_color = 0xCC0000

        await paginator.send(ctx)

def get_user_data(user: ipy.User) -> dict:
    try:
        response = requests.get(f'{url}?memberId={user.id}', headers=headers)
    except:
        print(f'Couldn\'t get data from API for user_id={user.id}')
    
    data = response.json()
    return data

def create_embed(ctx: ipy.SlashContext, data: dict, user: ipy.User) -> ipy.Embed:

    embed = ipy.Embed(
        title='Cheater Stats Info',
        author=ipy.EmbedAuthor(name=f'{user.username} | {user.display_name}', icon_url=LOGO_URL),
        description=f'User: {user.mention}, ID: {user.id}',
        thumbnail=user.avatar_url,
        footer=f'Powered by Cheater Stats | .gg/cheaterstats',
        timestamp=datetime.now()
    )

    if not data.get('data'):
        embed.color = 0x00CC00
        embed.title = '✅ ' + embed.title
        embed.add_field(name='Einträge', value='Keine Einträge gefunden!')
        return embed

    num_entries = len(data)
    
    embed.color = 0xCC0000
    embed.title = '🚨 ' + embed.title
    embed.add_field(name='Einträge', value=f'{num_entries} Einträge gefunden!')

    return embed

