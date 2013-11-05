#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
import re
def init_mysql_connector():#{{{
    import mysql.connector
    con = mysql.connector.connect(
        host='localhost',
        db='takoyaki',
        user='root',
        passwd='admin',
        buffered=True)
    return con


def get_bbs_message():
    con = init_mysql_connector()
    cur = con.cursor()
    query = "select * from bbs order by insert_time desc ";
    cur.execute(query)

    messages = []
    for message in cur:
        messages.append(message)
    return messages

def set_bbs_message(commit):
    con = init_mysql_connector()
    cur = con.cursor()
    query = "insert into bbs(user_name, text) values(%s, %s)";
    cur.execute(query, commit)

def check_user_password(commit):
    con = init_mysql_connector()
    cur = con.cursor()
    query = "select * from user where mail = %s and password = %s"
    cur.execute(query, commit)
    if (len([x for x in cur]) == 1):
        return True
    return False
    
def check_mail_address(mail):
    con = init_mysql_connector()
    cur = con.cursor()
    query = "select * from user where mail = %s"
    cur.execute(query, (mail,) )
    if (len([x for x in cur]) ==  1):
        return True
    return False

def add_user_info(commit):
    con = init_mysql_connector()
    cur = con.cursor()
    query = "insert into user(user_name, password, mail) values(%s, %s, %s)"
    cur.execute(query, commit)

def get_user_name(mail):
    con = init_mysql_connector()
    cur = con.cursor()
    query = "select user_name from user where mail = %s"
    cur.execute(query, (mail,) )

    return cur.fetchone()[0]
