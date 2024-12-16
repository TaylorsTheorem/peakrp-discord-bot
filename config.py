import interactions as ipy

# Some constants needed for many parts of the bot
GUILD_ID = 1198983389479452722

LOGO_URL = 'https://cdn.discordapp.com/attachments/1242538461123317850/1248180296483082292/ezgif-3-a141953a13_-_Copy-removebg-preview.png?ex=6662b9fc&is=6661687c&hm=b6bfa78c7fb62688a648a4fac8c070fb80f04835f0672af68d13db1f32c7bc53&'

DATABASE_PATH = "db/peak.db"
DATABASE_SETUP_FILE = "db/setup.sql"

INTENTS = ipy.Intents.ALL

BOT_STATUS = ipy.Status.DND
BOT_ACTIVITY = ipy.Activity(
    name='Peak Roleplay',
    type=ipy.ActivityType.COMPETING
)

# Colors used throughout the bot
COLORS = {
    'default': '7EDCF8', # Main community color
    'success': '00FF00',
    'error': 'FF0000',
    'info': '0000FF',
    'warning': 'FFFF00',
}

EMOJI_IDS = {
    'peak': 1248180032510365756,
    'upvote': 1265745866291941406,
    'downvote': 1265745856041193482,
}

CHANNEL_IDS = {
    'abmelden': 1242186810369642518,
    'team_commands': 1242186789746114611,
    'support_waiting': 1242186726089166953,
    'tickets': 1242186705809969295,
    'support_chat': 1248009829885411419,

    # Sentinel log channels
    'presence_update': 1283487302571790367,
    'typing_start': 1283487528585789470,
}

TICKET_CATEGORY_IDS = {
    'donator': 1242186654702239794,
    'fraktion': 1242186661627166931,
    'entbannung': 1242186662885326888,
    'rueckerstattung': 1242186656111530014,
    'streaming': 1242186668224544903,
    'support': 1242186660167290983,
    'beschwerde': 1242186667327226066,
    'bewerbung': 1242186667327226066,
    'ticket_logs': 1242186669491359927,
}

ROLE_IDS = {
    'pl': 1242186516503990323,
    'admin': 1242186527757303808,
    'sup3': 1245105543249662012,
    'sup2': 1242186543150403594,
    'sup1': 1242186543783743601,
    'tl': 1242186526574772339,
    'fv': 1242186538897641492,
    'sv': 1242186552218615968,
    'team': 1242186564172517437,
    'wl': 1242186572825231441,
    'citizen': 1242186573727010826
}

USER_IDS = {
    'bot': 1088230837562122370,
    'maestro': 120073956924456960,
    'deltixx': 630147302639534080,
}