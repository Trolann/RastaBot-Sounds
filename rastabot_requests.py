from rastadb import config_db
from rastabot import get_about as rastabot_get_about
from features.tester import tester_request
from features.utils import seed_vendor_request, strain_request
from features.iriedirect import irie_direct_request
from features.sounds import dab_request


REQUEST_PREFIX = config_db.request_prefix


async def process_request(irie_guild, message, member, channel):
	if message.content.startswith('{}seeds'.format(REQUEST_PREFIX)):
		await seed_vendor_request(message, channel)
		return

	if message.content.startswith('{}strain'.format(REQUEST_PREFIX)):
		await strain_request(message, channel)
		return

	if message.content.startswith('{}irie'.format(REQUEST_PREFIX)):
		await irie_direct_request(irie_guild, message, channel)
		return
	print('processing a request')
	if message.content.startswith('{}about'.format(REQUEST_PREFIX)):
		await rastabot_get_about(member, channel)
		return

	if message.content.startswith('{}tester'.format(REQUEST_PREFIX)):
		await tester_request(irie_guild, message, channel)
		return

	if message.content.startswith('{}dab'.format(REQUEST_PREFIX)):
		await dab_request(irie_guild, message)
		return
