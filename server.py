#!/usr/bin/env python2
import sys
import logging
import time
from hashlib import sha1

from wspy import AsyncServer, TextMessage
from game import Board


class BadRequest(RuntimeError):
    pass


def check(condition, error='invalid type or args'):
    if not condition:
        raise BadRequest(error)


class Msg:
    def __init__(self, mtype, *args):
        self.mtype = mtype
        self.args = args

    @classmethod
    def decode(cls, message):
        check(isinstance(message, TextMessage))
        parts = message.payload.split(';')
        check(parts)
        mtype = parts[0]
        args = [int(p) if p.isdigit() else p for p in parts[1:]]
        return cls(mtype, *args)

    def encode(self):
        return TextMessage(';'.join([self.mtype] + map(str, self.args)))


STATE_JOINING = 0
STATE_STARTED = 1
STATE_FINISHED = 2


class Session:
    def __init__(self, w, h, owner):
        self.sid = sha1(str(time.time())).hexdigest()
        self.clients = [owner]
        owner.player = 1
        self.player_counter = 2
        self.state = STATE_JOINING
        self.board = Board(w, h)
        self.turn = owner

        owner.send(Msg('newgame', self.sid, w, h).encode())
        owner.send(Msg('turn', self.turn.player).encode())

    def __str__(self):
        return '<Session %s state=%d size=%dx%d>' % \
                (self.sid, self.state, self.board.w, self.board.h)

    def click_wall(self, client, x, y, direction):
        check(self.turn is client, 'not your turn')
        check(self.state < STATE_FINISHED, 'already finished')
        self.state = STATE_STARTED

        occupied = self.board.click_wall(x, y, direction, client.player)
        self.bcast('clickwall', x, y, direction)

        if occupied:
            for x, y in occupied:
                self.bcast('occupy', x, y, client.player)

            if self.board.is_finished():
                scores = self.board.scores()

                for player in xrange(1, self.player_counter):
                    scores.setdefault(player, 0)

                scores = scores.items()
                scores.sort(key=lambda (player, score): score, reverse=True)

                self.bcast('finish', *['%d:%d' % s for s in scores])
                logging.info('finishing session %s' % self.sid)
                self.state = STATE_FINISHED
        else:
            index = (self.clients.index(self.turn) + 1) % len(self.clients)
            self.turn = self.clients[index]

    def bcast(self, mtype, *args):
        encoded = Msg(mtype, *args).encode()

        for client in self.clients:
            client.send(encoded)

    def join(self, client):
        client.player = self.player_counter
        self.player_counter += 1

        self.bcast('join', client.player)

        client.send(Msg('newgame', self.sid, self.board.w, self.board.h,
                        client.player).encode())
        client.send(Msg('turn', self.turn.player).encode())

        for other in self.clients:
            client.send(Msg('join', other.player).encode())

        self.clients.append(client)

    def leave(self, client):
        self.clients.remove(client)
        self.bcast('leave', client.player)

    def is_dead(self):
        return not self.clients


class GameServer(AsyncServer):
    def __init__(self, *args, **kwargs):
        super(GameServer, self).__init__(*args, **kwargs)
        self.sessions = {}

    def onmessage(self, client, message):
        try:
            msg = Msg.decode(message)

            if msg.mtype == 'newgame':
                check(len(msg.args) == 2)
                w, h = msg.args
                client.session = session = Session(w, h, client)
                self.sessions[session.sid] = session
                logging.info('%s created session %s' % (client, session))

            elif msg.mtype == 'join':
                check(len(msg.args) == 1)
                sid = msg.args[0]
                check(not hasattr(client, 'session'), 'already in a session')
                check(sid in self.sessions, 'no such session')
                session = self.sessions[sid]
                check(session.state == STATE_JOINING, 'game already started')
                session.join(client)
                client.session = session
                logging.info('%s joined %s' % (client, session))

            elif msg.mtype == 'clickwall':
                check(len(msg.args) == 3)
                x, y, direction = msg.args
                check(client.session, 'no session associated with client')
                client.session.click_wall(client, x, y, direction)

            else:
                raise BadRequest('unknown message type')

        except BadRequest as e:
            logging.warning('bad request: %s' % e.message)
            client.send(Msg('error', e.message).encode())

    def onclose(self, client, code, reason):
        if hasattr(client, 'session'):
            client.session.leave(client)
            logging.info('%s left %s' % (client, client.session))

            if client.session.is_dead():
                logging.info('deleting session %s' % client.session)
                del self.sessions[client.session.sid]


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >>sys.stderr, 'usage: % PORT' % sys.argv[0]
        sys.exit(1)

    port = int(sys.argv[1])
    GameServer(('', port)).run()
    #GameServer(('', port), loglevel=logging.DEBUG).run()
