import pygame, sys
from tools import pencil_tool, line_preview, flood_fill, save_canvas

pygame.init()

# ── Screen & canvas setup ──────────────────────────────────────────────────
WIDTH, HEIGHT  = 900, 650
TOOLBAR_HEIGHT = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Extended — TSIS 2")

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()

# ── Colors ─────────────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)
GREEN  = (0,   255, 0)
BLUE   = (0,   0,   255)
YELLOW = (255, 255, 0)
GRAY   = (200, 200, 200)
DKGRAY = (100, 100, 100)

current_color = BLACK

# ── Brush sizes ────────────────────────────────────────────────────────────
BRUSH_SIZES = {1: 2, 2: 5, 3: 10}
brush_size  = 2

# ── Tools ──────────────────────────────────────────────────────────────────
# b=pencil, l=line, r=rect, c=circle, s=square,
# t=right_triangle, e=equilateral_triangle, h=rhombus,
# f=fill, x=eraser, F2=text
tool = "pencil"

# ── Drawing state ──────────────────────────────────────────────────────────
drawing         = False
start_pos       = None
prev_pos        = None
canvas_snapshot = None

# ── Text tool state ────────────────────────────────────────────────────────
text_mode  = False
text_pos   = None
typed_text = ""
text_font  = pygame.font.SysFont("Arial", 24)

# ── HUD font ───────────────────────────────────────────────────────────────
hud_font = pygame.font.SysFont("Arial", 16)

# ── Toolbar color buttons ──────────────────────────────────────────────────
color_buttons = {
    "black":  (pygame.Rect(10,  HEIGHT - 40, 28, 28), BLACK),
    "red":    (pygame.Rect(45,  HEIGHT - 40, 28, 28), RED),
    "green":  (pygame.Rect(80,  HEIGHT - 40, 28, 28), GREEN),
    "blue":   (pygame.Rect(115, HEIGHT - 40, 28, 28), BLUE),
    "yellow": (pygame.Rect(150, HEIGHT - 40, 28, 28), YELLOW),
    "white":  (pygame.Rect(185, HEIGHT - 40, 28, 28), WHITE),
}

# ── Toolbar brush-size buttons ─────────────────────────────────────────────
size_buttons = {
    1: pygame.Rect(240, HEIGHT - 40, 28, 28),
    2: pygame.Rect(275, HEIGHT - 40, 28, 28),
    3: pygame.Rect(310, HEIGHT - 40, 28, 28),
}

# ── Helper functions ───────────────────────────────────────────────────────
def to_canvas(pos):
    return (pos[0], pos[1])

def on_canvas(pos):
    return pos[1] < HEIGHT - TOOLBAR_HEIGHT

