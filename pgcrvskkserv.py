#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    pgcrvskkserv.py 0.0.3
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
import re

VERSION = 'pgcrvskkserv 0.0.3'
HOST = '127.0.0.1'
PORT = 1178
ENCODING = 'euc_jis_2004'
#ENCODING = 'utf_8'
BASEURL = 'https://www.google.com/transliterate?langpair=ja-Hira|ja&text='
SUFFIX = ','
ANNOTATION = 'G'

def serv():
    print('port: %d' % PORT)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            print('connected by', addr)
            t = threading.Thread(target=comm, args=(conn, addr))
            t.start()
    except socket.error:
        s.close()
        print('socket error')
        sys.exit(1)

def comm(conn, addr):
    print('started by', addr)
    while True:
        try:
            data = conn.recv(1024)
        except socket.error:
            print('connection error', addr)
            break
        if not data:
            conn.close()
            print('closed by', addr)
            break

        res = '4\n'
        req = data.decode(ENCODING)
        printq('=> ' + req)

        command = req[0:1]
        if (command == '0'):
            conn.close()
            break
        elif (command == '1'):
            res = request(req[1:len(req) - 1])
        elif (command == '2'):
            res = VERSION + ' '
        elif (command == '3'):
            res = socket.gethostname() + ':' + \
                socket.gethostbyname(socket.gethostname()) + ' '

        printq('<= ' + res)
        conn.send(encodeq(res, ENCODING))

def request(s):
    # probably okuri-ari
    if (re.fullmatch('[^A-Za-z0-9]+[a-z]', s)):
        return '4\n'
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

def encodeq(s, enc):
    e = b''
    for c in s:
        try:
            e += c.encode(enc)
        except UnicodeEncodeError:
            e += b'?'
    return e

def printq(s):
    for c in s:
        try:
            print(c, end='')
        except UnicodeEncodeError:
            print('?', end='')
    print('')

if __name__ == "__main__":
    print(VERSION)
    print('encoding: ' + ENCODING)
    serv()
