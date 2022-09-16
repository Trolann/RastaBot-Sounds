from rastadb import config_db

from sounds import dab_request


REQUEST_PREFIX = config_db.request_prefix


async def process_request(irie_guild, message, member, channel):
	if message.content.startswith('{}dab'.format(REQUEST_PREFIX)):
		await dab_request(irie_guild, message)
		return
