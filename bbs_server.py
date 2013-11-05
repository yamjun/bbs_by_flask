#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import mysql.connector
import hashlib
from flask import Flask, render_template, request, session, redirect, url_for
from db_lib import get_bbs_message,  set_bbs_message, check_user_password, \
        check_mail_address, add_user_info, get_user_name
from simplekv.memory import DictStore
from flaskext.kvsession import KVSessionExtension
import re

app =  Flask(__name__)
store = DictStore()
KVSessionExtension(store, app)

app.secret_key = "funkin boys"

def valid(string):
    return len(string) > 128
@app.route("/", )
def index():
    return redirect(url_for('login'))

def generator_csrf_token():
    csrf_token = hashlib.md5( str(uuid.uuid4()) ).hexdigest()
    session['csrf_token'] = csrf_token
    return csrf_token


@app.route("/login", methods = ['GET', 'POST'])
def login():
    if session.get('mail') is not None:
        return redirect('/bbs')

    error_msg = []
    if request.method == 'POST':

        #Formに情報が欠落していた場合#{{{
        if " " in request.form['mail'] and request.form['password'] :
            error_msg.append(u'空白文字が含まれています')
            return render_template('login.html', error = error_msg)
        if request.form['password']  == '':
            error_msg.append(u'パスワードを入力してください')
        if request.form['mail'] == '':
            error_msg.append(u'メールアドレスを入力してください')
        if valid(request.form['password']):
            error_msg.append(u'パスワードの文字数が多すぎます')
        if valid(request.form['mail']):
            error_msg.append(u'メールの文字数が多すぎます')
        if len(error_msg) != 0:
            return render_template('login.html', error = error_msg, info = request.form['mail'])
        #}}}

        # パスワードチェック
        if check_user_password((request.form['mail'], \
                hashlib.md5(request.form['password'] + 'solt').hexdigest())):
            #セッションの再発行
            session.regenerate()
            session['mail'] = request.form['mail']
            
            return redirect(url_for('bbs'))
        else:
            # パスワードマッチに失敗したとき
            return render_template('login.html', \
                    error = [u'メールアドレスまたはパスワードが違います'], info = request.form['mail'])
    # 更新時(F5)
    return render_template('login.html')

@app.route("/add_message", methods = ['GET', 'POST'])
def add_message():
    if session.get('mail') is None:
        return redirect('/login')
    user_name = get_user_name(session.get('mail'))
    if request.method == 'POST':
        # csrfのチェック
        if session['csrf_token'] == request.form['csrf_token']:
            session.pop('csrf_toke', None)
            #投稿
            text = request.form['text']
            if text == '':
                return render_template('bbs.html', \
                        error_msg = u'テキストを入力してください')
            if len(text) > 200:
                return render_template('bbs.html', \
                        error_msg = u'文字数が多すぎます')
            set_bbs_message((user_name, text))
    return redirect(url_for('bbs'))

@app.route("/bbs", methods = ['GET', 'POST'])
def bbs():
    if session.get('mail') is None:
        return redirect('/login')
    messages = get_bbs_message()
    csrf_token = generator_csrf_token()
    return render_template("bbs.html", messages = messages, csrf_token = csrf_token)


@app.route("/register", methods = ['GET', 'POST'])
def registor():
    error_msg = []
    if request.method  == 'POST':

        # Formに情報が欠落していた場合#{{{
        if " " in request.form['mail'] and request.form['password'] and request.form['username']:
            error_msg.append(u'空白文字が含まれています')
            return render_template("register.html", error = error_msg)
        if request.form['username']  == '':
            error_msg.append(u"ユーザ名を入力してください") 
        if request.form['password']  == '':
            error_msg.append(u'パスワードを入力してください')
        if request.form['mail'] == '':
            error_msg.append(u'メールアドレスを入力してください')
        if valid(request.form['password']):
            error_msg.append(u'パスワードの文字数が多すぎます')
        if valid(request.form['mail']):
            error_msg.append(u'メールの文字数が多すぎます')
        if valid(request.form['username']):
            error_msg.append(u'ユーザ名の文字数が多すぎます')
        if len(error_msg) != 0:
            return render_template("register.html", error = error_msg, \
                    info = [request.form['username'], request.form['mail']])
        #}}}

        if check_mail_address(request.form['mail']):
            error_msg.append(u'メールが重複しています')
            return render_template("register.html", error = error_msg,\
                    info = [request.form['username'], request.form['mail']])

        password_hash = hashlib.md5(request.form['password'] + 'solt').hexdigest()
        csrf_token = get_bbs_message()
        return render_template("configuration.html", \
                user_info = [request.form['username'], \
                            password_hash, request.form['mail']], \
                            csrf_token = csrf_token)
    return render_template("register.html", info = ['', ''])


@app.route("/add_user", methods = ['POST'])
def add_user():
    # csrfのチェック
    if session['csrf_token'] == request.form['csrf_token']:
        session.pop('csrf_toke', None)
        add_user_info((request.form['username'], \
                request.form['password'], request.form['mail']))
    return redirect(url_for('bbs'))


@app.route("/logout")
def logout():
    session.pop('mail', None)
    return redirect('/login')

@app.context_processor 
def my_utility_processor():
    r = re.compile(r"(http?://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+)")
    rs = re.compile(r"(https?://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+)")
    def check(string):
        if rs.search(string) is None :
            if r.search(string) is None:
                return False
        return True
    def foo(string):
        string = rs.sub(r'<a href="\1">\1</a>', string)
        string = r.sub(r'<a href="\1">\1</a>', string)
        return string

    return dict(baz=foo, check=check)

def main():
    app.debug = True
    app.run()
    
if __name__ == '__main__':
    main()
