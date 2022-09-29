import datetime
import requests
import logging
import time
import yaml
from yaml.loader import SafeLoader
from mysql.connector import connect,Error

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s', filename='log.txt')

class db_context():
    #create string connection db
    def create_connection(self,host_name, user_name, user_password, db_name):
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
    #for insert,update,delete quary
    def execute_query(self, connection, query, val):
        cursor = connection.cursor()
        try:
            cursor.execute(query, val)
            connection.commit()
            print("Query executed successfully")
        except Error as e:
            print("The error execute_query {0} occurred").format(e)
    #for select query     
    def execute_read_query(self, connection, query):
        cursor = connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print("The error read_query {0} occurred").format(e)

class get_log():
    def loggining(self):
        user_id = bot.get_upd()[-1]['message']['chat']['id']
        text = bot.get_upd()[-1]['message']['text']
        messageTime = bot.get_upd()[-1]['message']['date']
        messageTime = datetime.datetime.utcfromtimestamp(messageTime)
        messageTime = messageTime.strftime('%Y-%m-%d %H:%M:%S')
        loguserid=str(user_id)
        logtext=str(text)
        logdate = str(messageTime)
        log = loguserid +' '+ logtext +' '+ logdate
        logging.info(log)            


class telega_bot():
    # parse command 
    def parse_text_to_command(self, chat_id, text):
        parse_text= text.replace(',',"") 
        command = parse_text.split()[0]
        if command == '/write':
            content = parse_text.partition(command)[2]
            user_id = self.get_upd()[-1]['message']['chat']['id']
            message_id = self.get_upd()[-1]['message']['message_id']
            messageTime = self.get_upd()[-1]['message']['date']
            messageTime = datetime.datetime.utcfromtimestamp(messageTime)
            messageTime = messageTime.strftime('%Y-%m-%d %H:%M:%S')
            TimeStamp = str(messageTime)
            if content:
                db.execute_query(connection, "insert into telegram_bot_db.messages (user_id, message_id, text_msg, date_send) values ( %s , %s, %s, %s)", (user_id, message_id,content, TimeStamp,))
                row = db.execute_read_query(connection, "select vcode from telegram_bot_db.messages where user_id = {0} order by vcode desc limit 1".format(user_id))
                rows = row[0][0]
                self.send_msg(chat_id, u'note {0} saved'.format(rows))
            else:
                self.send_msg(chat_id, u'note is blank!')   
        elif command == '/read_last':
            user_id = self.get_upd()[-1]['message']['chat']['id']
            row = db.execute_read_query(connection, "select text_msg from telegram_bot_db.messages where user_id = {0} order by vcode desc limit 1".format(user_id))
            rows = row[0][0]
            self.send_msg(chat_id, '{0}'.format(rows))
        elif command == '/read_all':
            user_id = self.get_upd()[-1]['message']['chat']['id']
            rows = db.execute_read_query(connection, "select text_msg from telegram_bot_db.messages where user_id = {0} order by vcode".format(user_id))
            for row in rows:
                rows = row[0]
                self.send_msg(chat_id, '{0}'.format(rows))      
        elif command == '/read':
            user_id = self.get_upd()[-1]['message']['chat']['id']
            content = parse_text.partition(command)[2]
            row = db.execute_read_query(connection, "select text_msg from telegram_bot_db.messages where user_id = {0} and vcode = {1} order by vcode".format(user_id, content))
            if row or '':
                self.send_msg(chat_id, '{0}'.format(row[0][0]))
            else:
                self.send_msg(chat_id, 'You didnt enter a note <id> ') 
        elif command == '/tag_all':
            user_id = self.get_upd()[-1]['message']['chat']['id']
            rows = db.execute_read_query(connection, "select discription from telegram_bot_db.tags order by vcode")
            for row in rows:
                rows = row[0]
                self.send_msg(chat_id, '{0}'.format(rows))
        elif command == '/write_tag':
            tag_discr = parse_text.partition(command)[2]
            split_tag_dicrs = tag_discr.split()
            tag = split_tag_dicrs[0]
            discr= parse_text.partition(tag)[2]
            row = db.execute_read_query(connection, "select name_tag from telegram_bot_db.tags where name_tag like '%{0}' order by vcode".format(tag))
            if row:
                self.send_msg(chat_id, 'Tag updated')
                db.execute_query(connection, "update telegram_bot_db.tags set name_tag =  %s, discription = %s where name_tag like '%{0}%'".format(tag), (tag, discr))
            else:
                db.execute_query(connection, "insert into telegram_bot_db.tags (name_tag, discription) values ( %s, %s)", (tag, discr))
                self.send_msg(chat_id, 'Tag saved')               
        elif command == '/read_tag':
            user_id = self.get_upd()[-1]['message']['chat']['id']
            content = parse_text.partition(command)[2]
            row = db.execute_read_query(connection, "select text_msg from telegram_bot_db.messages where user_id = {0} and text_msg like '%{1}%'".format(user_id, content))
            if row or '':
                self.send_msg(chat_id, '{0}'.format(row[0][0]))
            else:
                self.send_msg(chat_id, 'You didnt enter a note <tag> ')
        elif command == '/tag':
            user_id = self.get_upd()[-1]['message']['chat']['id']
            content = parse_text.partition(command)[2]
            tags = content.split()
            for tag in tags:
                rows = db.execute_read_query(connection, "select discription from telegram_bot_db.tags where name_tag like '%{0}%' order by vcode".format(tag))
                for row in rows:
                    rows = row[0]
                    self.send_msg(chat_id, '{0}'.format(rows))
        elif command == '/help':
            text ="""The /write command writes a message
            The /read_last command displays the last message for the given user.
            The /read <id> command displays the message field with the specified id.
            The /read_all command lists all the notes of the current bot user in order from oldest to newest.
            The /read_tag tag command displays all the user's notes by the specified tag in the message
            The /write_tag <tag> <tag description> command creates a tag. If the tag already exists, then changes its description.
            The /tag <tag_1>,<tag_2>...<tag_n> command displays the description of the entered tags.
            The /tag_all command displays a description of all tags.
            """
            self.send_msg(chat_id, text)
        elif command == '' or ' ':
            self.send_msg(chat_id, 'write /help')
        return text
    #get new messages
    def get_upd(self, offset=0):
        result = requests.get(                                                          
            url='https://api.telegram.org/bot{0}/{1}'.format(token,"getUpdates"),
            params = {
                "offset": offset,
            }
        ).json()
        return result['result']
    #get new user before user writed /start
    def get_user(self, user_id):                   
        db.execute_query(connection, """insert into telegram_bot_db.users (user_id,date_appeal) VALUES (%s, %s)""", (user_id, datetime.datetime.now(),))
    #anwser user
    def send_msg(self, chat_id, text):
        requests.get(
        url='https://api.telegram.org/bot{0}/{1}'.format(token,"sendMessage"),
        params = {
            "chat_id": chat_id,
            "text": text,
        })
    #check new messages in chat                      
    def check_msg(self, chat_id, message):
        user_id = self.get_upd()[-1]['message']['chat']['id']
        for mes in message.lower():
            if mes in ['/start']:
                self.get_user(user_id)
                self.send_msg(chat_id, 'Hi write /help')            
                                                                                       
def run():
    update_id = bot.get_upd()[-1]['update_id']
    while True:
        time.sleep(2)
        log.loggining()
        messages = bot.get_upd(update_id)
        for message in messages:
            if update_id < message['update_id']:
                update_id = message['update_id']
                bot.check_msg(message['message']['chat']['id'], message['message']['text'])
                bot.parse_text_to_command(message['message']['chat']['id'],message['message']['text'])
        
                           
if __name__ == '__main__':
    db = db_context()
    bot = telega_bot()
    log= get_log()
    with open('config.yaml', 'r') as f:
        yml = yaml.load(f, Loader=SafeLoader)
    connection = db.create_connection(
        host_name=yml['db']['host_name'], 
        user_name=yml['db']['user_name'], 
        user_password=yml['db']['user_password'], 
        db_name=yml['db']['db_name'])
    token = yml['bot']['token']
    run()

    