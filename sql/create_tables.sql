create database telegram_bot_db

use telegram_bot_db;

create table Users
(
	vcode int primary key auto_increment,
    user_id int,
    date_appeal datetime
);

insert into telegram_bot_db.Users (user_id, text_msg) values ('840009263','2022-09-28 11:55:10')

create table Messages
(
	vcode int primary key auto_increment,
    user_id int,
    message_id int,
    text_msg varchar(255),
    date_send datetime,
    FULLTEXT (text_msg)
);

insert into telegram_bot_db.messages (user_id,message_id, text_msg,date_send) 
values 
('840009263','1','test1 #tag1','2022-09-28 12:12:10'),
('840009263','2','test2 #tag2','2022-09-28 13:00:10'),
('840009263','3','test3 #tag4 #tag3','2022-09-28 14:22:10')



create table Tags
(
	vcode int primary key auto_increment,
    name_tags varchar(255),
    discription varchar(255)
);

insert into telegram_bot_db.tags (name_tags,discription) 
values 
('#tag1','#tag1 - test tag1'),
('#tag2','#tag2 - test tag2'),
('#tag2','#tag3 - test tag3')


