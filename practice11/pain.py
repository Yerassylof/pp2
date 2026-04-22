import pygame, sys

pygame.init()

# Экран параметрлері
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Extended with Shapes and Color Buttons")

# Түстер
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

current_color = BLACK   # бастапқы түс
tool = "brush"          # бастапқы құрал

clock = pygame.time.Clock()
drawing = False
start_pos = None

# Түстер батырмалары (төменгі жағында)
color_buttons = {
    "black": pygame.Rect(10, HEIGHT-40, 30, 30),
    "red":   pygame.Rect(50, HEIGHT-40, 30, 30),
    "green": pygame.Rect(90, HEIGHT-40, 30, 30),
    "blue":  pygame.Rect(130, HEIGHT-40, 30, 30),
}

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Тышқан басу
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Егер батырмаға басылса – түс таңдау
            for name, rect in color_buttons.items():
                if rect.collidepoint(event.pos):
                    if name == "black": current_color = BLACK
                    elif name == "red": current_color = RED
                    elif name == "green": current_color = GREEN
                    elif name == "blue": current_color = BLUE
                    break
            else:
                drawing = True
                start_pos = event.pos

        # Тышқанды босату
        if event.type == pygame.MOUSEBUTTONUP:
            end_pos = event.pos
            if tool == "rect":
                rect = pygame.Rect(start_pos, (end_pos[0]-start_pos[0], end_pos[1]-start_pos[1]))
                pygame.draw.rect(screen, current_color, rect, 2)
            elif tool == "square":
                side = min(abs(end_pos[0]-start_pos[0]), abs(end_pos[1]-start_pos[1]))
                rect = pygame.Rect(start_pos[0], start_pos[1], side, side)
                pygame.draw.rect(screen, current_color, rect, 2)
            elif tool == "right_triangle":
                points = [start_pos, (end_pos[0], start_pos[1]), end_pos]
                pygame.draw.polygon(screen, current_color, points, 2)
            elif tool == "equilateral_triangle":
                side = abs(end_pos[0]-start_pos[0])
                height = int((3**0.5/2)*side)
                points = [
                    (start_pos[0], start_pos[1]),
                    (start_pos[0]+side, start_pos[1]),
                    (start_pos[0]+side//2, start_pos[1]-height)
                ]
                pygame.draw.polygon(screen, current_color, points, 2)
            elif tool == "rhombus":
                dx = end_pos[0]-start_pos[0]
                dy = end_pos[1]-start_pos[1]
                points = [
                    (start_pos[0], start_pos[1]-dy//2),
                    (start_pos[0]+dx//2, start_pos[1]),
                    (start_pos[0], start_pos[1]+dy//2),
                    (start_pos[0]-dx//2, start_pos[1])
                ]
                pygame.draw.polygon(screen, current_color, points, 2)
            drawing = False

        # Пернетақта арқылы құрал таңдау
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b: tool = "brush"
            elif event.key == pygame.K_r: tool = "rect"
            elif event.key == pygame.K_s: tool = "square"
            elif event.key == pygame.K_t: tool = "right_triangle"
            elif event.key == pygame.K_e: tool = "equilateral_triangle"
            elif event.key == pygame.K_h: tool = "rhombus"

    # Brush
    if drawing and tool == "brush":
        pygame.draw.circle(screen, current_color, pygame.mouse.get_pos(), 5)

    # Түстер батырмаларын салу
    pygame.draw.rect(screen, BLACK, color_buttons["black"])
    pygame.draw.rect(screen, RED, color_buttons["red"])
    pygame.draw.rect(screen, GREEN, color_buttons["green"])
    pygame.draw.rect(screen, BLUE, color_buttons["blue"])

    pygame.display.update()
    clock.tick(60)


    pygame.display.update()
    clock.tick(60)