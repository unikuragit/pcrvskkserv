#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    pgcrvskkserv.py 0.0.1
#    Copyright 2016, SASAKI Nobuyuki. Licensed under the MIT license.
#
#    usage: python pgcrvskkserv.py
#    See also https://www.google.co.jp/ime/cgiapi.html
#

import sys
import socket
import threading
import urllib.parse
import urllib.request
import json

VERSION = 'pgcrvskkserv.py 0.0.1'
HOST = '127.0.0.1'
PORT = 58513
ENCODING = 'euc_jis_2004'
#ENCODING = 'utf_8'
BASEURL = 'https://www.google.com/transliterate?langpair=ja-Hira|ja&text='
SUFFIX = ','
ANNOTATION = 'G'

def serv():
    while True:
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((HOST, PORT))
            s.listen(1)
            print('listening')
        except socket.error:
            s.close()
            print('socket open error')
            sys.exit(1)
        conn, addr = s.accept()
        print('connected by', addr)
        t = threading.Thread(target=comm, args=(conn, addr))
        t.start()

def comm(conn, addr):
    print('communication started')
    while True:
        try:
            data = conn.recv(1024)
        except socket.error:
            print('connection error')
            break
        if not data: break
        req = data.decode(ENCODING)
        command = req[0:1]
        pw(u'=> ' + req)
        m = '4\n'
        if (command == '1'):
            m = request(req[1:len(req) - 1])
        elif (command == '2'):
            m = VERSION + ' '
        elif (command == '3'):
            m = socket.gethostname() + ':' + \
                socket.gethostbyname(socket.gethostname()) + ' '
        pw(u'<= ' + m)
        conn.send(encode(m, ENCODING))

def request(s):
    try:
        url = BASEURL + urllib.parse.quote(s + SUFFIX)
        f = urllib.request.urlopen(url)
        s = f.read().decode('utf_8')
        joiner = ''
        if ANNOTATION:
            joiner = ';' + ANNOTATION
        return '1/' + (joiner + '/').join(json.loads(s)[0][1]) + joiner + '/\n'
    except urllib.error.URLError:
        return '4\n'

def encode(s, enc):
    e = b''
    try:
        e = s.encode(enc)
    except UnicodeEncodeError:
        for c in s:
            try:
                e += c.encode(enc)
            except UnicodeEncodeError:
                e += b'?'
    return e

def pw(s):
    try:
        print(s)
    except UnicodeEncodeError:
        for c in s:
            try:
                print(c, end='')
            except UnicodeEncodeError:
                print('?', end='')

if __name__ == "__main__":
    print(VERSION)
    serv()
