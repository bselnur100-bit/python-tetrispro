import pygame
import random
import json
import os

# --- Инициализация Pygame ---
pygame.init()
pygame.font.init()
pygame.mixer.init()

# --- Константы ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 750  # Чуть увеличил высоту для очереди фигур
GAME_WIDTH = 300
GAME_HEIGHT = 600
BLOCK_SIZE = 30

# Базовые координаты (теперь переменные для эффекта тряски)
BASE_TOP_LEFT_X = (SCREEN_WIDTH - GAME_WIDTH) // 2
BASE_TOP_LEFT_Y = SCREEN_HEIGHT - GAME_HEIGHT - 30

# Цвета
WHITE = (255, 255, 255)
BLACK = (15, 15, 25)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
GRID_COLOR = (40, 40, 60)

# Фигуры
SHAPES = [
    [['..0..', '..0..', '..0..', '..0..', '.....'], ['.....', '0000.', '.....', '.....', '.....']],  # I
    [['.....', '.....', '.00..', '.00..', '.....']],  # O
    [['.....', '..0..', '.000.', '.....', '.....'], ['.....', '..0..', '..00.', '..0..', '.....'],
     ['.....', '.....', '.000.', '..0..', '.....'], ['.....', '..0..', '.00..', '..0..', '.....']],  # T
    [['.....', '..00.', '.00..', '.....', '.....'], ['.....', '..0..', '..00.', '...0.', '.....']],  # S
    [['.....', '.00..', '..00.', '.....', '.....'], ['.....', '..0..', '.00..', '.0...', '.....']],  # Z
    [['.....', '.0...', '.000.', '.....', '.....'], ['.....', '..00.', '..0..', '..0..', '.....'],
     ['.....', '.....', '.000.', '...0.', '.....'], ['.....', '..0..', '..0..', '.00..', '.....']],  # J
    [['.....', '...0.', '.000.', '.....', '.....'], ['.....', '..0..', '..0..', '..00.', '.....'],
     ['.....', '.....', '.000.', '.0...', '.....'], ['.....', '.00..', '..0..', '..0..', '.....']]  # L
]
COLORS = [(0, 255, 255), (255, 255, 0), (128, 0, 128), (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0)]

# Шрифты
FONT_L = pygame.font.SysFont('calibri', 60, bold=True)
FONT_M = pygame.font.SysFont('calibri', 30, bold=True)
FONT_S = pygame.font.SysFont('calibri', 20)

# Глобальные настройки
START_LEVEL = 1
SHOW_GRID = True


# --- Классы ---
class Piece:
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.shape_idx = shape_idx
        self.shape = SHAPES[shape_idx]
        self.color = COLORS[shape_idx]
        self.rotation = 0


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        draw_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, draw_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        text_surf = FONT_M.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, 1)
        self.color = color
        self.lifetime = 255
        self.size = random.randint(3, 7)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # Гравитация
        self.lifetime -= 8

    def draw(self, surface, offset_x, offset_y):
        if self.lifetime > 0:
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*self.color, self.lifetime), surf.get_rect())
            surface.blit(surf, (self.x + offset_x, self.y + offset_y))


# --- Данные (Файлы) ---
def load_records():
    if not os.path.exists("records.json"):
        return [{"name": "Empty", "score": 0} for _ in range(5)]
    with open("records.json", "r") as f:
        return json.load(f)


def save_record(name, score):
    records = load_records()
    records.append({"name": name, "score": score})
    records = sorted(records, key=lambda x: x["score"], reverse=True)[:5]
    with open("records.json", "w") as f:
        json.dump(records, f)


# --- Игровая логика ---
def create_grid(locked_pos={}):
    grid = [[BLACK for _ in range(10)] for _ in range(20)]
    for (x, y), color in locked_pos.items():
        if y >= 0: grid[y][x] = color
    return grid


def convert_shape_format(piece):
    positions = []
    fmt = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(fmt):
        for j, col in enumerate(line):
            if col == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == BLACK] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]
    for pos in convert_shape_format(piece):
        if pos not in accepted_pos:
            if pos[1] > -1: return False
    return True


def get_ghost_y(piece, grid):
    # Создаем дубликат фигуры для просчета падения
    temp_piece = Piece(piece.x, piece.y, piece.shape_idx)
    temp_piece.rotation = piece.rotation  # Важно скопировать угол поворота

    while valid_space(temp_piece, grid):
        temp_piece.y += 1

    return temp_piece.y - 1


