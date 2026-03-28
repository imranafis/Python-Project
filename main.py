import pygame
import random

pygame.init()

CELL = 40
COLS = 10
ROWS = 20
WIDTH  = COLS * CELL
HEIGHT = ROWS * CELL
screen = pygame.display.set_mode((WIDTH + 200, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22, bold=True)

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (40,  40,  40)
RED    = (240, 0,   0)

SHAPES = {
    'I': [
            [(0,0),(0,1),(0,2),(0,3)],
            [(0,0),(1,0),(2,0),(3,0)],
            [(0,0),(0,1),(0,2),(0,3)],
            [(0,0),(1,0),(2,0),(3,0)]
        ],

    'O': [
            [(0,0),(0,1),(1,0),(1,1)],
            [(0,0),(0,1),(1,0),(1,1)],
            [(0,0),(0,1),(1,0),(1,1)],
            [(0,0),(0,1),(1,0),(1,1)]
        ],

    'T': [
            [(0,1),(1,0),(1,1),(1,2)],
            [(0,0),(1,0),(1,1),(2,0)],
            [(1,0),(1,1),(1,2),(2,1)],
            [(0,1),(1,0),(1,1),(2,1)]
        ],

    'S': [
            [(0,1),(0,2),(1,0),(1,1)],
            [(0,0),(1,0),(1,1),(2,1)],
            [(0,1),(0,2),(1,0),(1,1)],
            [(0,0),(1,0),(1,1),(2,1)]
        ],

    'Z': [
            [(0,0),(0,1),(1,1),(1,2)],
            [(0,1),(1,0),(1,1),(2,0)],
            [(0,0),(0,1),(1,1),(1,2)],
            [(0,1),(1,0),(1,1),(2,0)]
        ],

    'J': [
            [(0,0),(1,0),(1,1),(1,2)],
            [(0,0),(0,1),(1,0),(2,0)],
            [(1,0),(1,1),(1,2),(2,2)],
            [(0,1),(1,1),(2,0),(2,1)]
        ],

    'L': [
            [(0,2),(1,0),(1,1),(1,2)],
            [(0,0),(1,0),(2,0),(2,1)],
            [(1,0),(1,1),(1,2),(2,0)],
            [(0,0),(0,1),(1,1),(2,1)]
        ],
}

COLORS = {
            'I': (0,240,240),
            'O': (240,240,0),
            'T': (160,0,240),
            'S': (0,240,0),
            'Z': (240,0,0),
            'J': (0,0,240),
            'L': (240,160,0),
}

def new_block():
    shape = random.choice(list(SHAPES.keys()))
    return {'shape': shape, 'color': COLORS[shape], 'rot': 0, 'row': 0, 'col': COLS // 2 - 2}

def get_blocks(block, row=None, col=None, rot=None):
    r   = block['row'] if row is None else row
    c   = block['col'] if col is None else col
    rot = block['rot'] if rot is None else rot
    return [(r + dr, c + dc) for dr, dc in SHAPES[block['shape']][rot]]

def is_valid(board, blocks):
    for r, c in blocks:
        if c < 0 or c >= COLS or r >= ROWS:
            return False
        if r >= 0 and board[r][c] is not None:
            return False
    return True

def lock_block(board, block):
    for r, c in get_blocks(block):
        if r >= 0:
            board[r][c] = block['color']

def clear_lines(board):
    new_board = [row for row in board if any(cell is None for cell in row)]
    cleared   = ROWS - len(new_board)
    new_board = [[None] * COLS for _ in range(cleared)] + new_board
    return new_board, cleared

def spawn_next(board, next_block):
    block      = next_block
    next_block = new_block()
    game_over  = not is_valid(board, get_blocks(block))
    return block, next_block, game_over

def after_lock(board, block, next_block, score, lines, level, fall_speed):
    lock_block(board, block)
    board, cleared = clear_lines(board)
    score     += [0, 100, 300, 500, 800][cleared] * level
    lines     += cleared
    level      = lines // 10 + 1
    fall_speed = max(80, 500 - (level - 1) * 40)
    block, next_block, game_over = spawn_next(board, next_block)
    return board, block, next_block, score, lines, level, fall_speed, game_over

def draw_block(surface, r, c, color, alpha=255):
    x, y = c * CELL, r * CELL
    if alpha < 255:
        s = pygame.Surface((CELL-2, CELL-2), pygame.SRCALPHA)
        s.fill((*color, alpha))
        surface.blit(s, (x+1, y+1))
    else:
        pygame.draw.rect(surface, color, (x+1, y+1, CELL-2, CELL-2), border_radius=3)
        lighter = tuple(min(v+60, 255) for v in color)
        pygame.draw.rect(surface, lighter, (x+1, y+1, CELL-2, 4))

def draw_board(board, block, next_block, score, level, lines, game_over):
    screen.fill((20, 20, 20))

    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen, GRAY, (c*CELL+1, r*CELL+1, CELL-2, CELL-2), border_radius=2)

    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]:
                draw_block(screen, r, c, board[r][c])

    if not game_over:
        for r, c in get_blocks(block):
            if r >= 0:
                draw_block(screen, r, c, block['color'])

    px = WIDTH + 10
    small = pygame.font.SysFont(None, 25)
    screen.blit(font.render("SCORE", True, WHITE),         (px, 20))
    screen.blit(font.render(str(score), True, (0,240,240)),(px, 45))
    screen.blit(font.render("LEVEL", True, WHITE),         (px, 100))
    screen.blit(font.render(str(level), True, (240,160,0)),(px, 125))
    screen.blit(font.render("LINES", True, WHITE),         (px, 180))
    screen.blit(font.render(str(lines), True, (0,240,0)),  (px, 205))

    screen.blit(font.render("NEXT", True, WHITE), (px, 265))
    for dr, dc in SHAPES[next_block['shape']][0]:
        pygame.draw.rect(screen, next_block['color'],
                         (px + dc*CELL+1, 295 + dr*CELL+1, CELL-2, CELL-2), border_radius=3)

    for i, tip in enumerate([" ^  Rotate", "< > Move", " v  Fast", "Space Drop", "R Restart"]):
        screen.blit(small.render(tip, True, (140,140,140)), (px, 420 + i*50))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        screen.blit(font.render("GAME  OVER",        True, RED),   (WIDTH / 2, HEIGHT / 2))
        screen.blit(font.render("Press R to restart", True, WHITE), (WIDTH / 2 - 40, HEIGHT / 2 + 30))

    pygame.display.flip()

