from rastadb import config_db
import os
from time import sleep

# DealCatcher/Irie Genetics daemons
from threading import Thread
from features.utils import get_site as get_site
from features.iriedirect import iriedirect_drop_daemon

REQUEST_PREFIX = config_db.request_prefix  # Prefix for users to interact with bot
COMMAND_PREFIX = config_db.command_prefix  # Prefix for managers to command the bot


def heartbeat_daemon(delay, loop):
    # TODO: Add environment variable to RastaBot (Replit)
    get_site(config_db.heartbeat_url)
    while loop:
        get_site(config_db.heartbeat_url)
        sleep(delay)


# *****************************************************#
#  Function Group: Database Update Functions          #
#  Description: Functions to manually add keys and    #
#               values to the database. Used for      #
#               intiial setup on a new sever          #
#       Contains: command_db_update(key, value)       #
#                 command_db_delete(key)              #
# *****************************************************#


async def get_about(member, channel):
    """Return about information"""
    print('{}about request received from {}'.format(REQUEST_PREFIX, member))
    about_msg = [config_db.about,
                 'RastaBot has processed {} users, {} messages, {} reactions and helped {} + {} people find beans.'.format(
                     config_db.get_count('members'), config_db.get_count('messages'), config_db.get_count('reactions'),
                     config_db.get_count('iriedirect'), config_db.get_count('seeds')),
                 'Use {}help to see all commands available for RastaBot'.format(REQUEST_PREFIX)]

    for i in range(len(about_msg)):
        if about_msg[i] is not None:
            await channel.send(about_msg[i])
    return


def start_daemons():
    heartbeat = Thread(target=heartbeat_daemon, args=(10, True,), daemon=True)
    heartbeat.start()
    iriedirect = Thread(target=iriedirect_drop_daemon, daemon=True)
    iriedirect.start()

def check_bot_manager(member, bot_manager_role):
    bot_manager = False
    for role in member.roles:
        if role == bot_manager_role:
            bot_manager = True
    return bot_manager


async def process_incoming_message(irie_guild, message):
    # Pull member for private messages, send things back to the member privately
    if str(message.channel.type) == 'private':
        member = irie_guild.get_member(message.author.id)
        channel = member

        # Alert everyone someone has DM'd the bot
        bot_channel = irie_guild.get_channel(config_db.bot_channel_id)
        await bot_channel.send('DM from: {}'.format(member))
        await bot_channel.send('Message: {}'.format(message.content))
        return member, channel

    # Catchall for User type bots (RastaBot) defaults to Bot ID
    if 'bot' in str(message.author).lower():
        member = irie_guild.get_member_named('JustCheckingThisOut')
        channel = message.channel
        return member, channel

    # Base case, assign from the given message
    member = message.author
    channel = message.channel
    return member, channel
