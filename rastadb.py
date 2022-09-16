import sqlite3
from time import sleep
from os import environ
from random import uniform
from pathlib import Path
from shutil import copy2 as copyfile

global dev_instance
global path

try:
    dev_instance = bool(int(environ['DEV_INSTANCE']))
    if dev_instance:
        print('-' * 35)
        print('DEVELOPMENT INSTANCE   ' * 3)
        print('-' * 35)
    else:
        print('-' * 35)
        print('**PROD' * 10 + '**')
        print('**PROD' * 10 + '**')
        print('**PROD' * 10 + '**')
        print('-' * 35)
except KeyError:
    print('-' * 35)
    print('DEVELOPMENT INSTANCE   ' * 3)
    print('-' * 35)
    dev_instance = True

try:
    path = environ['DB_DIR']
    print('RastaBot DB path: {}'.format(path))
except KeyError:
    path = ''
    print('RastaBot DB path: local'.format(path))

shared_rasta_db = Path(f"{environ['DB_DIR']}rastabot.db")
copyfile(f"{environ['DIR_PATH']}media/dabtime.mp3", environ['DB_DIR'])

if not shared_rasta_db.is_file():
    try:

        copyfile(f"{environ['DIR_PATH']}rastabot.db", environ['DB_DIR'])
        print('copied file')
    except:
        print('Using local rastabot.db')

def _db_recur(cursor, sql, called_from, recur_depth = 0):
    try:
        cursor.execute(sql)
    except sqlite3.OperationalError as e:
        if recur_depth <= 5:
            sleep(uniform(0.5, 4.5))
            recur_depth += 1
            print('Recur DB called for {}. Depth: {}'.format(called_from, recur_depth))
            _db_recur(cursor, sql, called_from, recur_depth = recur_depth)
        else:
            print('recur failed. SQL NOT EXECUTED:')
            print(f'{sql}')
            print(f'called from: {called_from}')
            print(e)


def remove(db, table, option, get_dev = False, commit_to_db=True):
    global dev_instance
    if dev_instance and get_dev:
        option = 'dev_' + option
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    if dev_instance and get_dev:
        sql = "DELETE FROM {} WHERE option = '{}'".format(table, option)
    else:
        sql = "DELETE FROM {} WHERE option = '{}' AND option NOT LIKE \'dev_%\'".format(table, option)
    _db_recur(cursor, sql, 'remove')
    if commit_to_db:
        connection.commit()
    cursor.close()


def remove_like_value(db, table, option_like, value_like, get_dev = False,  commit_to_db=True):
    global dev_instance
    if dev_instance and get_dev:
        option_like = 'dev_' + option_like
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    if dev_instance and get_dev:
        sql = "DELETE FROM {} WHERE option = '{}' AND value LIKE '%{}%'".format(table, option_like, value_like)
    else:
        sql = "DELETE FROM {} WHERE option = '{}' AND option NOT LIKE \'dev_%\' AND value LIKE '%{}%'".format(table, option_like, value_like)
    _db_recur(cursor, sql, 'remove_like')
    if commit_to_db:
        connection.commit()
    cursor.close()


def insert(db, table, option, value, get_dev = False, commit_to_db = True):
    '''Inserts into sqlite db with the option:value schema
        Recursively calls _insert wrapper to avoid collisions/locked db'''
    global dev_instance

    if dev_instance and get_dev:
        option = 'dev_' + option

    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    to_insert = (option, value)  # Tuple insertion avoids injections
    sql = 'INSERT OR REPLACE INTO {} VALUES {}'.format(table, to_insert)
    _db_recur(cursor, sql, 'insert')  # Wrapper for recursion

    if commit_to_db:
        connection.commit()

    # if dev_instance:
    #     print('Value inserted into {} option {}: {}'.format(table, option, value))
    cursor.close()
    connection.close()


