#!/usr/bin/env python2
import time
from hashlib import sha1

import wspy


class Session:
    def __init__(self):
        self.sid = sha1(str(time.time()))
        self.clients = []


class GameServer(wspy.AsyncServer):
    def onmessage(self, client, message):
        pass


if __name__ == '__main__':
    GameServer(('', 8099)).run()
