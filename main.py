"""
RastaBot developed by Trolan (Trevor Mathisen). 
"""
# Core requirements
from rastadb import config_db
import discord
from features import count
from os import environ as os_environ
from rastabot import process_incoming_message, start_daemons, check_bot_manager, heartbeat_daemon
from features.bad_words import check as check_bad_words
from features.welcome_messages import welcome_member
from rastabot_requests import process_request
from rastabot_commands import process_command
from features.podcast import auto_status as podcast_auto_status
from features.tester import process_incoming_message as tester_process_incoming_message
from features.reactions import add as add_reaction
from features.reactions import remove as remove_reaction
from features.iriedirect import iriedirect_check_for_drop
from features.utils import get_site
global irie_guild

# Configuration variables requested for the rest of the program
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)
start_daemons()

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
	print('We have logged in as {0.user}'.format(client))

# *****************************************************#
#               Member Join Processing:               #
#        Processes a new member to the server         #
#                      Process:                       #
#      - Counts every member                          #
#      - Checks if member was welcomed before         #
#      - Gets a welcome message based on season       #
#      - Adds welcomed member to welcomed list        #
#      - Sends the welcome message                    #
# *****************************************************#


@client.event
async def on_member_join(member):
	count.members()
	await welcome_member(irie_guild, member)

# *****************************************************#
#              Reaction Add Processing:               #
#            Reaction adds processed here             #
#                      Process:                       #
#     - Count every reaction                          #
#     - Loads reaction message from db                #
#     - Adds role based on reaction                   #
# *****************************************************#


@client.event
async def on_raw_reaction_add(payload):
	count.reactions() # Basic counter
	await add_reaction(irie_guild, payload)

# *****************************************************#
#            Reaction Removal Processing:             #
#          Reaction removals processed here           #
#                      Process:                       #
#     - Count every reaction                          #
#     - Loads guild object                            #
#     - Strips user_id from payload                   #
#     - Loads member from user_id and guild           #
#     - Loads reaction message from db                #
#     - Removes role based on reaction                #
# *****************************************************#


@client.event
async def on_raw_reaction_remove(payload):
	count.reactions() # Basic counter
	await remove_reaction(irie_guild, payload)

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
	count.message()  # Basic counter

	# Cancel own message
	if message.author == client.user:
		return

	# member and channel can change in DM's, this normalizes them
	member, channel = await process_incoming_message(irie_guild, message)
	message = await channel.fetch_message(int(message.id))

	# Simple test the bot is working
	if message.content.lower().startswith('ping?'):
		print('{}'.format(message.content))
		print('rbping?/pong! processed from {}, {}'.format(message.author, client.latency))
		await message.channel.send('pong!')
		heartbeat_daemon(1, False)
		return

	# Check messages and perform tasks
	await podcast_auto_status(client, irie_guild)
	await iriedirect_check_for_drop(irie_guild)
	await tester_process_incoming_message(irie_guild, message)

	#  You can't filter bad_words from commands and be able to add/remove bad_words with commands
	if not member:
		bot_manager = True
	else:
		bot_manager = check_bot_manager(member, irie_guild.get_role(int(config_db.bot_manager_id)))

	if message.content.startswith('{}'.format(COMMAND_PREFIX)) and bot_manager:
		pass
	else:
		await check_bad_words(irie_guild, channel, message, member)

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


			
try:
	# Start the bot
	client.run(os_environ['DISCORD_TOKEN'])
except:
	# Fails for discord banning this IP range, get a new container and IP block
	from os import system as os_system
	get_site(config_db.heartbeat_api)
