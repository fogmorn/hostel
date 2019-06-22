#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import ldap
import cgi
import string
import sha
import time
import os
import Cookie
import re



def login_form(page='', err_msg=''):
    print "Content-type: text/html\n"
    print """<html><head><title>Общежитие</title>
    <link rel="stylesheet" href="css/style.css" type="text/css" />
    </head>
    <body>
    <h1>Аутентификация</h1>
    
    <div class='content'>
    <form method=post action=https://hostel/auth.py>
    
    <div class='section'>
    <p class='err_msg'>"""+err_msg+"""</p>
    <div class='field'>
    <span class='field_name'>Логин</span><br />
    <input name=username type=text maxlength=15 autofocus />
    </div>

    <div class='field'>
    <span class='field_name'>Пароль</span><br />
    <input name=passwd type=password maxlength=15 />
    </div>
    <div style="clear: both;"></div>

    <input class='button' name=enter type=submit value="Войти" />
    <input name='page' type='hidden' value='"""+page+"""' />
    </div>
    </form>
    </div>
    </body></html>"""

    return



def ldap_auth(username, passwd):
    username = re.sub(r'[\';:&%\^\$\*\\/#\{\}"<>]', '', username)

    l = ldap.initialize('ldap://192.168.0.1')

    dn = username+"@a.loc"
    timeout = 0
    base_dn = "ou=фин,dc=a,dc=loc"
    member_of_list = ["cn=hostel,ou=группы,ou=фин,dc=a,dc=loc",
                      "cn=в,ou=в,ou=фин,dc=a,dc=loc"]
    scope = ldap.SCOPE_SUBTREE

    try:
        l.simple_bind_s(dn, passwd)
    except ldap.LDAPError, err_msg:
        login_form(err_msg = 'Неверный логин или пароль.')
        return


    for member_of in member_of_list:
    
        filter = "(&(memberOf="+member_of+")(sAMAccountName="+username+"))"
        ldap_result_id = l.search(base_dn, scope, filter, None) 
        result_set = []

        result_type, result_data = l.result(ldap_result_id, timeout)
    
        if result_data:
            if result_type == ldap.RES_SEARCH_ENTRY:
                result_set.append(result_data)
                break

    l.unbind_s()

    if not result_set:
        login_form(err_msg = 'Ошибка (№ 001).')
        return
    else:
        create_session(username)
    return



def create_session(username):
    del_session(username = username)

    file = open('sessions.txt', 'a')

    session_id = sha.new(repr(time.time())).hexdigest()

    file.write(session_id+":"+username+"\n")
    file.close()

    response('/hostel/main.cgi', session_id)
    return



def response(page, session_id):
    print "Content-type: text/html"
    print "Location: https://"+ os.environ["HTTP_HOST"] +"/hostel/"
    print "Set-Cookie: session_id="+session_id+"\n"



def ck_session():
    try:
        cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
        session_id = cookie["session_id"].value
    except:
        return


    f = open('sessions.txt')

    for line in f:
        sess_key_in_file = string.split(line, ":")
        if session_id == sess_key_in_file[0]:
            return True
    return 
    


def del_session(session_id='', username=''):
    sessions = []

    with open('sessions.txt') as fd:
        t = fd.read()

        for line in t.splitlines():
            if session_id not in line or username not in line:
                sessions.append(line)

    with open('sessions.txt', 'w') as fd:
        fd.write('\n'.join(sessions))
        fd.write('\n') # with join we lose the last newline char

    fd.close()

    # Если `username' пусто, значит нажата кнопка `Выход',
    # иначе целью вызова была чистка заброшенных сессий.
    if username:
        return
    else:
        print "Content-type: text/html"
        print "Location: https://"+ os.environ["HTTP_HOST"] +"/hostel/\n"
        return



def main():
    f = cgi.FieldStorage()
    if f.has_key("username") and f.has_key("passwd"):
        ldap_auth(f["username"].value, f["passwd"].value)

    elif f.has_key("exit"):
        try:
            cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
            session_id = cookie["session_id"].value
        except:
            return
        del_session(session_id=session_id)
    else:
        login_form(f.getvalue('page', '/hostel/'))

if __name__ == "__main__":
    main()
