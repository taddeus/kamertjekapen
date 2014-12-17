URL = 'ws://localhost:8099'
PLAYER_COLORS = ['blue', 'green', 'red', 'yellow']

WALL_NONE   = 0
WALL_TOP    = 1
WALL_RIGHT  = 2
WALL_BOTTOM = 4
WALL_LEFT   = 8
WALL_ALL    = WALL_TOP | WALL_RIGHT | WALL_BOTTOM | WALL_LEFT

div = (cls) ->
    elem = document.createElement 'div'
    elem.className = cls
    elem

divin = (parent, cls) ->
    elem = div cls
    parent.appendChild elem
    elem

class Game
    constructor: (@w, @h, elem) ->
        @render elem if elem

    get_wall: (x, y, direction) ->
        x *= 2
        y *= 2

        if direction == WALL_TOP
            x += 1
        else if direction == WALL_RIGHT
            x += 2
            y += 1
        else if direction == WALL_BOTTOM
            x += 1
            y += 2
        else if direction == WALL_LEFT
            y += 1

        @board.children[y].children[x]

    click_wall: (x, y, direction) ->
        wall = @get_wall x, y, direction
        wall.className += ' clicked'

    get_room: (x, y) ->
        @board.children[y * 2 + 1].children[x * 2 + 1]

    occupy: (x, y, player) ->
        room = @get_room x, y
        room.style.backgroundColor = PLAYER_COLORS[player]

    render: (elem) ->
        @board = div 'board'
        elem.appendChild @board

        row = divin @board, 'row'
        for x in [1..@w]
            divin row, 'dot'
            divin row, 'wall-h clicked'
        divin row, 'dot'

        for y in [1..@h]
            row = divin @board, 'row'
            for x in [1..@w]
                clicked = if x == 1 then ' clicked' else ''
                divin row, "wall-v#{clicked}"
                divin row, 'room'
            divin row, 'wall-v clicked'

            row = divin @board, 'row'
            clicked = if y == @h then ' clicked' else ''
            for x in [1..@w]
                divin row, 'dot'
                divin row, "wall-h#{clicked}"
            divin row, 'dot'

game = new Game 6, 6
game.render document.getElementById 'game'
game.click_wall 2, 2, WALL_RIGHT
game.click_wall 2, 2, WALL_BOTTOM
game.click_wall 1, 2, WALL_RIGHT
game.click_wall 2, 2, WALL_TOP
game.occupy 2, 2, 2

#ws = new WebSocket URL
#
#ws.onopen = ->
#    console.log 'open'
#
#ws.onclose = ->
#    console.log 'close'
#
#ws.onerror = (e) ->
#    console.log 'error', e
#
#ws.onmessage = (msg) ->
#    console.log 'msg', msg