def draw_block(surface, x, y, color, alpha=255):
    rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
    if alpha < 255:
        pygame.draw.rect(surface, color, rect, 2, border_radius=4)
    else:
        pygame.draw.rect(surface, color, rect, border_radius=4)
        pygame.draw.rect(surface, (0, 0, 0), rect, 1, border_radius=4)
        highlight = pygame.Rect(x + 4, y + 4, BLOCK_SIZE - 8, 6)
        pygame.draw.rect(surface, (255, 255, 255), highlight, border_radius=2)


def draw_window(surface, grid, score, level, combo, next_pieces, held_piece, particles, shake_offset,
                current_piece=None, ghost_y=0):
    surface.fill(BLACK)

    # Применяем тряску
    off_x, off_y = shake_offset
    TL_X = BASE_TOP_LEFT_X + off_x
    TL_Y = BASE_TOP_LEFT_Y + off_y

    title = FONT_L.render('TETRIS PRO', True, NEON_BLUE)
    surface.blit(title, (BASE_TOP_LEFT_X + GAME_WIDTH // 2 - title.get_width() // 2, 10))

    # Поле
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] != BLACK:
                draw_block(surface, TL_X + j * BLOCK_SIZE, TL_Y + i * BLOCK_SIZE, grid[i][j])

    # Отрисовка призрака (тени)
    if current_piece:
        for x, y in convert_shape_format(current_piece):
            ghost_grid_y = y + (ghost_y - current_piece.y)
            # Рисуем тень только если она в пределах поля
            if ghost_grid_y >= 0:
                draw_block(surface, TL_X + x * BLOCK_SIZE, TL_Y + ghost_grid_y * BLOCK_SIZE, current_piece.color,
                           alpha=100)

    # Частицы
    for p in particles:
        p.draw(surface, off_x, off_y)

    # Сетка и рамка
    if SHOW_GRID:
        for i in range(21):
            pygame.draw.line(surface, GRID_COLOR, (TL_X, TL_Y + i * BLOCK_SIZE),
                             (TL_X + GAME_WIDTH, TL_Y + i * BLOCK_SIZE))
        for j in range(11):
            pygame.draw.line(surface, GRID_COLOR, (TL_X + j * BLOCK_SIZE, TL_Y),
                             (TL_X + j * BLOCK_SIZE, TL_Y + GAME_HEIGHT))
    pygame.draw.rect(surface, NEON_PINK, (TL_X, TL_Y, GAME_WIDTH, GAME_HEIGHT), 3, border_radius=4)

    # UI Справа (Очередь фигур)
    side_x = TL_X + GAME_WIDTH + 40
    surface.blit(FONT_M.render(f'СЧЁТ: {score}', True, WHITE), (side_x, TL_Y))
    surface.blit(FONT_M.render(f'УРОВЕНЬ: {level}', True, (0, 255, 100)), (side_x, TL_Y + 40))
    if combo > 0:
        surface.blit(FONT_S.render(f'КОМБО x{combo}!', True, (255, 215, 0)), (side_x, TL_Y + 80))

    surface.blit(FONT_S.render('СЛЕДУЮЩИЕ:', True, WHITE), (side_x, TL_Y + 120))
    # Отрисовка 3 следующих фигур
    for p_idx, piece in enumerate(next_pieces):
        for i, line in enumerate(piece.shape[0]):
            for j, col in enumerate(line):
                if col == '0':
                    draw_block(surface, side_x + j * BLOCK_SIZE, TL_Y + 160 + i * BLOCK_SIZE + (p_idx * 90),
                               piece.color)

    # UI Слева (Карман)
    hold_x = TL_X - 160
    surface.blit(FONT_S.render('В ЗАПАСЕ (C):', True, WHITE), (hold_x, TL_Y))
    if held_piece:
        for i, line in enumerate(held_piece.shape[0]):
            for j, col in enumerate(line):
                if col == '0':
                    draw_block(surface, hold_x + j * BLOCK_SIZE, TL_Y + 40 + i * BLOCK_SIZE, held_piece.color)


def main_game():
    locked_pos = {}
    grid = create_grid(locked_pos)

    change_piece = False
    run = True
    paused = False

    current_piece = Piece(5, 0, random.randint(0, 6))
    next_pieces = [Piece(5, 0, random.randint(0, 6)) for _ in range(3)]  # Очередь из 3 фигур
    held_piece = None
    can_hold = True
    particles = []

    clock = pygame.time.Clock()
    fall_time = 0
    level = START_LEVEL
    fall_speed = 0.45 - (level * 0.03)
    score = 0
    lines_cleared = 0
    combo = 0
    shake_time = 0

    while run:
        grid = create_grid(locked_pos)

        # Обновление частиц
        for p in particles: p.update()
        particles = [p for p in particles if p.lifetime > 0]

        # Эффект тряски
        shake_offset = (0, 0)
        if shake_time > 0:
            shake_offset = (random.randint(-6, 6), random.randint(-6, 6))
            shake_time -= 1

        if not paused:
            fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > max(0.05, fall_speed) and not paused:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid): current_piece.x += 1
                    if event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid): current_piece.x -= 1
                    if event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid): current_piece.y -= 1
                    if event.key == pygame.K_UP:
                        # Алгоритм Wall Kick (Отталкивание от стен)
                        current_piece.rotation += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1  # Пробуем сдвинуть влево
                            if not valid_space(current_piece, grid):
                                current_piece.x += 2  # Пробуем сдвинуть вправо
                                if not valid_space(current_piece, grid):
                                    current_piece.x -= 1  # Возвращаем X
                                    current_piece.y -= 1  # Пробуем сдвинуть вверх
                                    if not valid_space(current_piece, grid):
                                        current_piece.y += 1  # Возвращаем Y
                                        current_piece.rotation -= 1  # Отменяем поворот (места нет)

                    if event.key == pygame.K_SPACE:
                        while valid_space(current_piece, grid): current_piece.y += 1
                        current_piece.y -= 1
                        change_piece = True
                    if event.key == pygame.K_c and can_hold:
                        if not held_piece:
                            held_piece = Piece(5, 0, current_piece.shape_idx)
                            current_piece = next_pieces.pop(0)
                            next_pieces.append(Piece(5, 0, random.randint(0, 6)))
                        else:
                            temp_idx = current_piece.shape_idx
                            current_piece = Piece(5, 0, held_piece.shape_idx)
                            held_piece = Piece(5, 0, temp_idx)
                        can_hold = False

        ghost_y = current_piece.y
        if not paused:
            # Считаем позицию тени перед отрисовкой сетки
            ghost_y = get_ghost_y(current_piece, grid)

            for x, y in convert_shape_format(current_piece):
                if y >= 0: grid[y][x] = current_piece.color

            if change_piece:
                for x, y in convert_shape_format(current_piece):
                    locked_pos[(x, y)] = current_piece.color
                current_piece = next_pieces.pop(0)
                next_pieces.append(Piece(5, 0, random.randint(0, 6)))
                change_piece = False
                can_hold = True

                cleared_in_turn = 0
                for i in range(len(grid) - 1, -1, -1):
                    if BLACK not in grid[i]:
                        cleared_in_turn += 1
                        for j in range(10):
                            for _ in range(3):
                                p_x = BASE_TOP_LEFT_X + j * BLOCK_SIZE + 15
                                p_y = BASE_TOP_LEFT_Y + i * BLOCK_SIZE + 15
                                particles.append(Particle(p_x, p_y, grid[i][j]))

                        for j in range(len(grid[i])): del locked_pos[(j, i)]
                        new_locked = {}
                        for (x, y), val in locked_pos.items():
                            if y < i:
                                new_locked[(x, y + 1)] = val
                            else:
                                new_locked[(x, y)] = val
                        locked_pos = new_locked

                # Подсчет очков с КОМБО
                if cleared_in_turn > 0:
                    combo += 1
                    base_scores = {1: 100, 2: 300, 3: 500, 4: 1200}
                    score += (base_scores[cleared_in_turn] + 50 * combo) * level
                    lines_cleared += cleared_in_turn

                    if cleared_in_turn == 4:  # Если Тетрис - трясем экран
                        shake_time = 15

                    if lines_cleared >= level * 10:
                        level += 1
                        fall_speed = max(0.05, fall_speed - 0.03)
                else:
                    combo = 0  # Сброс комбо, если фигура упала без очистки линий

        draw_window(win, grid, score, level, combo, next_pieces, held_piece, particles, shake_offset, current_piece,
                    ghost_y)

        if paused:
            pause_text = FONT_L.render("ПАУЗА", True, WHITE)
            win.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        pygame.display.update()

        if any(y < 0 for (x, y) in locked_pos):
            if score > load_records()[-1]["score"]:
                # Простая заглушка сохранения для примера
                save_record("Player", score)
            run = False

    return "MENU"


