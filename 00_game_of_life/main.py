from fasthtml.common import *
import asyncio
import sys

import math
# UTCTF 2025 https://ctftime.org/event/2641
#  Streamified
#
# Apparently I'm supposed to scan this or something... but I don't really get it.
secret = "1111111000011110101111111100000100110101100100000110111010110110111010111011011101010101001101011101101110101001010010101110110000010100101111010000011111111010101010101111111000000001011110100000000010111110001110110011111000111010101100000010100000100011110111100101110111100000100001010100010000011000001000000001011011111100010001010111011100011010100010101001111100110111011100001001100110000011100001100110101011111111100000000110000001000110101111111001111001101010011100000101101001010001000010111010111100011111111011011101011001110011010011101110101010011110010010110000010011011001011100011111111010101010000010111"
step = math.isqrt(len(secret))
if __name__ == "__main__": sys.exit("Run this app with `uvicorn main:app`")

css = Style('''
    body, html { height: 100%; margin: 0; }
    body { display: flex; flex-direction: column; background-color: #f4ecd8}
    main { flex: 1 0 auto; }
    footer { flex-shrink: 0; padding: 10px; text-align: center; background-color: #333; color: white; }
    footer a { color: #9cf; }
    #grid { display: grid; grid-template-columns: repeat(20, 20px); grid-template-rows: repeat(20, 20px);gap: 0px; }
    .cell { width: 20px; height: 20px; border: 0px solid black; }
    .alive { background-color: black; }
    .dead { background-color: white; }
'''.replace("repeat(20", f"repeat({step}"))

gridlink = Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css", type="text/css")
htmx_ws = Script(src="https://unpkg.com/htmx-ext-ws@2.0.0/ws.js")
app = FastHTML(hdrs=(picolink, gridlink, css, htmx_ws))
rt = app.route

init_grid = [[int(c) for c in secret[i:i+step]] for i in range(0, len(secret), step)]

game_state = {'running': False, 'grid': init_grid}

def update_grid(grid: list[list[int]]) -> list[list[int]]:
    new_grid = [[0 for _ in range(step)] for _ in range(step)]
    def count_neighbors(x, y):
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        count = 0
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]): count += grid[nx][ny]
        return count
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            neighbors = count_neighbors(i, j)
            if grid[i][j] == 1:
                if neighbors < 2 or neighbors > 3: new_grid[i][j] = 0
                else: new_grid[i][j] = 1
            elif neighbors == 3: new_grid[i][j] = 1
    return new_grid

def Grid():
    cells = []
    for y, row in enumerate(game_state['grid']):
        for x, cell in enumerate(row):
            cell_class = 'alive' if cell else 'dead'
            cell = Div(cls=f'cell {cell_class}', hx_put='/update', hx_vals={'x': x, 'y': y}, hx_swap='none', hx_target='#gol', hx_trigger='click')
            cells.append(cell)
    return Div(*cells, id='grid')

def Home():
    gol = Div(Grid(), id='gol', cls='row center-xs')
    run_btn = Button('Run', id='run', cls='col-xs-2', hx_put='/run', hx_target='#gol', hx_swap='none')
    pause_btn = Button('Pause', id='pause', cls='col-xs-2', hx_put='/pause', hx_target='#gol', hx_swap='none')
    reset_btn = Button('Reset', id='reset', cls='col-xs-2', hx_put='/reset', hx_target='#gol', hx_swap='none')
    main = Main(gol, Div(P("")), Div(run_btn, pause_btn, reset_btn, cls='row center-xs'), hx_ext="ws", ws_connect="/gol")
    footer = Footer(P('Made by Nathan Cooper. Check out the code', AX('here', href='https://github.com/AnswerDotAI/fasthtml-example/tree/main/game_of_life', target='_blank')))
    return Title('Game of Life'), main, footer

@rt('/')
def get(): return Home()

player_queue = []
async def update_players():
    for i, player in enumerate(player_queue):
        try: await player(Grid())
        except: player_queue.pop(i)
async def on_connect(send): player_queue.append(send)
async def on_disconnect(send): await update_players()

@app.ws('/gol', conn=on_connect, disconn=on_disconnect)
async def ws(msg:str, send): pass

async def background_task():
    while True:
        if game_state['running'] and len(player_queue) > 0:
            game_state['grid'] = update_grid(game_state['grid'])
            await update_players()
        await asyncio.sleep(1.0)

background_task_coroutine = asyncio.create_task(background_task())

@rt('/update')
async def put(x: int, y: int):
    game_state['grid'][y][x] = 1 if game_state['grid'][y][x] == 0 else 0
    await update_players()

@rt('/run')
async def put():
    game_state['running'] = True
    await update_players()

@rt("/reset")
async def put():
    game_state['grid'] = init_grid
    game_state['running'] = False
    await update_players()

@rt('/pause')
async def put():
    game_state['running'] = False
    await update_players()
