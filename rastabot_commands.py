from rastadb import config_db
from sounds import check_dab_timer, start_dab_timer, clear_dab_timer


COMMAND_PREFIX = config_db.command_prefix


async def process_command(client, irie_guild, message, member, channel):
	print('Command issued by BotManager {}'.format(member))

	if message.content.startswith('{}check_dab_timer'.format(COMMAND_PREFIX)):
		await check_dab_timer(channel)
	if message.content.startswith('{}start_dab_timer'.format(COMMAND_PREFIX)):
		await start_dab_timer(channel)
	if message.content.startswith('{}clear_dab_timer'.format(COMMAND_PREFIX)):
		await clear_dab_timer(channel)