def get_value(db, table, option, get_dev = False):
    global dev_instance

    if dev_instance and get_dev:
        option = 'dev_' + option

    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    if dev_instance and get_dev:
        sql = 'SELECT value FROM {} WHERE option LIKE \'%{}%\''.format(table, option)
    else:
        sql = 'SELECT value FROM {} WHERE option LIKE \'%{}%\' AND option NOT LIKE \'%dev_%\''.format(table, option)
    _db_recur(cursor, sql, 'get_value')
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return_val = rows[0][0] if rows else 0
    if dev_instance:
        print('Get value result for {}: {}'.format(option, return_val))
    return return_val


def select_from_table(db, table, option, get_dev = False):
    global dev_instance

    if dev_instance and get_dev:
        option = 'dev_' + option

    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    if dev_instance and get_dev:
        sql = 'SELECT value FROM {} WHERE option LIKE \'%{}%\''.format(table, option)
    else:
        sql = 'SELECT value FROM {} WHERE option LIKE \'%{}%\' AND option NOT LIKE \'dev_%\''.format(table, option)
    _db_recur(cursor, sql, 'select_from_table')
    rows = cursor.fetchall()
    values = []
    for _value in rows:
        values.append(_value[0])
    cursor.close()
    connection.close()
    if dev_instance and 'After' in values:
        print('Get table length of {}: {}'.format(option, values))
    return values


class ConfigDB:
    def __init__(self):
        global path
        self.environ_path = path
        self._rastadb = path + 'rastabot.db'
        self.table = 'config'
        self.tester_table = 'testers'
        self.welcome_table = 'welcome_messages'
        self.request_prefix = get_value(self._rastadb, self.table, 'request_prefix')
        self.command_prefix = get_value(self._rastadb, self.table, 'command_prefix')
        self.bot_manager_id = int(get_value(self._rastadb, self.table, 'bot_manager_id', get_dev = True))
        self.heartbeat_url = self.get_heartbeat('url')
        self.heartbeat_api = self.get_heartbeat('api')

        self.system_killed_by = get_value(self._rastadb, self.table, 'system_killed_by')
        self.system_killed = False if self.system_killed_by == 'None' or '' else True

        self.bot_channel_id = int(get_value(self._rastadb, self.table, 'bot_channel_id', get_dev = True))
        self.tester_channel_id = int(get_value(self._rastadb, self.table, 'tester_channel_id', get_dev = True))
        self.irie_direct_channel_id = int(get_value(self._rastadb, self.table, 'irie_direct_channel_id', get_dev=True))

        self.about = get_value(self._rastadb, self.table, 'about', get_dev = True)


    def get_messages(self):
        return select_from_table(self._rastadb, self.welcome_table, 'welcome_message', get_dev=True)

    def new_message(self, new_message):
        item = 'welcome_message'
        insert(self._rastadb, self.welcome_table, item, new_message, get_dev=True)

    def get_heartbeat(self, value):
        value = 'heartbeat_' + value
        return get_value(self._rastadb, self.table, value, get_dev = True)

    def update_killed(self, by = ''):
        item = 'system_killed_by'
        option = by
        insert(self._rastadb, self.table, item, option)

    def get_tester_message(self):
        return get_value(self._rastadb, self.tester_table, 'tester_message', get_dev = True)

    def get_tester_members(self):
        rows = select_from_table(self._rastadb, self.tester_table, 'member_id')
        return_list = list()
        for value in rows:
            return_list.append(int(value))
        return return_list

    def update_count(self, counter, value):
        item = counter + '_count'
        insert(self._rastadb, self.table, item, value, get_dev = True)

    def add_tester(self, tester_id):
        item = 'member_id'
        insert(self._rastadb, self.tester_table, item, tester_id, get_dev = True)

    def clear_tester(self):
        option = 'dev_member_id' if dev_instance else 'member_id'
        conn = sqlite3.connect(self._rastadb)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM {} WHERE option = '{}'".format(self.tester_table, option))
        conn.commit()
        cursor.close()
        conn.close()
        self.add_tester('1234')
        self.add_tester('4556')

    def update_tester_message(self, tester_message):
        item = 'tester_message'
        remove(self._rastadb, self.tester_table, item, get_dev = True)
        insert(self._rastadb, self.tester_table, item, tester_message, get_dev = True)

    def get_count(self, counter):
        item = counter + '_count'
        return int(get_value(self._rastadb, self.table, item, get_dev = True))

