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

class Board
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

    destroy: ->
        @board.parentNode.removeChild @board

show_error = alert

set_this_player = (id) ->

add_other_player = (id) ->

remove_other_player = (id) ->

set_turn_player = (id) ->

finish = (scores) ->
    console.log 'scores:', scores

cancel = (reason) ->

ws = new WebSocket URL

ws.send_msg = (mtype, args...) ->
    console.debug '>', mtype, args
    @send [mtype].concat(args).join ';'

ws.onopen = ->
    console.debug 'open'

    if location.hash
        @send_msg 'join', location.hash.substr 1
    else
        @send_msg 'newgame', 5, 6

ws.onclose = ->
    console.debug 'close'
    @board?.destroy()

ws.onerror = (e) ->
    console.debug 'error', e

ws.onmessage = (msg) ->
    [mtype, args...] = msg.data.split ';'
    args = args.map (s) -> if s.match /^\d+$/ then parseInt s else s
    console.debug '<', mtype, args

    switch mtype
        when 'newgame'
            [@sid, w, h, player] = args
            @board = new Board w, h
            @board.render document.getElementById 'board'
            location.hash = @sid
            set_this_player player
        when 'join'
            add_other_player args[0]
        when 'leave'
            remove_other_player args[0]
        when 'clickwall'
            [x, y, direction] = args
            @board.click_wall x, y, direction
        when 'occupy'
            [x, y, player] = args
            @board.occupy x, y, player
        when 'turn'
            set_turn_player args[0]
        when 'finish'
            finish (s.split(':').map parseInt for s in args)
        when 'cancel'
            cancel args[0]
        when 'error'
            error = args[0]

            if error == 'no such session'
                @send_msg 'newgame', 5, 6
            else
                show_error error
        else
            show_error 'received invalid message from server'
