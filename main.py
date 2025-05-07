import pygame
import sys
import random
import math
from pygame import gfxdraw

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 600, 700
BOARD_SIZE = 600
LINE_WIDTH = 10
CELL_SIZE = BOARD_SIZE // 3
OFFSET = CELL_SIZE // 4
X_COLOR = (255, 50, 50)    # Красный
O_COLOR = (50, 50, 255)    # Синий
LINE_COLOR = (70, 70, 70)   # Тёмно-серый
BG_COLOR = (240, 240, 240) # Светло-серый
TEXT_COLOR = (50, 50, 50)   # Тёмно-серый
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (180, 180, 180)
ANIMATION_SPEED = 15

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Крестики-нолики с анимацией")
font = pygame.font.SysFont('Arial', 40)
button_font = pygame.font.SysFont('Arial', 30)

# Игровое поле
board = [" "] * 9
current_player = "X"
game_over = False
winner = None

# Анимационные переменные
animating = False
animation_progress = 0
animation_type = ""  # "X" или "O"
animation_pos = (0, 0)  # Позиция анимации (row, col)

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER_COLOR
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, LINE_COLOR, self.rect, 2, border_radius=5)
        
        text_surf = button_font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

# Создаем кнопку
restart_button = Button(WIDTH - 200, BOARD_SIZE + 20, 180, 50, "Новая игра")