class PodcastDB:
    def __init__(self):
        global path
        self._rastadb = path + 'rastabot.db'
        self.table = 'podcast'
        self.podcast_channel_id = int(get_value(self._rastadb, self.table, 'irie_podcast_channel_id', get_dev = True))

    def get_auto_status(self):
        return bool(get_value(self._rastadb, self.table, 'auto_status'))

    def get_current(self, value):
        item = 'current_' + value
        row = get_value(self._rastadb, self.table, item, get_dev = True)
        return row if 'num' not in value else int(row)

    def new_podcast(self, num, title, url):
        n = ('current_number', num)
        t = ('current_title', title)
        u = ('current_url', url)
        for item, option in (n, t, u):
            insert(self._rastadb, self.table, item, option, get_dev = True)


class WordFilterDB:
    def __init__(self):
        global path
        self._rastadb = path + 'rastabot.db'
        self.table = 'word_filter'

    def get_list(self, which_list):
        item = which_list + '_word'
        return select_from_table(self._rastadb, self.table, item)

    def add(self, which_list, bad_word):
        insert(self._rastadb, self.table, which_list + '_word', bad_word)

    def remove(self, which_list, bad_word):
        remove(self._rastadb, self.table, which_list + '_word', bad_word)


class ReactionsDB:
    def __init__(self):
        global path
        self._rastadb = path + 'rastabot.db'
        self.table = 'reactions'
        self.separator = '||'

    def get_reactions(self, msg_id = None):
        if msg_id is None:
            return list(select_from_table(self._rastadb, self.table, 'reaction_message'))
        rows = select_from_table(self._rastadb, self.table, msg_id)

        if len(rows[0]) > 1:
            reaction_tups = list()
            reaction_messages = list(rows)
            for option in reaction_messages:
                option_split = option.split(self.separator)
                tup = (option_split[0], option_split[1])
                reaction_tups.append(tup)
        else:
            emoji, role_id = rows.split(self.separator)
            reaction_tups = (emoji, role_id)

        return reaction_tups

    # TODO: Implement custom emoji support
    def add_message(self, message_id):
        item = 'reaction_message'
        insert(self._rastadb, self.table, item, message_id)

    def remove_message(self, message_id):
        remove(self._rastadb, self.table, message_id)
        remove_like_value(self._rastadb, self.table, 'reaction_message', message_id)

    def add_reaction(self, message_id, emoji, role_id):
        item = message_id
        option = emoji + self.separator + role_id
        insert(self._rastadb, self.table, item, option)
        option = '1||1'  # Dummy record to ensure list parses correctly. Unique values will be overriden and not stack
        insert(self._rastadb, self.table, item, option)

    def remove_reaction(self, message_id, emoji):
        remove_like_value(self._rastadb, self.table, message_id, emoji)


class SoundsDB:
    def __init__(self):
        global path
        self._rastadb = path + 'rastabot.db'
        self.table = 'sounds'
        self.dab_cooldown_length = int(get_value(self._rastadb, self.table, 'dab_cooldown_length'))
        self.dab_text_channel_id = int(get_value(self._rastadb, self.table, 'dab_text_channel_id', get_dev = True))
        self.dab_voice_channel_id = int(get_value(self._rastadb, self.table, 'dab_voice_channel_id', get_dev = True))
        self.dab_delay_seconds = int(get_value(self._rastadb, self.table, 'dab_delay_seconds', get_dev = True))

    def check_dab_timer(self):
        return int(round(float(get_value(self._rastadb, self.table, 'dab_timer_expires', get_dev = True))))

    def start_dab_timer(self, time):
        insert(self._rastadb, self.table, 'dab_timer_expires', time, get_dev = True)

    def clear_dab_timer(self):
        insert(self._rastadb, self.table, 'dab_timer_expires', 0, get_dev = True)


config_db = ConfigDB()
wordfilter_db = WordFilterDB()
podcast_db = PodcastDB()
reactions_db = ReactionsDB()
sounds_db = SoundsDB()
