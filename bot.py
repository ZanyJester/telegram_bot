# -*- coding: UTF-8 -*-
import datetime
import requests
import logging
import time
import yaml
from yaml.loader import SafeLoader
from mysql.connector import connect

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s', filename='log.txt')


def create_connection(host_name, user_name, user_password, db_name):
    # строка подкления к бд
    connection = None
    try:
        connection = connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        log_message("Connection to MySQL DB successful",
                    connection, datetime.datetime.now())
    except Exception as e:
        log_message("The error create_connection", e, datetime.datetime.now())
        time.sleep(5)
        return False
    return connection


def execute_query(connection, query, val):
    # вставка, обвновление и удаление записей
    cursor = connection.cursor()
    try:
        cursor.execute(query, val)
        connection.commit()
        log_message("Query executed successfully",
                    query, datetime.datetime.now())
    except Exception as e:
        log_message("The error execute_query", e, datetime.datetime.now())


def execute_read_query(connection, query, val=None):
    # выборка записей
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, val)
        result = cursor.fetchall()
        log_message(connection, query, datetime.datetime.now())
        return result
    except Exception as e:
        log_message("The error read_query", e, datetime.datetime.now())


def log_message(chat_id, text, date):
    log = str(chat_id) + ' ' + str(text) + ' ' + str(date)
    logging.info(log)


def telegram_bot(chat_id, text):
    # телеграм бот, парсер команд
    parse_text = text.replace(',', "")
    command = parse_text.split()[0]
    user_id = upd[-1]['message']['chat']['id']
    if command == '/start':
        row = execute_read_query(
            connection, "select vcode from telegram_bot_db.user where user_id = %(user_id)s", {'user_id': user_id})
        execute_query(connection, "insert into telegram_bot_db.users (user_id,date_appeal) VALUES (%(user_id)s, %(date_appeal)s)", {
                      'user_id': user_id, 'date_appeal': datetime.datetime.now()})
        send_msg(chat_id, 'Hi write /help')
    elif command == '/write':
        content = parse_text.partition(command)[2]
        message_id = upd[-1]['message']['message_id']
        messageTime = upd[-1]['message']['date']
        messageTime = datetime.datetime.utcfromtimestamp(messageTime)
        messageTime = messageTime.strftime('%Y-%m-%d %H:%M:%S')
        TimeStamp = str(messageTime)
        if content:
            execute_query(connection, "insert into telegram_bot_db.messages (user_id, message_id, text_msg, date_send) values ( %(user_id)s , %(message_id)s, %(text_msg)s, %(date_send)s)",
                          {'user_id': user_id, 'message_id': message_id, 'text_msg': content, 'date_send': TimeStamp, })
            row = execute_read_query(
                connection, "select vcode from telegram_bot_db.messages where user_id = %(user_id)s order by vcode desc limit 1", {'user_id': user_id})
            rows = row[0][0]
            send_msg(chat_id, 'note {0} saved'.format(rows))
        else:
            send_msg(chat_id, 'note is blank!')
    elif command == '/read_last':
        row = execute_read_query(
            connection, "select text_msg from telegram_bot_db.messages where user_id = %(user_id)s order by vcode desc limit 1", {'user_id': user_id})
        rows = row[0][0]
        send_msg(chat_id, '{0}'.format(rows))
    elif command == '/read_all':
        rows = execute_read_query(
            connection, "select text_msg from telegram_bot_db.messages where user_id = %(user_id)s order by vcode", {'user_id': user_id})
        for row in rows:
            rows = row[0]
            send_msg(chat_id, '{0}'.format(rows))
    elif command == '/read':
        content = parse_text.partition(command)[2]
        row = execute_read_query(
            connection, "select text_msg from telegram_bot_db.messages where user_id = %(user_id)s and vcode = %(vcode)s order by vcode", {'user_id': user_id, 'vcode': content})
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
            connection, "select name_tag from telegram_bot_db.tags where name_tag = %(name_tag)s order by vcode", {'name_tag': tag})
        if row:
            send_msg(chat_id, 'Tag updated')
            execute_query(
                connection, "update telegram_bot_db.tags set name_tag =  %(name_tag)s, discription = %(discription)s where name_tag = %(name_tag)s", {'name_tag': tag, 'discription': discr})
        else:
            execute_query(
                connection, "insert into telegram_bot_db.tags (name_tag, discription) values ( %(name_tag)s, %(discription)s)", {'name_tag': tag, 'discription': discr})
            send_msg(chat_id, 'Tag saved')
    elif command == '/read_tag':
        content = parse_text.partition(command)[2]
        row = execute_read_query(
            connection, "select text_msg from telegram_bot_db.messages where user_id = %(user_id)s and MATCH (text_msg) AGAINST (+%(tag)s)", {'user_id': user_id, 'tag': content})
        if row or '':
            send_msg(chat_id, '{0}'.format(row[0][0]))
        else:
            send_msg(chat_id, 'You didnt enter a note <tag> ')
    elif command == '/tag':
        content = parse_text.partition(command)[2]
        tags = content.split()
        for tag in tags:
            rows = execute_read_query(
                connection, "select discription from telegram_bot_db.tags where name_tag = %(name_tag)s order by vcode", {'name_tag': tag})
            for row in rows:
                rows = row[0]
                send_msg(chat_id, '{0}'.format(rows))
    elif command == '/help':
        send_msg(chat_id,
                 "The /write command writes a message.\n"
                 "The /read_last command displays the last message for the given user.\n"
                 "The /read <id> command displays the message field with the specified id.\n"
                 "The /read_all command lists all the notes of the current bot user in order from oldest to newest.\n"
                 "The /read_tag tag command displays all the user's notes by the specified tag in the message.\n"
                 "The /write_tag <tag> <tag description> command creates a tag. If the tag already exists, then changes its description.\n"
                 "The /tag <tag_1>,<tag_2>...<tag_n> command displays the description of the entered tags.\n"
                 "The /tag_all command displays a description of all tags.\n")
    elif command:
        send_msg(chat_id, 'write /help')
    return text


def get_upd(offset=0):
    # получаем последние сообщения
    result = requests.get(url='https://api.telegram.org/bot{0}/{1}'.format(token, "getUpdates"), params={"offset": offset, }, timeout=60).json()
    return result['result']


def send_msg(chat_id, text):
    # отвечаем в чат пользователю
    requests.get(url='https://api.telegram.org/bot{0}/{1}'.format(token, "sendMessage"), params={"chat_id": chat_id, "text": text, }, timeout=60)


def run():
    # cпроверяем сообщения в чате
    update_id = upd[-1]['update_id']
    connection = False
    while True:
        if not connection:
            while True:
                connection = create_connection(
                    host_name=yml['db']['host_name'],
                    user_name=yml['db']['user_name'],
                    user_password=yml['db']['user_password'],
                    db_name=yml['db']['db_name'])
                if connection:
                    break
        messages = get_upd(update_id)
        for message in messages:
            if update_id < message['update_id']:
                update_id = message['update_id']
                telegram_bot(
                    message['message']['chat']['id'], message['message']['text'])
                log_message(message['message']['chat']['id'],
                            message['message']['text'], datetime.datetime.now())


if __name__ == '__main__':
    # грузим конфиг для бд и api
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