def main():
    board      = [[None] * COLS for _ in range(ROWS)]
    block      = new_block()
    next_block = new_block()
    score      = 0
    level      = 1
    lines      = 0
    fall_speed = 500
    last_fall  = pygame.time.get_ticks()
    fast_fall  = False
    game_over  = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main(); return

                if game_over:
                    continue

                if event.key == pygame.K_LEFT:
                    if is_valid(board, get_blocks(block, col=block['col']-1)):
                        block['col'] -= 1

                elif event.key == pygame.K_RIGHT:
                    if is_valid(board, get_blocks(block, col = block['col']+1)):
                        block['col'] += 1

                elif event.key == pygame.K_UP:
                    new_rot = (block['rot'] + 1) % 4
                    if is_valid(board, get_blocks(block, rot = new_rot)):
                        block['rot'] = new_rot
                    elif is_valid(board, get_blocks(block, col = block['col']+1, rot=new_rot)):
                        block['col'] += 1; block['rot'] = new_rot
                    elif is_valid(board, get_blocks(block, col = block['col']-1, rot=new_rot)):
                        block['col'] -= 1; block['rot'] = new_rot

                elif event.key == pygame.K_SPACE:
                    while is_valid(board, get_blocks(block, row = block['row']+1)):
                        block['row'] += 1
                    board, block, next_block, score, lines, level, fall_speed, game_over = \
                     after_lock(board, block, next_block, score, lines, level, fall_speed)

                elif event.key == pygame.K_DOWN:
                    fast_fall = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    fast_fall = False

        if not game_over:
            now   = pygame.time.get_ticks()
            speed = 60 if fast_fall else fall_speed
            if now - last_fall > speed:
                last_fall = now
                if is_valid(board, get_blocks(block, row=block['row']+1)):
                    block['row'] += 1
                else:
                    board, block, next_block, score, lines, level, fall_speed, game_over = \
                        after_lock(board, block, next_block, score, lines, level, fall_speed)

        draw_board(board, block, next_block, score, level, lines, game_over)
        clock.tick(60)

if __name__ == "__main__":
    main()