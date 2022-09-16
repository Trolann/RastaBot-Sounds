from time import sleep
from asyncio import sleep as asynciosleep
from datetime import datetime, timedelta
from rastadb import config_db, sounds_db
from discord import FFmpegPCMAudio, PCMVolumeTransformer


REQUEST_PREFIX = config_db.request_prefix
global vc
global path


async def check_dab_timer(channel = None):

	if not bool(sounds_db.check_dab_timer()):
		if channel:
			await channel.send('No active timer')
		return 0

	current_epoch = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
	timer_expire = sounds_db.check_dab_timer()

	seconds_left = timer_expire - int(round(float(current_epoch)))

	if seconds_left <= 0:
		seconds_left = 0
	if channel:
		minutes, seconds = divmod(seconds_left, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)
		time_left = '{} hours, {} minutes'.format(hours, minutes) if hours else '{} minutes, {} seconds'.format(minutes, seconds)
		await channel.send('{} remaining'.format(time_left))
	
	return int(seconds_left)


async def clear_dab_timer(channel = None):
	sounds_db.clear_dab_timer()
	if channel:	
		await channel.send('{} seconds remaining'.format(sounds_db.check_dab_timer()))


async def start_dab_timer(channel = None):
	current_epoch = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
	timer_expire = current_epoch + sounds_db.dab_cooldown_length * 60
	sounds_db.start_dab_timer(timer_expire)
	
	seconds_left = await check_dab_timer()
	if channel:
		minutes, seconds = divmod(seconds_left, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)
		time_left = '{} hours, {} minutes'.format(hours, minutes) if hours else '{} minutes, {} seconds'.format(minutes, seconds)
		await channel.send('{} remaining'.format(time_left))
	
	return True


async def dab_request(irie_guild, message):
	global vc
	# confirm {}dab is available
	if message.channel.id != sounds_db.dab_text_channel_id:
		text_channel = irie_guild.get_channel(sounds_db.dab_text_channel_id)
		await message.channel.send('{}dab only usable in {}'.format(REQUEST_PREFIX, text_channel.mention))
		return

	dab_timer_active = await check_dab_timer()
	if dab_timer_active:
		await message.channel.send('Can\'t right now {}, I\'m cleaning my rig'.format(message.author.mention))
		return

	voice_channel = irie_guild.get_channel(sounds_db.dab_voice_channel_id)

	# check if member is in the channel
	in_channel = False
	for member in voice_channel.members:
		if member is message.author:
			in_channel = True
	if not in_channel:
		await message.channel.send('You have to be in {} in order to spam it with {}dab'.format(voice_channel.mention, REQUEST_PREFIX))
		return

	# we have a valid request	
	# if there's already a voice client connected, disconnect it
	try:
		await vc.disconnect()
		return
	except:
		print('{}dab issued by {}'.format(REQUEST_PREFIX, message.author))
		await message.channel.send('Not a bad idea {}. Give me like {} seconds to get my dab rig.'.format(message.author.mention, sounds_db.dab_delay_seconds))
		sleep(sounds_db.dab_delay_seconds)
		vc = await voice_channel.connect()
		
	# connect to the channel
	print('Connecting to {}...'.format(voice_channel.name))
	await message.channel.send('Alright {} on my way.'.format(message.author.mention))
	time = 0
	while vc.average_latency == 'inf' and time < 10:
		time += 1
		sleep(1)

	print('Connected to {} with latency of {}'.format(voice_channel.name, vc.average_latency))

	try:
		vc.play(FFmpegPCMAudio('{}dabtime.mp3'.format(sounds_db.media_path)))
		print('Playing dabtime.mp3 with latency of {}'.format(vc.average_latency))
		vc.source = PCMVolumeTransformer(vc.source, volume=0.35)
		while vc.is_playing():
			await asynciosleep(1)
			continue
		print('Done playing dabtime.mp3 with latency of {}'.format(vc.average_latency))
		await vc.disconnect()
		await start_dab_timer()
		return
	except Exception as e:
		print(e)
		await vc.disconnect()
		await start_dab_timer()
		return
