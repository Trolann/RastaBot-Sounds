from rastadb import config_db


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