def settings_menu():
    global START_LEVEL, SHOW_GRID
    run = True
    btn_level_up = Button(SCREEN_WIDTH // 2 + 50, 250, 50, 50, "+", (50, 50, 70), (100, 100, 150))
    btn_level_down = Button(SCREEN_WIDTH // 2 - 100, 250, 50, 50, "-", (50, 50, 70), (100, 100, 150))
    btn_grid = Button(SCREEN_WIDTH // 2 - 100, 350, 200, 50, "Сетка: ВКЛ", (50, 50, 70), (100, 100, 150))
    btn_back = Button(SCREEN_WIDTH // 2 - 100, 500, 200, 50, "НАЗАД", (150, 0, 0), (255, 50, 50))

    while run:
        win.fill(BLACK)
        win.blit(FONT_L.render('НАСТРОЙКИ', True, NEON_BLUE), (SCREEN_WIDTH // 2 - 150, 100))
        win.blit(FONT_M.render(f"Ст. Уровень: {START_LEVEL}", True, WHITE), (SCREEN_WIDTH // 2 - 90, 200))
        btn_grid.text = "Сетка: ВКЛ" if SHOW_GRID else "Сетка: ВЫКЛ"

        for btn in [btn_level_up, btn_level_down, btn_grid, btn_back]:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(win)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.is_hovered: run = False
                if btn_level_up.is_hovered and START_LEVEL < 15: START_LEVEL += 1
                if btn_level_down.is_hovered and START_LEVEL > 1: START_LEVEL -= 1
                if btn_grid.is_hovered: SHOW_GRID = not SHOW_GRID


def records_menu():
    run = True
    btn_back = Button(SCREEN_WIDTH // 2 - 100, 550, 200, 50, "НАЗАД", (150, 0, 0), (255, 50, 50))

    while run:
        win.fill(BLACK)
        win.blit(FONT_L.render('ТОП 5 РЕКОРДОВ', True, (255, 215, 0)), (SCREEN_WIDTH // 2 - 220, 100))
        for i, rec in enumerate(load_records()):
            win.blit(FONT_M.render(f"{i + 1}. {rec['name']} - {rec['score']}", True, WHITE),
                     (SCREEN_WIDTH // 2 - 150, 220 + i * 50))

        btn_back.check_hover(pygame.mouse.get_pos())
        btn_back.draw(win)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            if event.type == pygame.MOUSEBUTTONDOWN and btn_back.is_hovered: run = False


def main_menu():
    run = True
    btn_start = Button(SCREEN_WIDTH // 2 - 125, 250, 250, 60, "ИГРАТЬ", (0, 100, 200), (0, 150, 255))
    btn_settings = Button(SCREEN_WIDTH // 2 - 125, 330, 250, 60, "НАСТРОЙКИ", (50, 50, 70), (100, 100, 150))
    btn_records = Button(SCREEN_WIDTH // 2 - 125, 410, 250, 60, "РЕКОРДЫ", (50, 50, 70), (100, 100, 150))
    btn_exit = Button(SCREEN_WIDTH // 2 - 125, 490, 250, 60, "ВЫХОД", (150, 0, 0), (255, 50, 50))

    while run:
        win.fill(BLACK)
        title = FONT_L.render('PYTHON TETRIS PRO', True, NEON_BLUE)
        win.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        for btn in [btn_start, btn_settings, btn_records, btn_exit]:
            btn.check_hover(pygame.mouse.get_pos())
            btn.draw(win)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_start.is_hovered:
                    if main_game() == "QUIT": run = False
                if btn_settings.is_hovered: settings_menu()
                if btn_records.is_hovered: records_menu()
                if btn_exit.is_hovered: run = False
    pygame.quit()


# --- Запуск ---
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris - Ultimate Esports Edition')
main_menu()
