WALL_NONE   = 0
WALL_TOP    = 1
WALL_RIGHT  = 2
WALL_BOTTOM = 4
WALL_LEFT   = 8
WALL_ALL = WALL_TOP | WALL_RIGHT | WALL_BOTTOM | WALL_LEFT


class Board:
    def __init__(self, w, h):
        assert w > 1 and h > 1
        self.w = w
        self.h = h
        self.rooms = [[None] * w for _ in xrange(h)]
        self.walls = [[WALL_NONE] * w for _ in xrange(h)]

        for col in xrange(w):
            self.walls[0][col] |= WALL_TOP
            self.walls[-1][col] |= WALL_BOTTOM

        for row in self.walls:
            row[0] |= WALL_LEFT
            row[-1] |= WALL_RIGHT

    def click_wall(self, x, y, direction, player):
        def try_click(x, y, d):
            if 0 <= x < self.w and 0 <= y < self.h:
                if self.walls[y][x] & d:
                    raise ValueError('dir %d already set on %d,%d' % (d, x, y))

                self.walls[y][x] |= d

                if self.walls[y][x] == WALL_ALL:
                    self.rooms[y][x] = player
                    rooms.append((x, y))

        rooms = []
        try_click(x, y, direction)

        if direction == WALL_TOP:
            try_click(x, y - 1, WALL_BOTTOM)
        elif direction == WALL_RIGHT:
            try_click(x + 1, y, WALL_LEFT)
        elif direction == WALL_BOTTOM:
            try_click(x, y + 1, WALL_TOP)
        elif direction == WALL_LEFT:
            try_click(x - 1, y, WALL_RIGHT)

        return rooms

    def __str__(self):
        roomwidth = 3

        s = ('+' + '-' * roomwidth) * self.w + '+\n'

        for y, (rrow, wrow) in enumerate(zip(self.rooms, self.walls)):
            for x, (p, wall) in enumerate(zip(rrow, wrow)):
                s += '|' if wall & WALL_LEFT else ' '
                s += ('%%-%dd' % roomwidth) % p if p else ' ' * roomwidth

            s += '|\n'

            for wall in wrow:
                s += '+'
                s += ('-' if wall & WALL_BOTTOM else ' ') * roomwidth

            s += '+'

            if y != self.h - 1:
                s += '\n'

        return s

    def is_finished(self):
        return all(all(row) for row in self.rooms)

    def scores(self):
        indexed = {}

        for row in self.rooms:
            for player in row:
                if player:
                    indexed[player] = indexed.get(player, 0) + 1

        return indexed

    def sorted_scores(self):
        scores = self.scores().items()
        scores.sort(key=lambda (player, score): score, reverse=True)
        return scores
