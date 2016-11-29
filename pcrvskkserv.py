#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    pcrvskkserv.py 0.0.1
#    Copyright 2016, SASAKI Nobuyuki. Licensed under the MIT license.
#
#    usage: python pcrvskkserv.py <skk dic file>
#

import codecs
import sys
import socket
import threading

VERSION = 'pcrvskkserv.py 0.0.1'
HOST = '127.0.0.1'
PORT = 1178
ENCODING = 'euc_jis_2004'
#ENCODING = 'utf_8'
dict = {}

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
            key = req[1:]
            if (key in dict):
                m = '1' + dict[key]
        elif (command == '2'):
            m = VERSION + ' '
        elif (command == '3'):
            m = socket.gethostname() + ':' + \
                socket.gethostbyname(socket.gethostname()) + ' '
        pw(u'<= ' + m)
        conn.send(m.encode(ENCODING))

def init(f):
    comment = ';;'
    for line in codecs.open(f, 'r', ENCODING):
        if (len(line) < 2):
            continue
        if (line[:len(comment)] == comment):
            continue
        si = line.find(' /')
        if (si < 0):
            continue
        key = line[:si + 1]
        candidates = line[si + 1:]
        dict[key] = candidates
    print('entry: %d' % len(dict))

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
    if (len(sys.argv) != 2):
        print('usage: python pcrvskkserv.py <skk dic file>')
        sys.exit(1)
    init(sys.argv[1])
    serv()
