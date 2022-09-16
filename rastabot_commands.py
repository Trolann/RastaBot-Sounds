from time import sleep

from rastadb import config_db, wordfilter_db
from os import system as os_system
from features.welcome_messages import new_message
from features.bad_words import list_bad_words
from features.reactions import new_reaction_message, delete_reaction_message, new_role_reaction, delete_role_reaction, list_reactions
from features.tester import clear_testers
from features.sounds import check_dab_timer, start_dab_timer, clear_dab_timer


COMMAND_PREFIX = config_db.command_prefix


async def process_command(client, irie_guild, message, member, channel):
	print('Command issued by BotManager {}'.format(member))

	if message.content.startswith('{}new_welcome_message'.format(COMMAND_PREFIX)):
		split_message = message.content.split()
		updated_welcome_message = split_message[1:]
		updated_welcome_message = ' '.join(updated_welcome_message)
		reply = new_message(updated_welcome_message)
		print('Welcome message added by {}. {}'.format(member.name, reply))
		await channel.send(reply)
	# TODO: Change to embed
	if message.content.startswith('{}list_welcome_messages'.format(COMMAND_PREFIX)):
		messages = config_db.get_messages()
		i = 0
		for message in messages:
			i += 1
			await channel.send('{}: {}'.format(i, message))
	
	if message.content.startswith('{}add_bad_word'.format(COMMAND_PREFIX)):
		new_word = message.clean_content[14:]
		wordfilter_db.add('bad_word', new_word)
		await channel.send('Added {} to bad_word_list'.format(new_word))
	# TODO: Change to embed
	if message.content.startswith('{}list_bad_words'.format(COMMAND_PREFIX)):
		reply = list_bad_words()
		await channel.send(reply)
	if message.content.startswith('{}delete_bad_word'.format(COMMAND_PREFIX)):
		to_delete = message.clean_content[17:]
		wordfilter_db.remove('bad_word', to_delete)
		await channel.send('Deleted {} from the bad words list'.format(to_delete))
		# TODO: Change to embed
		bad_words_reply = list_bad_words()
		await channel.send(bad_words_reply)
	if message.content.startswith('{}add_banned_word'.format(COMMAND_PREFIX)):
		new_word = message.clean_content[20:]
		wordfilter_db.add('banned_words', new_word)
		await channel.send('Added {} to banned_words'.format(new_word))
	if message.content.startswith('{}list_banned_words'.format(COMMAND_PREFIX)):
		reply = wordfilter_db.banned_words
		await channel.send(reply)
	if message.content.startswith('{}delete_banned_word'.format(COMMAND_PREFIX)):
		to_delete = message.clean_content[23:]
		wordfilter_db.remove('banned_words', to_delete)
		await channel.send('Deleted {} from the banned words list'.format(to_delete))
		bad_words_reply = list_bad_words()
		await channel.send(bad_words_reply)
	
	if message.content.startswith('{}new_reaction_message'.format(COMMAND_PREFIX)):
		await new_reaction_message(message, channel)
		return
	if message.content.startswith('{}delete_reaction_message'.format(COMMAND_PREFIX)):
		await delete_reaction_message(message, channel)
		return	
	if message.content.startswith('{}new_role_reaction'.format(COMMAND_PREFIX)):
		await new_role_reaction(irie_guild, message, channel)
		return	
	if message.content.startswith('{}delete_role_reaction'.format(COMMAND_PREFIX)):
		await delete_role_reaction(irie_guild, message, channel)
		return
	if message.content.startswith('{}list_role_reaction'.format(COMMAND_PREFIX)):
		await list_reactions(irie_guild, message, channel)
		return
	
	if message.content.startswith('{}kill'.format(COMMAND_PREFIX)):
		while not config_db.system_killed:
			config_db.update_killed(member.name)
			sleep(1)
		os_system('kill 1')
		return
	
	if message.content.startswith('{}clear_testers'.format(COMMAND_PREFIX)):
		await clear_testers(channel)
	if message.content.startswith('{}tester_message'.format(COMMAND_PREFIX)):
		tester_message = message.content[16:]
		config_db.update_tester_message(tester_message)
		await channel.send('Tester message updated to: {}'.format(tester_message))

	if message.content.startswith('{}check_dab_timer'.format(COMMAND_PREFIX)):
		await check_dab_timer(channel)
	if message.content.startswith('{}start_dab_timer'.format(COMMAND_PREFIX)):
		await start_dab_timer(channel)
	if message.content.startswith('{}clear_dab_timer'.format(COMMAND_PREFIX)):
		await clear_dab_timer(channel)
