"""
RastaBot developed by Trolan (Trevor Mathisen). 
"""
# Core requirements
from rastadb import config_db
import discord
from os import environ as os_environ
from rastabot import process_incoming_message, check_bot_manager
from rastabot_requests import process_request
from rastabot_commands import process_command
global irie_guild

# Configuration variables requested for the rest of the program
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)


# Guild as a global variable to reduce calling for it
REQUEST_PREFIX = config_db.request_prefix  # Prefix for users to interact with bot
COMMAND_PREFIX = config_db.command_prefix  # Prefix for managers to command the bot

# *****************************************************#
#                      On ready:                      #
#                    Basic actions                    #
#                      Process:                       #
#      - Prints to console when ready                 #
# *****************************************************#


@client.event
async def on_ready():  # When ready
	# Globally pull the guild to prevent future calls
	global irie_guild
	irie_guild = client.get_guild(int(os_environ['IRIE_GUILD_ID']))
	config_db.client = client
	print('RastaBot-Sounds has logged in as {0.user}'.format(client))



# *****************************************************#
#                 Message Processing:                 #
#     Channel and Private messages processed here     #
#                      Process:                       #
#     - Count every message                           #
#     - Don't process the bot's own message           #
#     - Tell DM senders DM's aren't supported         #
#     - Process ping/pong checks                      #
#     - Check if the user is a BotManager             #
#     - Run message through bad word detector         #
#                       (if not a bot manager         #
#     - Then the message is processed                 #
#           - Requests: Require @IrieArmy role        #
#           - Commands: Require @BotManager role      #
# *****************************************************#


@client.event
async def on_message(message):  # On every message

	# Cancel own message
	if message.author == client.user:
		return

	# member and channel can change in DM's, this normalizes them
	member, channel = await process_incoming_message(irie_guild, message)
	message = await channel.fetch_message(int(message.id))

	# Simple test the bot is working
	if message.content.lower().startswith('sounds?'):
		print('{}'.format(message.content))
		print('rbping?/pong! processed from {}, {}'.format(message.author, client.latency))
		await message.channel.send('pong!')
		return

	#  You can't filter bad_words from commands and be able to add/remove bad_words with commands
	if not member:
		bot_manager = True
	else:
		bot_manager = check_bot_manager(member, irie_guild.get_role(int(config_db.bot_manager_id)))

	# Only processing of requests and commands beyond here
	try:
		if message.content[0] not in (REQUEST_PREFIX, COMMAND_PREFIX):
			return
	except:
		f = open('error.txt', 'a')
		f.write(str(message) + '\n')
		f.close()
		pass

	# Route Requests
	if message.content.startswith(REQUEST_PREFIX):
		await process_request(irie_guild, message, member, channel)
		return

	# Route commands
	if message.content.startswith(COMMAND_PREFIX): # All commands for the bot
		# Stop non-managers
		if not bot_manager:
			print('{} command attempted by {}'.format(COMMAND_PREFIX, member))
			return
		try:
			await process_command(client, irie_guild, message, member, channel)
		except AttributeError:
			print('AttributeError | {}'.format(await channel.fetch_message(message.id)))
		return


# Start the bot
client.run(os_environ['DISCORD_TOKEN'])
