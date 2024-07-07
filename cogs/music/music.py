# Inspired by https://github.com/axiinyaa/music-bot-template
# and https://github.com/devoxin/Lavalink.py/blob/development/examples/music.py

import re
import uuid
import interactions as ipy
import lavalink
from interactions_lavalink import Lavalink, Player
from interactions_lavalink.events import TrackStart
import random, asyncio

# Extension for a playing music with Lavalink
class Music(ipy.Extension):
    def __init__(self, bot) -> None:
        self.bot: ipy.Client = bot
    
    # Initialize Lavalink
    @ipy.listen()
    async def on_ready(self) -> None:
        self.lavalink: Lavalink = Lavalink(self.bot)
        self.lavalink.add_node('lavalink', '2337', 'youshallnotpass', 'de')
        print('Music extension loaded')

    # Base command for music
    @ipy.slash_command(
        name='music',
        description='Spiele Musik ab',
    )
    async def music(self, ctx: ipy.SlashContext) -> None:
        pass

    # Subcommand for playing music
    # Parameters:
    #   query: str - The query to search for a song
    @music.subcommand(sub_cmd_description='Spiele Musik ab!')
    @ipy.slash_option(
        name='query',
        description='Suche nach einem Lied',
        opt_type=ipy.OptionType.STRING,
        required=True
    )
    async def play(self, ctx: ipy.SlashContext, query: str) -> None:
        # Get voice state of the author, if not in a voice channel, return
        voice_state = ctx.author.voice
        if not voice_state or not voice_state.channel:
            await ctx.send("Du bist in keinem Channel.", ephemeral=True, delete_after=10)
            return
        
        # Regex for checking if the query is a URL, if not add ytsearch: to the query for searching on youtube
        url_rx = re.compile(r'https?://(?:www\.)?.+')
        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        message = await send_fancy_message(ctx, f"Loading search results...")

        # Connect to the voice channel and get tracks
        player = await self.lavalink.connect(voice_state.guild.id, voice_state.channel.id)
        results: lavalink.LoadResult = await self.lavalink.client.get_tracks(query, check_local=False)
        
        # If no results found, return
        if results.load_type == lavalink.LoadType.EMPTY:
            return await ctx.send("Konnte keine Ergebnisse zu deiner Anfrage finden...")
        # If the load type is a playlist, add all tracks to the queue
        elif results.load_type == lavalink.LoadType.PLAYLIST:
            tracks = results.tracks
            for track in tracks:
                player.add(track=track, requester=ctx.author.id)
        # If the load type is a track, add the track to the queue
        else:
            track = results.tracks[0]

            player.add(track=track, requester=ctx.author.id)
        
        await message.delete()
        
        player.store('Channel', ctx.channel) # Store the channel for later use
        
        # If the player playing, add the track to the queue, else play the track
        if player.is_playing:
            add_to_queue_embed = self.create_added_to_playlist_embed(ctx, player, tracks[0])

            return await ctx.channel.send(embeds=add_to_queue_embed)
        else:
            await player.play()
    
    # Subcommand for pausing the music
    @music.subcommand(sub_cmd_description="Stoppe die Musik!")
    async def stop(self, ctx: ipy.SlashContext):
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if player is None:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        player.current = None
        await self.lavalink.disconnect(ctx.guild_id)

        await send_fancy_message(ctx, f"{ctx.author.mention} hat den Player gestopped.")

    # Base command for adding filters to the player
    @ipy.slash_command(
        name='music_filter',
        description='Stelle einen Filter ein!'
    )
    async def music_filter(self, ctx: ipy.SlashContext):
        pass
    
    # Subcommand for setting an equalizer
    # Parameters:
    #   band: int - Band of the equalizer, must be between 0 and 14
    #   gain: float - Gain of the equalizer, must be between -0.25 and 1.0
    @music_filter.subcommand(sub_cmd_description="Stelle einen Equalizer ein!")
    @ipy.slash_option(name='band', description='Band des Equalizers.', opt_type=ipy.OptionType.INTEGER, required=True)
    @ipy.slash_option(name='gain', description='Gain des Equalizers.', opt_type=ipy.OptionType.NUMBER, required=True)
    async def equalizer(self, ctx: ipy.SlashContext, band: int = 0, gain: float = 0):
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        if band == 0 and gain == 0:
            await player.remove_filter('equalizer')
            await send_fancy_message(ctx, '**Equalizer** ausgeschaltet')

        if band < 0 or band > 14:
            return await send_fancy_message(ctx, "Band muss zwischen 0 und 14 sein.", color=0xff0000, ephemeral=True)

        if gain < -0.25 or gain > 1.0:
            return await send_fancy_message(ctx, "Gain muss zwischen -0.25 und 1.0 sein.", color=0xff0000, ephemeral=True)


        equalizer = lavalink.Equalizer()
        equalizer.update(band=band, gain=gain)
        await player.set_filter(equalizer)

        await send_fancy_message(ctx, f"{ctx.user.mention} hat den Equalizer auf Band {band} und Gain {gain} gesetzt.")

    # Subcommand for setting a low pass filter
    # Parameters:
    #   strength: float - Strength of the low pass filter, must be between 0 and 100
    @music_filter.subcommand(sub_cmd_description="Stelle einen Low Pass Filter ein!")
    @ipy.slash_option(name='strength', description='Setze den Lowpass Filter.', opt_type=ipy.OptionType.INTEGER, required=True)
    async def lowpass(self, ctx: ipy.SlashContext, strength: float = 0):

        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        if strength < 0:
            return await send_fancy_message(ctx, "Stärke muss größer als 0 sein.", color=0xff0000, ephemeral=True)

        if strength > 100:
            return await send_fancy_message(ctx, "Stärke muss kleiner als 100 sein.", color=0xff0000, ephemeral=True)
        
        if strength == 0:
            await player.remove_filter('lowpass')
            await send_fancy_message(ctx, '**Low Pass Filter** ausgeschaltet')

        lowpass = lavalink.LowPass()
        lowpass.update(smoothing=strength)
        await player.set_filter(lowpass)

        await send_fancy_message(ctx, f"{ctx.user.mention} hat den Lowpass Filter auf {strength} gesetzt.")
    
    # Subcommand for setting a karaoke filter
    # Parameters:
    #   level: float - Level of the karaoke filter, must be greater than 0
    #   mono_level: float - Mono level of the karaoke filter, must be greater than 0
    #   filter_band: float - Filter band of the karaoke filter, must be greater than 0
    #   filter_width: float - Filter width of the karaoke filter, must be greater than 0
    @music_filter.subcommand(sub_cmd_description="Stelle einen Karaoke Filter ein!")
    @ipy.slash_option(name='level', description='Level des Karaoke Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    @ipy.slash_option(name='mono_level', description='Mono Level des Karaoke Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    @ipy.slash_option(name='filter_band', description='Filter Band des Karaoke Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    @ipy.slash_option(name='filter_width', description='Filter Width des Karaoke Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    async def karaoke(self, ctx: ipy.SlashContext, level: float = 0, mono_level: float = 0, filter_band: float = 0, filter_width: float = 0):
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        if level < 0 or mono_level < 0 or filter_band < 0 or filter_width < 0:
            return await send_fancy_message(ctx, "Alle Werte müssen größer gleich 0 sein.", color=0xff0000, ephemeral=True)

        if level == 0 and mono_level == 0 and filter_band == 0 and filter_width == 0:
            await player.remove_filter('karaoke')
            await send_fancy_message(ctx, '**Karaoke Filter** ausgeschaltet')

        karaoke = lavalink.Karaoke()
        karaoke.update(level=level, mono_level=mono_level, filter_band=filter_band, filter_width=filter_width)
        await player.set_filter(karaoke)

        await send_fancy_message(ctx, f"{ctx.user.mention} hat den Karaoke Filter auf {level}, {mono_level}, {filter_band}, {filter_width} gesetzt.")

    # Subcommand for setting a timescale filter
    # Parameters:
    #   pitch: float - Pitch of the timescale filter, must be greater than 0.1
    #   rate: float - Rate of the timescale filter, must be greater than 0.1
    #   speed: float - Speed of the timescale filter, must be greater than 0.1
    @music_filter.subcommand(sub_cmd_description='Stelle einen Timescale Filter ein!')
    @ipy.slash_option(name='pitch', description='Pitch des Timescale Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    @ipy.slash_option(name='rate', description='Rate des Timescale Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    @ipy.slash_option(name='speed', description='Speed des Timescale Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    async def timescale(self, ctx: ipy.SlashContext, pitch: float = 1, rate: float = 1, speed: float = 1):
            
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        if pitch < 0.1 or rate < 0.1 or speed < 0.1:
            return await send_fancy_message(ctx, "Alle Werte müssen größer gleich 0.1 sein.", color=0xff0000, ephemeral=True)

        if pitch == 0 and rate == 0 and speed == 0:
            await player.remove_filter('timescale')
            await send_fancy_message(ctx, '**Timescale Filter** ausgeschaltet')

        timescale = lavalink.Timescale()
        timescale.update(pitch=pitch, rate=rate, speed=speed)
        await player.set_filter(timescale)

        await send_fancy_message(ctx, f"{ctx.user.mention} hat den Timescale Filter auf {pitch}, {rate}, {speed} gesetzt.")
    
    # Subcommand for setting a tremolo filter
    # Parameters:
    #   depth: float - Depth of the tremolo filter, must be greater than 0 and less than 1
    #   frequency: float - Frequency of the tremolo filter, must be greater than 0
    @music_filter.subcommand(sub_cmd_description='Stelle einen Tremolo Filter ein!')
    @ipy.slash_option(name='depth', description='Depth des Tremolo Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    @ipy.slash_option(name='frequency', description='Frequency des Tremolo Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    async def tremolo(self, ctx: ipy.SlashContext, depth: float= 0, frequency: float= 0):
                
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        if depth == 0 and frequency == 0:
            await player.remove_filter('tremolo')
            await send_fancy_message(ctx, '**Tremolo Filter** ausgeschaltet')

        if depth <= 0 or frequency <= 0:
            return await send_fancy_message(ctx, "Alle Werte müssen größer als 0 sein.", color=0xff0000, ephemeral=True)
        
        if depth > 1:
            return await send_fancy_message(ctx, "Depth muss kleiner gleich 1 sein.", color=0xff0000, ephemeral=True)

        tremolo = lavalink.Tremolo()
        tremolo.update(depth=depth, frequency=frequency)
        await player.set_filter(tremolo)

        await send_fancy_message(ctx, f"{ctx.user.mention} hat den Tremolo Filter auf {depth}, {frequency} gesetzt.")
    
    # Subcommand for setting a vibrato filter
    # Parameters:
    #   depth: float - Depth of the vibrato filter, must be greater than 0 and less than 1
    #   frequency: float - Frequency of the vibrato filter, must be greater than 0 and less than 14
    @music_filter.subcommand(sub_cmd_description='Stelle einen Vibrato Filter ein!')
    @ipy.slash_option(name='depth', description='Depth des Vibrato Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    @ipy.slash_option(name='frequency', description='Frequency des Vibrato Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    async def vibrato(self, ctx: ipy.SlashContext, depth: float = 0, frequency: float = 0):
                        
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        if depth == 0 and frequency == 0:
            await player.remove_filter('vibrato')
            await send_fancy_message(ctx, '**Vibrato Filter** ausgeschaltet')

        if depth <= 0 or frequency <= 0:
            return await send_fancy_message(ctx, "Alle Werte müssen größer als 0 sein.", color=0xff0000, ephemeral=True)
        
        if depth > 1:
            return await send_fancy_message(ctx, "Depth muss kleiner gleich 1 sein.", color=0xff0000, ephemeral=True)
        
        if frequency > 14:
            return await send_fancy_message(ctx, "Frequency muss kleiner gleich 14 sein.", color=0xff0000, ephemeral=True)

        vibrato = lavalink.Vibrato()
        vibrato.update(depth=depth, frequency=frequency)
        await player.set_filter(vibrato)

        await send_fancy_message(ctx, f"{ctx.user.mention} hat den Vibrato Filter auf {depth}, {frequency} gesetzt.")
    
    # Subcommand for setting a rotation filter
    # Parameters:
    #   rotation_hz: float - Rotation of the rotation filter, must be greater than 0
    @music_filter.subcommand(sub_cmd_description='Stelle einen Rotation Filter ein!')
    @ipy.slash_option(name='rotation', description='Rotation des Rotation Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    async def rotation(self, ctx: ipy.SlashContext, rotation_hz: float = 0):
                                
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        if rotation < 0:
            return await send_fancy_message(ctx, "Rotation muss größer gleich 0 sein.", color=0xff0000, ephemeral=True)

        if rotation == 0:
            await player.remove_filter('rotation')
            await send_fancy_message(ctx, '**Rotation Filter** ausgeschaltet')

        rotation = lavalink.Rotation()
        rotation.update(rotation_hz=rotation_hz)
        await player.set_filter(rotation)

        await send_fancy_message(ctx, f"{ctx.user.mention} hat den Rotation Filter auf {rotation} gesetzt.")

    # Subcommand for setting a distortion filter
    # Parameters:
    #   sin_offset: float - Sin offset of the distortion filter
    #   sin_scale: float - Sin scale of the distortion filter
    #   cos_offset: float - Cos offset of the distortion filter
    #   cos_scale: float - Cos scale of the distortion filter
    #   tan_offset: float - Tan offset of the distortion filter
    #   tan_scale: float - Tan scale of the distortion filter
    #   offset: float - Offset of the distortion filter
    #   scale: float - Scale of the distortion filter
    @music_filter.subcommand(sub_cmd_description='Stelle einen Distortion Filter ein!')
    @ipy.slash_option(name='sin_offset', description='Sin Offset des Distortion Filters.', opt_type=ipy.OptionType.NUMBER, required=False)
    @ipy.slash_option(name='sin_scale', description='Sin Scale des Distortion Filters.', opt_type=ipy.OptionType.NUMBER, required=False)
    @ipy.slash_option(name='cos_offset', description='Cos Offset des Distortion Filters.', opt_type=ipy.OptionType.NUMBER, required=False)
    @ipy.slash_option(name='cos_scale', description='Cos Scale des Distortion Filters.', opt_type=ipy.OptionType.NUMBER, required=False)
    @ipy.slash_option(name='tan_offset', description='Tan Offset des Distortion Filters.', opt_type=ipy.OptionType.NUMBER, required=False)
    @ipy.slash_option(name='tan_scale', description='Tan Scale des Distortion Filters.', opt_type=ipy.OptionType.NUMBER, required=False)
    @ipy.slash_option(name='offset', description='Offset des Distortion Filters.', opt_type=ipy.OptionType.NUMBER, required=False)
    @ipy.slash_option(name='scale', description='Scale des Distortion Filters.', opt_type=ipy.OptionType.NUMBER, required=False)
    async def distortion(self, ctx: ipy.SlashContext, sin_offset: float = 0, sin_scale: float = 0, cos_offset: float = 0, cos_scale: float = 0, tan_offset: float = 0, tan_scale: float = 0, offset: float = 0, scale: float = 0):                              
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        if sin_offset == 0 and sin_scale == 0 and cos_offset == 0 and cos_scale == 0 and tan_offset == 0 and tan_scale == 0 and offset == 0 and scale == 0:
            await player.remove_filter('distortion')
            await send_fancy_message(ctx, '**Distortion Filter** ausgeschaltet')

        distortion = lavalink.Distortion()
        distortion.update(sin_offset=sin_offset, sin_scale=sin_scale, cos_offset=cos_offset, cos_scale=cos_scale, tan_offset=tan_offset, tan_scale=tan_scale, offset=offset, scale=scale)
        await player.set_filter(distortion)

        await send_fancy_message(ctx, f"{ctx.user.mention} hat den Distortion Filter auf {sin_offset}, {sin_scale}, {cos_offset}, {cos_scale}, {tan_offset}, {tan_scale}, {offset}, {scale} gesetzt.")

    # Subcommand for setting a channel mix filter
    # Parameters:
    #   left_to_left: float - Left to Left of the channel mix filter, must be between 0 and 1
    #   left_to_right: float - Left to Right of the channel mix filter, must be between 0 and 1
    #   right_to_left: float - Right to Left of the channel mix filter, must be between 0 and 1
    #   right_to_right: float - Right to Right of the channel mix filter, must be between 0 and 1
    @music_filter.subcommand(sub_cmd_description='Stelle einen Channel Mix Filter ein!')
    @ipy.slash_option(name='left_to_left', description='Left to Left des Channel Mix Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    @ipy.slash_option(name='left_to_right', description='Left to Right des Channel Mix Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    @ipy.slash_option(name='right_to_left', description='Right to Left des Channel Mix Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    @ipy.slash_option(name='right_to_right', description='Right to Right des Channel Mix Filters.', opt_type=ipy.OptionType.NUMBER, required=True)
    async def channelmix(self, ctx: ipy.SlashContext, left_to_left: float = 0, left_to_right: float = 0, right_to_left: float = 0, right_to_right: float = 0):
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)
        
        if left_to_left < 0 or left_to_right < 0 or right_to_left < 0 or right_to_right < 0:
            return await send_fancy_message(ctx, "Alle Werte müssen größer gleich 0 sein.", color=0xff0000, ephemeral=True)
        if left_to_left > 1 or left_to_right > 1 or right_to_left > 1 or right_to_right > 1:
            return await send_fancy_message(ctx, "Alle Werte müssen kleiner gleich 1 sein.", color=0xff0000, ephemeral=True)

        if left_to_left == 0 and left_to_right == 0 and right_to_left == 0 and right_to_right == 0:
            await player.remove_filter('channelmix')
            await send_fancy_message(ctx, '**Channel Mix Filter** ausgeschaltet')

        channelmix = lavalink.ChannelMix()
        channelmix.update(left_to_left=left_to_left, left_to_right=left_to_right, right_to_left=right_to_left, right_to_right=right_to_right)
        await player.set_filter(channelmix)

        await send_fancy_message(ctx, f"{ctx.user.mention} hat den Channel Mix Filter auf {left_to_left}, {left_to_right}, {right_to_left}, {right_to_right} gesetzt.")
    
    # Subcommand for setting a volume filter
    # Parameters:
    #   volume: float - Volume of the player, must be between 0 and 5
    @music_filter.subcommand(sub_cmd_description='Stelle die Lautstärke ein!')
    @ipy.slash_option(name='volume', description='Lautstärke des Players.', opt_type=ipy.OptionType.NUMBER, required=True)
    async def volume(self, ctx: ipy.SlashContext, volume: float = 1):

        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        if volume < 0 or volume > 5:
            return await send_fancy_message(ctx, "Lautstärke muss zwischen 0 und 5 sein. 1 = 100%", color=0xff0000, ephemeral=True)

        await player.set_volume(volume)

        await send_fancy_message(ctx, f"{ctx.user.mention} hat die Lautstärke auf {volume} gesetzt.")

    # Subcommand for clearing all filters
    @music_filter.subcommand(sub_cmd_description='Cleare alle Filter!')
    async def clear(self, ctx: ipy.SlashContext):
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        await player.clear_filters()

        await send_fancy_message(ctx, f"{ctx.user.mention} hat alle Filter gelöscht.")

    # Base command for controlling the queue
    @ipy.slash_command(description="Weitere Controls für die Warteschlange!")
    async def music_queue(self, ctx: ipy.SlashContext):
        pass
    
    # Subcommand for jumping to a song in the queue
    # Parameters:
    #   position: int - Position of the song to jump to
    @music_queue.subcommand(sub_cmd_description="Skippe zu einem Song!")
    @ipy.slash_option(name="position", description="Position des Songs zu dem du skippen willst.", opt_type=ipy.OptionType.INTEGER, required=True)
    async def jump(self, ctx: ipy.SlashContext, position: int):

        voice_state = ctx.author.voice
        if not voice_state or not voice_state.channel:
            return await send_fancy_message(ctx, "Du bist in keinem Voice-Channel.", color=0xff0000, ephemeral=True)

        player: Player = self.lavalink.get_player(ctx.guild_id)

        if player is None:
            return await send_fancy_message(ctx, "Keinen Player gefunden, mach was rein!", color=0xff0000, ephemeral=True)

        if len(player.queue) == 0:
            return await send_fancy_message(ctx, "Warteschlange ist leer!", color=0xff0000, ephemeral=True)

        if position > len(player.queue) or position < 0:
            return await send_fancy_message(ctx, "Ungültige Position!", color=0xff0000, ephemeral=True)

        song = player.queue[position]

        if player.loop != 2:
            del player.queue[:position]
        else:
            del player.queue[position]
            player.queue.insert(0, song)

        await player.skip()

        await send_fancy_message(ctx, f'{ctx.user.mention} hat zu **{song.title}** geskipped!')

    # Subcommand for removing a song from the queue
    # Parameters:
    #   position: int - Position of the song to remove
    @music_queue.subcommand(sub_cmd_description="Entferne einen Song von der Warteschlange.")
    @ipy.slash_option(name="position", description="Position des Liedes in der Warteschlange.", opt_type=ipy.OptionType.INTEGER, required=True)
    async def remove(self, ctx: ipy.SlashContext, position: int):

        voice_state = ctx.author.voice
        if not voice_state or not voice_state.channel:
            return await send_fancy_message(ctx, "Du bist in keinem Voice-Channel.", color=0xff0000,
                                       ephemeral=True)

        player: Player = self.lavalink.get_player(ctx.guild_id)

        if player is None:
            return await send_fancy_message(ctx, "Gerade keinen Player gefunden, mach was rein!", color=0xff0000,
                                       ephemeral=True)

        if len(player.queue) == 0:
            return await send_fancy_message(ctx, "Warteschlange ist leer!", color=0xff0000, ephemeral=True)

        if position > len(player.queue) or position < 0:
            return await send_fancy_message(ctx, "Ungültige Position!", color=0xff0000, ephemeral=True)

        song = player.queue[position]
        
        can_remove = self.can_modify(player, ctx.author, ctx.guild_id)
        
        if song.requester != ctx.author.id and not can_remove:
            return await send_fancy_message(ctx, "Du kannst diesen Song nicht entfernen!", color=0xff0000, ephemeral=True)

        del player.queue[position]

        await send_fancy_message(ctx, f'{ctx.user.mention} entfernte **{song.title}** von der Warteschlange.')
    
    # Remove a song from the autocomplete list
    @remove.autocomplete('position')
    async def autocomplete_remove(self, ctx: ipy.AutocompleteContext):

        input_text = ctx.input_text
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if player is None:
            return await ctx.send([])

        show_first_results = False

        if input_text == '':
            show_first_results = True

        queue = []

        for i, item in enumerate(player.queue):
            queue.append(f"{i + 1}. {item.title} | {item.author}")

        choices = []

        for i, item in enumerate(queue):
            if show_first_results:
                choices.append({"name": item, "value": i})
            else:
                if input_text.lower() in item.lower():
                    choices.append({"name": item, "value": i})

        if len(choices) > 24:
            choices = choices[:24]

        await ctx.send(choices)

    # Remove all songs before jump position from autocomplete list
    @jump.autocomplete('position')
    async def autocomplete_jump(self, ctx: ipy.AutocompleteContext):

        input_text = ctx.input_text
        player: Player = self.lavalink.get_player(ctx.guild_id)

        if player is None:
            return await ctx.send([])

        show_first_results = False

        if input_text == '':
            show_first_results = True

        queue = []

        for i, item in enumerate(player.queue):
            queue.append(f"{i + 1}. {item.title} | {item.author}")

        choices = []

        for i, item in enumerate(queue):
            if show_first_results:
                choices.append({"name": item, "value": i})
            else:
                if input_text.lower() in item.lower():
                    choices.append({"name": item, "value": i})

        if len(choices) > 24:
            choices = choices[:24]

        await ctx.send(choices)
    
    # Listener for when a track starts playing
    @ipy.listen()
    async def on_track_start(self, event: TrackStart):

        player: Player = event.player

        channel: ipy.GuildText = player.fetch('Channel')

        await self.on_player(event.player, channel)
    
    # Listener for when voice state updates
    @ipy.listen()
    async def voice_state_update(self, event: ipy.events.VoiceUserLeave):
        player: Player = self.lavalink.get_player(event.author.guild.id)

        if player is None:
            return

        if event.author.bot:
            return

        channel = event.channel

        if not channel.id == player.channel_id:
            return

        if len(channel.voice_members) <= 2:
            text_channel = player.fetch('Channel')

            await send_fancy_message(text_channel, f'Alle sind von {channel.mention} disconnected. Um Musik zu stoppen, nutze ``/music stop``.')
    
    # Predefined buttons for the music player
    @staticmethod
    def get_buttons():
        return [
            ipy.Button(
                style=ipy.ButtonStyle.BLUE,
                emoji=ipy.PartialEmoji(id=1019286929059086418),
                custom_id="queue",
                label="Queue"
            ),
            ipy.Button(
                style=ipy.ButtonStyle.BLUE,
                emoji=ipy.PartialEmoji(id=1019286927888883802),
                custom_id="playpause",
                label="Pause"
            ),
            ipy.Button(
                style=ipy.ButtonStyle.BLUE,
                emoji=ipy.PartialEmoji(id=1019286930296410133),
                custom_id="skip",
                label="Skip"
            ),
            ipy.Button(
                style=ipy.ButtonStyle.BLUE,
                emoji=ipy.PartialEmoji(id=1019286926404091914),
                custom_id="loop",
                label="Loop"
            ),
        ]

    # Predefined buttons for the queue
    @staticmethod
    async def get_queue_buttons():
        options = [
            ipy.Button(
                style=ipy.ButtonStyle.RED,
                emoji=ipy.PartialEmoji(id=1031309494946385920),
                custom_id="left"
            ),
            ipy.Button(
                style=ipy.ButtonStyle.BLUE,
                emoji=ipy.PartialEmoji(id=1031309497706225814),
                custom_id="shuffle",
                label="Shuffle"
            ),
            ipy.Button(
                style=ipy.ButtonStyle.GREY,
                emoji=ipy.PartialEmoji(id=1019286926404091914),
                custom_id="loopqueue",
                label="Loop"
            ),
            ipy.Button(
                style=ipy.ButtonStyle.RED,
                emoji=ipy.PartialEmoji(id=1031309496401793064),
                custom_id="right"
            )
        ]

        return options
    
    # Main player embed message
    async def on_player(self, player: Player, channel: ipy.GuildText):

        if player.loop == 1:
            return

        player_uid = str(uuid.uuid4())

        player.store('uid', player_uid)

        main_buttons = Music.get_buttons()
        
        player_state = 'Now Playing...'
        embed = await self.get_playing_embed(player_state, player, True)

        message = await channel.send(embed=embed, components=main_buttons)

        stopped_track = player.current

        while player.current is not None and player_uid == player.fetch('uid'):

                if player.loop == 1:
                    player_state = 'Jetzt in Loop...'
                    main_buttons[3].label = 'Stop Loop'
                    main_buttons[3].style = ipy.ButtonStyle.GREEN
                else:
                    main_buttons[3].label = 'Start Loop'
                    main_buttons[3].style = ipy.ButtonStyle.BLUE
                
                if player.paused:
                    player_state = 'Pausiert.'
                    main_buttons[1].label = 'Resume'
                    main_buttons[1].style = ipy.ButtonStyle.GREEN
                else:
                    player_state = 'Now Playing...'
                    main_buttons[1].label = 'Pause'
                    main_buttons[1].style = ipy.ButtonStyle.BLUE

                user = await self.bot.fetch_member(player.current.requester, player.guild_id)

                can_control: bool = False

                voice_state = user.voice
                if not voice_state or not voice_state.channel:
                    can_control = True

                embed = await self.get_playing_embed(player_state, player, can_control)

                message = await message.edit(embed=embed, components=main_buttons)

                await asyncio.sleep(1)

        embed = ipy.Embed(
            title=stopped_track.title,
            url=stopped_track.uri,
            description=f'Von **{stopped_track.author}**',
            color=0x696969
        )

        embed.set_author(name="Gestoppt...")
        embed.set_thumbnail(self.get_cover_image(stopped_track.identifier))

        requester = await self.bot.fetch_user(stopped_track.requester)

        embed.set_footer(text='Angefragt von: ' + requester.username, icon_url=requester.avatar_url)

        message = await message.edit(content='<:nikosleepy:1027492467337080872>', embed=embed, components=[])
    
    # Component Callback for the player buttons
    @ipy.component_callback('queue', 'loop', 'playpause', 'skip', 'lyrics')
    async def buttons(self, ctx: ipy.ComponentContext):

        player: Player = self.lavalink.get_player(ctx.guild_id)

        if player is None:
            return

        if ctx.custom_id == 'queue':

            player.store("current_page", 1)

            if len(player.queue) < 1:
                return await send_fancy_message(ctx, 'Keine Songs in der Warteschlange, nutze ``/music play`` um mehr hinzuzufügen!', ephemeral=True, color=0xff0000)

            embed = await self.get_queue_embed(player, 1)

            components = await Music.get_queue_buttons()
            return await ctx.send(embed=embed, components=components, ephemeral=True)

        if ctx.custom_id == 'lyrics':
            message = await send_fancy_message(ctx, f'Searching Lyrics for this track...', ephemeral=True)
            embed = await self.get_lyrics(player.current)
            return await ctx.edit(message, embed=embed)

        if not await self.can_modify(player, ctx.author, ctx.guild.id):
            await send_fancy_message(ctx, 'You cannot modify the player.', ephemeral=True, color=0xff0d13)
            return

        await ctx.defer(edit_origin=True)

        if ctx.custom_id == 'loop':
            if not player.loop:
                player.set_loop(1)
                msg = await send_fancy_message(ctx.channel, f'{ctx.author.mention} Start Loop.')
            else:
                player.set_loop(0)
                msg =await send_fancy_message(ctx.channel, f'{ctx.author.mention} Stop Loop.')

        if ctx.custom_id == 'playpause':
            await player.set_pause(not player.paused)

            if player.paused:
                msg = await send_fancy_message(ctx.channel, f'{ctx.author.mention} Paused.')
            else:
                msg = await send_fancy_message(ctx.channel, f'{ctx.author.mention} Resumed.')

        if ctx.custom_id == 'skip':
            await player.skip()

            await send_fancy_message(ctx.channel, f'{ctx.author.mention} Skipped.')
            
        if msg is not None:
            await msg.delete(delay=5)

    # Component Callback for the queue buttons
    @ipy.component_callback('shuffle', 'loopqueue', 'left', 'right')
    async def queue_buttons(self, ctx: ipy.ComponentContext):

        player: Player = self.lavalink.get_player(ctx.guild_id)

        page = player.fetch('current_page')

        if ctx.custom_id == 'left':
            if page == 1:
                page = 1
            else:
                page -= 1

        max_pages = (len(player.queue) + 9) // 10

        if ctx.custom_id == 'right':
            if page < max_pages:  # Only allow moving to the right if there are more pages to display
                page += 1

        player.store('current_page', page)

        message = None

        if ctx.custom_id == 'shuffle':
            random.shuffle(player.queue)
            message = await send_fancy_message(ctx.channel, f'{ctx.author.mention} hat die Wartschlange geshuffled.')

        if ctx.custom_id == 'loopqueue':
            if player.loop == 2:
                player.set_loop(0)
                message = await send_fancy_message(ctx.channel, f'{ctx.author.mention} hat Loop deaktiviert.')
            else:
                player.set_loop(2)
                message = await send_fancy_message(ctx.channel, f'{ctx.author.mention} hat Loop aktiviert.')

        embed = await self.get_queue_embed(player, page)

        components = await Music.get_queue_buttons()
        await ctx.edit_origin(embed=embed, components=components)
        if message is not None:
            await asyncio.sleep(5)
            await message.delete()
    
    # Subcommand for removing last song added by the user from the queue
    @music_filter.subcommand(sub_cmd_description='Entferne den letzten Song von dir.')
    async def remove_last(self, ctx: ipy.SlashContext):
        player = self.lavalink.get_player(ctx.guild_id)

        if not player:
            return await send_fancy_message(ctx, 'Da gab es wohl einen Fehler, probiere es später nochmal.', ephemeral=True, color=0xff0000)

        if len(player.queue) == 0:
            return await send_fancy_message(ctx, 'Kein Lied in der Wartschlange.', ephemeral=True, color=0xff0000)

        queue = player.queue[::-1]

        for track in queue:
            if track.requester == int(ctx.user.id):
                player.queue.remove(track)
                return await send_fancy_message(ctx, f'{ctx.user.mention} entfernte **{track.title}** von der Warteschlange.')

    # Create an embed for the main player embed
    async def get_playing_embed(self, player_status: str, player: Player, allowed_control: bool) -> ipy.Embed:
        track = player.current
        
        if not track:
            return
        
        bar_empty = '░'
        bar_filled = '█'

        progress_bar_length = 20
        progress = round(progress_bar_length * player.position / track.duration)

        progress_bar = f'{bar_filled * progress}{bar_empty * (progress_bar_length - progress)}'

        current = lavalink.format_time(player.position)
        total = lavalink.format_time(track.duration)

        description = f'**[{track.title}] ({track.uri})**\n{progress_bar} `{current}/{total}`'

        requester = await self.bot.fetch_user(track.requester)
        control_text = 'Alle habe Kontrolle' if allowed_control else 'Hat gerade die Kontrolle'

        embed = ipy.Embed(
            title=track.title,
            description=description,
            url=track.uri,
            color=0x00ffff,
            author=ipy.EmbedAuthor(name=player_status),
            thumbnail= self.get_cover_image(track.identifier),
            footer=ipy.EmbedFooter(text=f'Angefragt von: {requester.username} / {control_text}', icon_url=requester.avatar_url)
        )

        return embed
    
    # Create an embed for the queue
    async def get_queue_embed(self, player: Player, page: int) -> ipy.Embed:
        queue_list = ''

        queue = player.queue[(page * 10) - 10: (page * 10)]
        i = (page * 10) - 9

        for track in queue:
            title = track.title
            author = track.author
            requester = await self.bot.fetch_user(track.requester)

            queue_list = f'{queue_list}**{i}**. ***{title}*** by {author} - {requester.mention}\n'

            i += 1
        
        track = player.current
        guild = await self.bot.fetch_guild(player.guild_id)

        time = 0

        for t in player.queue:
            time += t.duration / 1000

        hours = int(time / 3600)
        minutes = int((time % 3600) / 60)

        description = f'### Playing:\n**{track.title}** von **{track.author}**\n\n*Aktuell sind* ***{len(player.queue)}*** *songs in der Warteschlange.*\n*Ungefähr* ***{hours} Stunden*** und ***{minutes} Minuten*** *übrig.*\n### Als nächstes kommt...\n{queue_list}'

        icon = None

        if guild.icon:
            icon = guild.icon.url

        queue_embed = ipy.Embed(
            description=description,
            color=0x00ffff,
            author=ipy.EmbedAuthor(name=f'Warteschlange für {guild.name}', icon_url=icon),
            thumbnail=self.get_cover_image(track.identifier),
            footer=ipy.EmbedFooter(text=f'Page {page} of {len(player.queue) // 10 + 1}')
            )
        
        return queue_embed
    
    # Check if a user can modify the player
    async def can_modify(self, player: Player, author: ipy.Member, guild_id: ipy.Snowflake):

        requester_member: ipy.Member = await self.bot.fetch_member(player.current.requester, guild_id)

        user_voice_state = author.voice
        requester_voice_state = requester_member.voice

        if ipy.Permissions.MANAGE_CHANNELS in author.guild_permissions:
            return True

        if not user_voice_state or not user_voice_state.channel:
            return False
        
        if not requester_voice_state or not requester_voice_state.channel:
            return True

        if int(author.id) == player.current.requester:
            return True

        return False
    
    # Create embed after edding song to queue
    def create_added_to_playlist_embed(self, ctx: ipy.SlashContext, player: Player, track: lavalink.AudioTrack):
        add_to_queue_embed = ipy.Embed(
            title=track.title,
            url=track.uri,
            description=f'Von **{track.author}**\n\nErfolgreich in die Warteschlange gesetzt.',
            color=0x2B2D31
        )

        add_to_queue_embed.set_author(name='Angefragt von ' + ctx.author.user.username,
                                      icon_url=ctx.author.user.avatar_url)

        add_to_queue_embed.set_thumbnail(self.get_cover_image(track.identifier))
        add_to_queue_embed.set_footer(text='War dies ein Fehler? Nutze /music remove_last um schnell zu entfernen.')

        return add_to_queue_embed

    def get_cover_image(self, identifier: str) -> str:
        return f'https://img.youtube.com/vi/{identifier}/0.jpg'

# Helper function for sending messages as embed
async def send_fancy_message(
        ctx: ipy.SlashContext,
        message: str,
        color: int = 0x00ffff,
        ephemeral: bool = False,
        components: list[ipy.BaseComponent] = []
        ):
    
    embed = ipy.Embed(
        description=message,
        color=color
    )
    
    return await ctx.send(embed=embed, ephemeral=ephemeral, components=components)