def draw_shape(surface, tool_name, start, end, color, size):
    if tool_name == "rect":
        rect = pygame.Rect(start, (end[0]-start[0], end[1]-start[1]))
        pygame.draw.rect(surface, color, rect, size)

    elif tool_name == "circle":
        cx = (start[0] + end[0]) // 2
        cy = (start[1] + end[1]) // 2
        r  = max(abs(end[0]-start[0])//2, abs(end[1]-start[1])//2)
        pygame.draw.circle(surface, color, (cx, cy), r, size)

    elif tool_name == "square":
        side = min(abs(end[0]-start[0]), abs(end[1]-start[1]))
        pygame.draw.rect(surface, color, pygame.Rect(start[0], start[1], side, side), size)

    elif tool_name == "right_triangle":
        points = [start, (end[0], start[1]), end]
        pygame.draw.polygon(surface, color, points, size)

    elif tool_name == "equilateral_triangle":
        side   = abs(end[0] - start[0])
        height = int((3 ** 0.5 / 2) * side)
        points = [
            (start[0],           start[1]),
            (start[0] + side,    start[1]),
            (start[0] + side//2, start[1] - height)
        ]
        pygame.draw.polygon(surface, color, points, size)

    elif tool_name == "rhombus":
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        points = [
            (start[0],           start[1] - dy//2),
            (start[0] + dx//2,   start[1]),
            (start[0],           start[1] + dy//2),
            (start[0] - dx//2,   start[1])
        ]
        pygame.draw.polygon(surface, color, points, size)

    elif tool_name == "line":
        pygame.draw.line(surface, color, start, end, size)


# ── Main loop ──────────────────────────────────────────────────────────────
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ── Keyboard ──────────────────────────────────────────────────────
        if event.type == pygame.KEYDOWN:

            if text_mode:
                # ── Text mode: capture typing ──────────────────────────────
                if event.key == pygame.K_RETURN:
                    # Confirm — render text permanently
                    text_surf = text_font.render(typed_text, True, current_color)
                    canvas.blit(text_surf, text_pos)
                    text_mode  = False
                    typed_text = ""
                    text_pos   = None

                elif event.key == pygame.K_ESCAPE:
                    # FIX: ESC exits text mode back to normal tools
                    text_mode  = False
                    typed_text = ""
                    text_pos   = None
                    tool       = "pencil"   # return to pencil after exiting text

                elif event.key == pygame.K_BACKSPACE:
                    typed_text = typed_text[:-1]

                else:
                    if event.unicode:
                        typed_text += event.unicode

            else:
                # ── Normal mode: tool shortcuts ────────────────────────────
                if   event.key == pygame.K_b: tool = "pencil"
                elif event.key == pygame.K_l: tool = "line"
                elif event.key == pygame.K_r: tool = "rect"
                elif event.key == pygame.K_c: tool = "circle"
                elif event.key == pygame.K_s: tool = "square"
                elif event.key == pygame.K_t: tool = "right_triangle"
                elif event.key == pygame.K_e: tool = "equilateral_triangle"
                elif event.key == pygame.K_h: tool = "rhombus"
                elif event.key == pygame.K_f: tool = "fill"
                elif event.key == pygame.K_x: tool = "eraser"

                # FIX: text tool on F2 — no conflict with other keys
                elif event.key == pygame.K_F2:
                    tool = "text"

                # Brush sizes
                elif event.key == pygame.K_1: brush_size = BRUSH_SIZES[1]
                elif event.key == pygame.K_2: brush_size = BRUSH_SIZES[2]
                elif event.key == pygame.K_3: brush_size = BRUSH_SIZES[3]

                # Ctrl+S: save
                elif (event.key == pygame.K_s and
                      pygame.key.get_mods() & pygame.KMOD_CTRL):
                    save_canvas(canvas)

        # ── Mouse button DOWN ──────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            for name, (rect, color) in color_buttons.items():
                if rect.collidepoint(pos):
                    current_color = color
                    break

            for num, rect in size_buttons.items():
                if rect.collidepoint(pos):
                    brush_size = BRUSH_SIZES[num]
                    break

            if on_canvas(pos):
                canvas_pos = to_canvas(pos)

                if tool == "fill":
                    flood_fill(canvas, canvas_pos, current_color)

                elif tool == "text":
                    # Click sets cursor position and starts typing
                    text_mode  = True
                    text_pos   = canvas_pos
                    typed_text = ""

                elif tool in ("eraser", "pencil"):
                    drawing  = True
                    prev_pos = canvas_pos

                elif tool == "line":
                    drawing         = True
                    start_pos       = canvas_pos
                    canvas_snapshot = canvas.copy()

                else:
                    drawing   = True
                    start_pos = canvas_pos

        # ── Mouse button UP ────────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONUP:
            if drawing and on_canvas(event.pos):
                end_pos    = to_canvas(event.pos)
                draw_color = WHITE if tool == "eraser" else current_color
                draw_sz    = brush_size * 5 if tool == "eraser" else brush_size

                if tool == "line":
                    canvas.blit(canvas_snapshot, (0, 0))
                    pygame.draw.line(canvas, current_color, start_pos, end_pos, brush_size)

                elif tool not in ("pencil", "eraser", "fill", "text"):
                    draw_shape(canvas, tool, start_pos, end_pos, draw_color, brush_size)

            drawing         = False
            start_pos       = None
            prev_pos        = None
            canvas_snapshot = None

    # ── Continuous drawing ─────────────────────────────────────────────────
    if drawing and tool in ("pencil", "eraser"):
        curr_pos   = to_canvas(pygame.mouse.get_pos())
        draw_color = WHITE if tool == "eraser" else current_color
        draw_sz    = brush_size * 5 if tool == "eraser" else brush_size
        pencil_tool(canvas, prev_pos, curr_pos, draw_color, draw_sz)
        prev_pos = curr_pos

    # ── Live line preview ──────────────────────────────────────────────────
    if drawing and tool == "line" and canvas_snapshot:
        canvas.blit(canvas_snapshot, (0, 0))
        curr_pos = to_canvas(pygame.mouse.get_pos())
        line_preview(canvas, start_pos, curr_pos, current_color, brush_size)

    # ── Blit canvas ────────────────────────────────────────────────────────
    screen.blit(canvas, (0, 0))

    # ── Toolbar ────────────────────────────────────────────────────────────
    pygame.draw.rect(screen, GRAY, (0, HEIGHT - TOOLBAR_HEIGHT, WIDTH, TOOLBAR_HEIGHT))

    for name, (rect, color) in color_buttons.items():
        pygame.draw.rect(screen, color, rect)
        if color == current_color:
            pygame.draw.rect(screen, DKGRAY, rect, 3)

    for num, rect in size_buttons.items():
        pygame.draw.rect(screen, DKGRAY, rect, 2)
        pygame.draw.circle(screen, BLACK, rect.center, BRUSH_SIZES[num])
        if BRUSH_SIZES[num] == brush_size:
            pygame.draw.rect(screen, RED, rect, 3)

    # ── HUD ────────────────────────────────────────────────────────────────
    if text_mode:
        # Show different hint when in text mode
        hud = hud_font.render(
            f"TEXT MODE — type text, ENTER=confirm, ESC=cancel", True, RED)
    else:
        hud = hud_font.render(
            f"Tool: {tool}  |  Size: {brush_size}px  |  F2=text  Ctrl+S=save", True, BLACK)
    screen.blit(hud, (355, HEIGHT - 32))

    # ── Text preview ───────────────────────────────────────────────────────
    if text_mode and text_pos:
        preview_surf = text_font.render(typed_text + "|", True, current_color)
        screen.blit(preview_surf, text_pos)

    pygame.display.update()
    clock.tick(60)