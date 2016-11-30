#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#    pcrvskkserv.py 0.0.2
#    Copyright 2016, SASAKI Nobuyuki. Licensed under the MIT license.
#
#    usage: python pcrvskkserv.py <skk dic file>
#

import codecs
import sys
import socket
import threading

VERSION = 'pcrvskkserv 0.0.2'
HOST = '127.0.0.1'
PORT = 1178
ENCODING = 'euc_jis_2004'
#ENCODING = 'utf_8'
dictionary = {}

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
        printq(u'=> ' + req)

        command = req[0:1]
        if (command == '0'):
            conn.close()
            break
        elif (command == '1'):
            key = req[1:]
            if (key in dictionary):
                res = '1' + dictionary[key]
        elif (command == '2'):
            res = VERSION + ' '
        elif (command == '3'):
            res = socket.gethostname() + ':' + \
                socket.gethostbyname(socket.gethostname()) + ' '

        printq(u'<= ' + res)
        conn.send(res.encode(ENCODING))

def init(f):
    comment = ';;'
    for line in codecs.open(f, 'r', ENCODING):
        if (line.startswith(comment)):
            continue
        si = line.find(' /')
        if (si < 0):
            continue
        key = line[:si + 1]
        candidates = line[si + 1:]
        dictionary[key] = candidates
    print('entry: %d' % len(dictionary))

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
    if (len(sys.argv) != 2):
        print('usage: python pcrvskkserv <skk dic file>')
        sys.exit(1)
    init(sys.argv[1])
    serv()
