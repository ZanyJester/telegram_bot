import datetime
import requests
import logging
import time
import yaml
from yaml.loader import SafeLoader
from mysql.connector import connect, Error

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s', filename='log.txt')

# create string connection db


def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print("The error create_connection {0} occurred").format(e)
    return connection

# insert,update,delete quary


def execute_query(connection, query, val):
    cursor = connection.cursor()
    try:
        cursor.execute(query, val)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print("The error execute_query {0} occurred").format(e)

# select query


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print("The error read_query {0} occurred").format(e)


def loggining():
    user_id = upd[-1]['message']['chat']['id']
    text = upd[-1]['message']['text']
    messageTime = upd[-1]['message']['date']
    messageTime = datetime.datetime.utcfromtimestamp(messageTime)
    messageTime = messageTime.strftime('%Y-%m-%d %H:%M:%S')
    loguserid = str(user_id)
    logtext = str(text)
    logdate = str(messageTime)
    log = loguserid + ' ' + logtext + ' ' + logdate
    logging.info(log)

# parse command


def telegram_bot(chat_id, text):
    parse_text = text.replace(',', "")
    command = parse_text.split()[0]
    user_id = upd[-1]['message']['chat']['id']
    if command == '/start':
        row= execute_read_query(connection, "select vcode from telegram_bot_db.user where ex".format(user_id))
        execute_query(connection, """insert into telegram_bot_db.users (user_id,date_appeal) VALUES (%s, %s)""",
                      (user_id, datetime.datetime.now(),))
        send_msg(chat_id, 'Hi write /help')
    elif command == '/write':
        content = parse_text.partition(command)[2]
        message_id = upd[-1]['message']['message_id']
        messageTime = upd[-1]['message']['date']
        messageTime = datetime.datetime.utcfromtimestamp(messageTime)
        messageTime = messageTime.strftime('%Y-%m-%d %H:%M:%S')
        TimeStamp = str(messageTime)
        if content:
            execute_query(connection, "insert into telegram_bot_db.messages (user_id, message_id, text_msg, date_send) values ( %s , %s, %s, %s)", (
                user_id, message_id, content, TimeStamp,))
            row = execute_read_query(
                connection, "select vcode from telegram_bot_db.messages where user_id = {0} order by vcode desc limit 1".format(user_id))
            rows = row[0][0]
            send_msg(chat_id, u'note {0} saved'.format(rows))
        else:
            send_msg(chat_id, u'note is blank!')
    elif command == '/read_last':
        row = execute_read_query(
            connection, "select text_msg from telegram_bot_db.messages where user_id = {0} order by vcode desc limit 1".format(user_id))
        rows = row[0][0]
        send_msg(chat_id, '{0}'.format(rows))
    elif command == '/read_all':
        rows = execute_read_query(
            connection, "select text_msg from telegram_bot_db.messages where user_id = {0} order by vcode".format(user_id))
        for row in rows:
            rows = row[0]
            send_msg(chat_id, '{0}'.format(rows))
    elif command == '/read':
        content = parse_text.partition(command)[2]
        row = execute_read_query(
            connection, "select text_msg from telegram_bot_db.messages where user_id = {0} and vcode = {1} order by vcode".format(user_id, content))
        if row or '':
            send_msg(chat_id, '{0}'.format(row[0][0]))
        else:
            send_msg(chat_id, 'You didnt enter a note <id> ')
    elif command == '/tag_all':
        rows = execute_read_query(
            connection, "select discription from telegram_bot_db.tags order by vcode")
        for row in rows:
            rows = row[0]
            send_msg(chat_id, '{0}'.format(rows))
    elif command == '/write_tag':
        tag_discr = parse_text.partition(command)[2]
        split_tag_dicrs = tag_discr.split()
        tag = split_tag_dicrs[0]
        discr = parse_text.partition(tag)[2]
        row = execute_read_query(
            connection, "select name_tag from telegram_bot_db.tags where name_tag like '%{0}' order by vcode".format(tag))
        if row:
            send_msg(chat_id, 'Tag updated')
            execute_query(
                connection, "update telegram_bot_db.tags set name_tag =  %s, discription = %s where name_tag like '%{0}%'".format(tag), (tag, discr))
        else:
            execute_query(
                connection, "insert into telegram_bot_db.tags (name_tag, discription) values ( %s, %s)", (tag, discr))
            send_msg(chat_id, 'Tag saved')
    elif command == '/read_tag':
        content = parse_text.partition(command)[2]
        row = execute_read_query(
            connection, "select text_msg from telegram_bot_db.messages where user_id = {0} and text_msg like '%{1}%'".format(user_id, content))
        if row or '':
            send_msg(chat_id, '{0}'.format(row[0][0]))
        else:
            send_msg(chat_id, 'You didnt enter a note <tag> ')
    elif command == '/tag':
        content = parse_text.partition(command)[2]
        tags = content.split()
        for tag in tags:
            rows = execute_read_query(
                connection, "select discription from telegram_bot_db.tags where name_tag like '%{0}%' order by vcode".format(tag))
            for row in rows:
                rows = row[0]
                send_msg(chat_id, '{0}'.format(rows))
    elif command == '/help':
        text = """
The /write command writes a message\n
The /read_last command displays the last message for the given user.\n
The /read <id> command displays the message field with the specified id.\n
The /read_all command lists all the notes of the current bot user in order from oldest to newest.\n
The /read_tag tag command displays all the user's notes by the specified tag in the message.\n
The /write_tag <tag> <tag description> command creates a tag. If the tag already exists, then changes its description.\n
The /tag <tag_1>,<tag_2>...<tag_n> command displays the description of the entered tags.\n
The /tag_all command displays a description of all tags.\n
                """
        send_msg(chat_id, text)
    elif command:
        send_msg(chat_id, 'write /help')
    return text

# get new messages


def get_upd(offset=0):
    result = requests.get(
        url='https://api.telegram.org/bot{0}/{1}'.format(
            token, "getUpdates"),
        params={
            "offset": offset,
        }, timeout=60).json()
    return result['result']


# anwser user


def send_msg(chat_id, text):
    requests.get(
        url='https://api.telegram.org/bot{0}/{1}'.format(
            token, "sendMessage"),
        params={
            "chat_id": chat_id,
            "text": text,
        }, timeout=60)

# check new messages in chat


            


def run():
    update_id = upd[-1]['update_id']
    while True:
        messages = get_upd(update_id)
        for message in messages:
            if update_id < message['update_id']:
                update_id = message['update_id']
                telegram_bot(
                    message['message']['chat']['id'], message['message']['text'])


if __name__ == '__main__':
    with open('config.yaml', 'r') as f:
        yml = yaml.load(f, Loader=SafeLoader)
    connection = create_connection(
        host_name=yml['db']['host_name'],
        user_name=yml['db']['user_name'],
        user_password=yml['db']['user_password'],
        db_name=yml['db']['db_name'])
    token = yml['bot']['token']
    upd = get_upd()
    run()
