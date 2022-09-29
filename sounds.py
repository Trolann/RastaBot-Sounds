from time import sleep
from asyncio import sleep as asynciosleep
from datetime import datetime
from rastadb import config_db, sounds_db
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from rastabot import check_bot_manager


REQUEST_PREFIX = config_db.request_prefix
global path


def get_vc():
	voice = config_db.client.voice_clients
	if voice and voice[0].is_playing():
		return voice[0]
	else:
		return None


async def check_dab_timer(channel = None):
	print('checking dab timer')
	if not bool(sounds_db.check_dab_timer()):
		if channel:
			await channel.send('No active timer')
		return 0

	current_epoch = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
	timer_expire = sounds_db.check_dab_timer()

	seconds_left = timer_expire - int(round(float(current_epoch)))
	print(f'seconds left {seconds_left}')

	if seconds_left <= 0:
		seconds_left = 0
	if channel:
		minutes, seconds = divmod(seconds_left, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)
		time_left = f'{hours} hours, {minutes} minutes' if hours else f'{minutes} minutes, {seconds} seconds'
		await channel.send(f'{time_left} remaining')
	print(f'dab timer checked {seconds_left}')
	return int(seconds_left)


async def clear_dab_timer(channel = None):
	sounds_db.clear_dab_timer()
	if channel:	
		await channel.send(f'{sounds_db.check_dab_timer()} seconds remaining')


async def start_dab_timer(channel = None):
	current_epoch = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
	timer_expire = current_epoch + sounds_db.dab_cooldown_length * 60
	sounds_db.start_dab_timer(timer_expire)
	
	seconds_left = await check_dab_timer()
	if channel:
		minutes, seconds = divmod(seconds_left, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)
		time_left = f'{hours} hours, {minutes} minutes' if hours else f'{minutes} minutes, {seconds} seconds'
		await channel.send(f'{time_left} remaining')
	
	return True


async def dab_request(irie_guild, message, rj_command = False):

	bot_manager = check_bot_manager(message.author, irie_guild.get_role(int(config_db.bot_manager_id)))
	if rj_command and not bot_manager:
		return

	# confirm {}dab is available
	if message.channel.id != sounds_db.dab_text_channel_id:
		text_channel = irie_guild.get_channel(sounds_db.dab_text_channel_id)
		await message.channel.send(f'{REQUEST_PREFIX}dab only usable in {text_channel.mention}')
		return

	dab_timer_active = await check_dab_timer()

	if not rj_command and dab_timer_active:
		await message.channel.send(f'Can\'t right now {message.author.mention}, I\'m cleaning my rig')
		return

	voice_channel = irie_guild.get_channel(sounds_db.dab_voice_channel_id)

	# check if member is in the channel
	in_channel = False
	for member in voice_channel.members:
		print(member)
		if member is message.author:
			in_channel = True
	if not rj_command and not in_channel:
		await message.channel.send(f'You have to be in {voice_channel.mention} in order to spam it with {REQUEST_PREFIX}dab')
		return

	vc = get_vc()
	# we have a valid request	
	# if there's already a voice client connected, disconnect it
	if vc:
		print('trying to disconnect')
		await vc.disconnect()
		return
	else:
		print(f'{REQUEST_PREFIX}dab issued by {message.author}')
		if not rj_command:
			await message.channel.send(f'Not a bad idea {message.author.mention}. Give me like {sounds_db.dab_delay_seconds} seconds to get my dab rig.')
			sleep(sounds_db.dab_delay_seconds)
		else:
			sleep(2)
		vc = await voice_channel.connect()
		
	# connect to the channel
	print(f"Connecting to {voice_channel.name}...")
	await message.channel.send(f'Alright {message.author.mention} on my way.')
	time = 0
	while vc.average_latency == 'inf' and time < 10:
		time += 1
		sleep(1)

	print(f'Connected to {voice_channel.name} with latency of {vc.average_latency}')

	try:
		dab_file = sounds_db.get_dab_file(rj_command)
		vc.play(FFmpegPCMAudio(f'{sounds_db.media_path}{dab_file}'))
		print(f"Playing {dab_file} with latency of {vc.average_latency}")
		vc.source = PCMVolumeTransformer(vc.source, volume=0.35)
		while vc.is_playing():
			await asynciosleep(1)
			continue
		print(f'Done playing {dab_file} with latency of {vc.average_latency}')
		await vc.disconnect()
		if not rj_command:
			await start_dab_timer()
		return
	except Exception as e:
		print(e)
		await vc.disconnect()
		if not rj_command:
			await start_dab_timer()
		return
