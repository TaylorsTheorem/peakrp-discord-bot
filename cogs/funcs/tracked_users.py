import os
import json
from config import TRACKED_USERS_FILE

_tracked_ids = set()

def ensure_file() -> None:
    os.makedirs(os.path.dirname(TRACKED_USERS_FILE), exist_ok=True)

    if not os.path.isfile(TRACKED_USERS_FILE):
        with open(TRACKED_USERS_FILE, 'w') as f:
            json.dump({'tracked_users': []}, f)

def load_tracked_users() -> None:
    global _tracked_ids
    ensure_file()
    with open(TRACKED_USERS_FILE, 'r') as f:
        data = json.load(f)
    _tracked_ids = set(data.get('tracked_users', []))

def save_tracked_users() -> None:
    with open(TRACKED_USERS_FILE, 'w') as f:
        json.dump({'tracked_users': list(_tracked_ids)}, f)

def get_tracked_users() -> None:
    return _tracked_ids

def is_tracked(id: int) -> bool:
    return id in _tracked_ids

def add_tracked_user(id: int) -> None:
    _tracked_ids.add(id)
    save_tracked_users()

def remove_tracked_user(id: int) -> None:
    _tracked_ids.remove(id)
    save_tracked_users()


import interactions as ipy

class TrackedUsers(ipy.Extension):
    def __init__(self, bot: ipy.Client):
        self.bot = bot
        load_tracked_users()

    @ipy.slash_command(
        name="track",
        description="Interaktion mit der tracked_user-Liste",
    )
    async def track_base(self, ctx: ipy.SlashContext) -> None:
        pass

    @track_base.subcommand(
        sub_cmd_name='add',
        sub_cmd_description='Füge einen User in die tracked_user-Liste hinzu'
    )
    @ipy.slash_option(
        name='user',
        description='Der User, der getracked werden soll',
        opt_type=ipy.OptionType.USER,
        required=True
    )
    async def track_add(self, ctx: ipy.SlashContext, user: ipy.User):
        if is_tracked(user.id):
            await ctx.send(f"{user.mention} wird bereits getrackt.", ephemeral=True)
            return
        add_tracked_user(user.id)
        await ctx.send(f"{user.mention} wird jetzt getrackt.", ephemeral=True)

    @track_base.subcommand(
        sub_cmd_name='remove',
        sub_cmd_description='Entferne einen User von der tracked_user-Liste'
    )
    @ipy.slash_option(
        name='user',
        description='Der User, der getracked werden soll',
        opt_type=ipy.OptionType.USER,
        required=True
    )
    async def track_remove(self, ctx: ipy.SlashContext, user: ipy.User):
        if not is_tracked(user.id):
            await ctx.send(f"{user.mention} wird nicht getrackt.", ephemeral=True)
            return
        remove_tracked_user(user.id)
        await ctx.send(f"{user.mention} wird nicht mehr getrackt.", ephemeral=True)
    
    @track_base.subcommand(
        sub_cmd_name="list",
        sub_cmd_description="Zeigt alle aktuell getrackten User"
    )
    async def track_list(self, ctx: ipy.SlashContext):
        ids = get_tracked_users()
        mentions = [f"<@{uid}>" for uid in ids]
        await ctx.send("\n".join(mentions) if mentions else "Keine Benutzer werden getrackt.", ephemeral=True)