def draw_board():
    # Очистка экрана
    screen.fill(BG_COLOR)
    
    # Рисуем игровое поле с закругленными углами
    for i in range(1, 3):
        # Горизонтальные линии
        pygame.draw.line(screen, LINE_COLOR, 
                       (20, i * CELL_SIZE), 
                       (BOARD_SIZE - 20, i * CELL_SIZE), 
                       LINE_WIDTH)
        # Вертикальные линии
        pygame.draw.line(screen, LINE_COLOR, 
                       (i * CELL_SIZE, 20), 
                       (i * CELL_SIZE, BOARD_SIZE - 20), 
                       LINE_WIDTH)
    
    # Рисуем крестики и нолики
    for i in range(9):
        row = i // 3
        col = i % 3
        center_x = col * CELL_SIZE + CELL_SIZE // 2
        center_y = row * CELL_SIZE + CELL_SIZE // 2
        
        if board[i] == "X":
            # Плавное появление крестика
            if animating and animation_type == "X" and (row, col) == animation_pos:
                progress = min(animation_progress / 100, 1.0)
                length = progress * (CELL_SIZE // 2 - OFFSET)
                
                # Первая линия крестика
                angle = math.pi / 4
                x1 = center_x - length * math.cos(angle)
                y1 = center_y - length * math.sin(angle)
                x2 = center_x + length * math.cos(angle)
                y2 = center_y + length * math.sin(angle)
                pygame.draw.line(screen, X_COLOR, (x1, y1), (x2, y2), LINE_WIDTH)
                
                # Вторая линия крестика
                angle = -math.pi / 4
                x1 = center_x - length * math.cos(angle)
                y1 = center_y - length * math.sin(angle)
                x2 = center_x + length * math.cos(angle)
                y2 = center_y + length * math.sin(angle)
                pygame.draw.line(screen, X_COLOR, (x1, y1), (x2, y2), LINE_WIDTH)
            else:
                # Обычный крестик
                pygame.draw.line(screen, X_COLOR, 
                               (col * CELL_SIZE + OFFSET, row * CELL_SIZE + OFFSET),
                               ((col + 1) * CELL_SIZE - OFFSET, (row + 1) * CELL_SIZE - OFFSET), 
                               LINE_WIDTH)
                pygame.draw.line(screen, X_COLOR, 
                               ((col + 1) * CELL_SIZE - OFFSET, row * CELL_SIZE + OFFSET),
                               (col * CELL_SIZE + OFFSET, (row + 1) * CELL_SIZE - OFFSET), 
                               LINE_WIDTH)
        
        elif board[i] == "O":
            # Плавное появление нолика
            if animating and animation_type == "O" and (row, col) == animation_pos:
                progress = min(animation_progress / 100, 1.0)
                radius = progress * (CELL_SIZE // 2 - OFFSET)
                
                # Антиалиасинг для круга
                gfxdraw.aacircle(screen, center_x, center_y, int(radius), O_COLOR)
                gfxdraw.filled_circle(screen, center_x, center_y, int(radius), O_COLOR)
            else:
                # Обычный нолик
                pygame.draw.circle(screen, O_COLOR, 
                                 (center_x, center_y),
                                 CELL_SIZE // 2 - OFFSET, LINE_WIDTH)
    
    # Отображаем текущего игрока
    player_text = font.render(f"Ход: {current_player}", True, TEXT_COLOR)
    screen.blit(player_text, (20, BOARD_SIZE + 20))
    
    # Рисуем кнопку
    restart_button.draw(screen)
    
    # Отображаем результат игры
    if game_over:
        if winner == "Ничья":
            result_text = font.render("Ничья!", True, TEXT_COLOR)
        else:
            result_text = font.render(f"Победил {winner}!", True, TEXT_COLOR)
        screen.blit(result_text, (WIDTH // 2 - 100, BOARD_SIZE + 100))

def check_winner():
    # Проверка строк
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] != " ":
            return board[i]
    
    # Проверка столбцов
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] != " ":
            return board[i]
    
    # Проверка диагоналей
    if board[0] == board[4] == board[8] != " ":
        return board[0]
    if board[2] == board[4] == board[6] != " ":
        return board[2]
    
    # Проверка на ничью
    if " " not in board:
        return "Ничья"
    
    return None

def minimax(board, depth, is_maximizing):
    winner = check_winner()
    
    if winner == "X":
        return -10 + depth
    elif winner == "O":
        return 10 - depth
    elif winner == "Ничья":
        return 0
    
    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if board[i] == " ":
                board[i] = "O"
                score = minimax(board, depth + 1, False)
                board[i] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == " ":
                board[i] = "X"
                score = minimax(board, depth + 1, True)
                board[i] = " "
                best_score = min(score, best_score)
        return best_score

def ai_move():
    best_score = -float('inf')
    best_move = None
    
    for i in range(9):
        if board[i] == " ":
            board[i] = "O"
            score = minimax(board, 0, False)
            board[i] = " "
            if score > best_score:
                best_score = score
                best_move = i
    
    return best_move

def reset_game():
    global board, current_player, game_over, winner
    board = [" "] * 9
    current_player = random.choice(["X", "O"])
    game_over = False
    winner = None
    
    # Если ИИ ходит первым, делаем ход
    if current_player == "O":
        make_ai_move()

def make_move(index, player):
    global animating, animation_progress, animation_type, animation_pos
    
    if board[index] == " " and not animating:
        row, col = index // 3, index % 3
        animating = True
        animation_progress = 0
        animation_type = player
        animation_pos = (row, col)
        board[index] = player
        return True
    return False

def make_ai_move():
    move = ai_move()
    if move is not None:
        make_move(move, "O")

# Основной игровой цикл
clock = pygame.time.Clock()
reset_game()

while True:
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_click = True
    
    # Проверка наведения на кнопку
    restart_button.check_hover(mouse_pos)
    
    if not animating:
        if game_over:
            if restart_button.is_clicked(mouse_pos, mouse_click):
                reset_game()
        else:
            if restart_button.is_clicked(mouse_pos, mouse_click):
                reset_game()
            elif current_player == "X" and mouse_click:
                if mouse_pos[1] < BOARD_SIZE:  # Клик на игровом поле
                    col = mouse_pos[0] // CELL_SIZE
                    row = mouse_pos[1] // CELL_SIZE
                    index = row * 3 + col
                    if make_move(index, "X"):
                        winner = check_winner()
                        if not winner:
                            current_player = "O"
                        else:
                            game_over = True
    
    # Ход ИИ
    if not game_over and not animating and current_player == "O":
        pygame.time.delay(500)  # Задержка перед ходом ИИ
        make_ai_move()
        winner = check_winner()
        if winner:
            game_over = True
        else:
            current_player = "X"
    
    # Обновление анимации
    if animating:
        animation_progress += ANIMATION_SPEED
        if animation_progress >= 100:
            animating = False
            animation_progress = 0
    
    draw_board()
    pygame.display.flip()
    clock.tick(60)