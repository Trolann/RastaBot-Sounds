import sqlite3
from time import sleep
from os import environ
from random import uniform
from pathlib import Path

from os import listdir
from os.path import isfile, join

global dev_instance
global path
global media_path

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
    print('RastaBot-Sounds DB path: {}'.format(path))
except KeyError:
    path = ''
    print('RastaBot-Sounds DB path: local'.format(path))

try:
    media_path = f"{environ['DIR_PATH']}media/"
    print(f'RastaBot-Sounds media path: {media_path}')
except KeyError:
    media_path = 'media/'
    print(f'Rastabot-Sounds media path: local')

shared_rasta_db = Path(f"{environ['DB_DIR']}rastabot.db")


if not shared_rasta_db.is_file():
    print('UNABLE TO FIND RASTA DB')


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


class ConfigDB:
    def __init__(self):
        global path
        self.environ_path = path
        self._rastadb = path + 'rastabot.db'
        self.table = 'config'
        self.client = ''

        self.request_prefix = get_value(self._rastadb, self.table, 'request_prefix')
        self.command_prefix = get_value(self._rastadb, self.table, 'command_prefix')
        self.bot_manager_id = int(get_value(self._rastadb, self.table, 'bot_manager_id', get_dev = True))
        self.bot_channel_id = int(get_value(self._rastadb, self.table, 'bot_channel_id', get_dev = True))



class SoundsDB:
    def __init__(self):
        global path
        self._rastadb = path + 'rastabot.db'
        self.media_path = media_path
        self.table = 'sounds'
        self.dab_cooldown_length = int(get_value(self._rastadb, self.table, 'dab_cooldown_length'))
        self.dab_text_channel_id = int(get_value(self._rastadb, self.table, 'dab_text_channel_id', get_dev = True))
        self.dab_voice_channel_id = int(get_value(self._rastadb, self.table, 'dab_voice_channel_id', get_dev = True))
        self.dab_delay_seconds = int(get_value(self._rastadb, self.table, 'dab_delay_seconds', get_dev = True))
        self.dab_files = self.get_dab_files()
        self.dab_files_index = -1

    def get_dab_file(self, rj_command = False):
        self.dab_files_index = 0 if self.dab_files_index >= len(self.dab_files) else self.dab_files_index + 1
        return self.dab_files[self.dab_files_index] if not rj_command else self.dab_files[self.dab_files.index('joeydiaz.mp3')]

    def get_dab_files(self):
        dab_files = [f for f in listdir(self.media_path) if isfile(join(self.media_path, f))]
        dab_files.remove('.gitignore')
        print(dab_files)
        return dab_files

    def check_dab_timer(self):
        return int(round(float(get_value(self._rastadb, self.table, 'dab_timer_expires', get_dev = True))))

    def start_dab_timer(self, time):
        insert(self._rastadb, self.table, 'dab_timer_expires', time, get_dev = True)

    def clear_dab_timer(self):
        insert(self._rastadb, self.table, 'dab_timer_expires', 0, get_dev = True)


config_db = ConfigDB()
sounds_db = SoundsDB()
