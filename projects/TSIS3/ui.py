import pygame

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (180, 180, 180)
DARK   = (40,  40,  40)
GREEN  = (0,   200, 80)
RED    = (220, 50,  50)
YELLOW = (255, 220, 0)
BLUE   = (50,  120, 255)

def draw_text(surface, text, size, x, y, color=WHITE, center=True):
    font = pygame.font.SysFont("Arial", size, bold=True)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.centerx = x
        rect.centery = y
    else:
        rect.x = x
        rect.y = y
    surface.blit(rendered, rect)

def draw_button(surface, text, x, y, w, h, color=DARK, text_color=WHITE):
    rect = pygame.Rect(x - w//2, y - h//2, w, h)
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
    draw_text(surface, text, 22, x, y, text_color)
    return rect

def main_menu_screen(surface, width, height):
    surface.fill((20, 20, 40))
    draw_text(surface, "🏎  RACER", 64, width//2, height//4, YELLOW)
    draw_text(surface, "Arcade Racing Game", 22, width//2, height//4 + 60, GRAY)
    btn_play  = draw_button(surface, "▶  Play",        width//2, height//2,       220, 50, GREEN)
    btn_lb    = draw_button(surface, "🏆  Leaderboard", width//2, height//2 + 70,  220, 50)
    btn_set   = draw_button(surface, "⚙  Settings",    width//2, height//2 + 140, 220, 50)
    btn_quit  = draw_button(surface, "✖  Quit",        width//2, height//2 + 210, 220, 50, RED)
    return btn_play, btn_lb, btn_set, btn_quit

def name_entry_screen(surface, width, height, name):
    surface.fill((20, 20, 40))
    draw_text(surface, "Enter Your Name", 40, width//2, height//3, YELLOW)
    draw_text(surface, name + "|", 32, width//2, height//2, WHITE)
    draw_text(surface, "Press ENTER to start", 20, width//2, height//2 + 60, GRAY)

def settings_screen(surface, width, height, settings):
    surface.fill((20, 20, 40))
    draw_text(surface, "Settings", 44, width//2, 70, YELLOW)

    colors = ["red", "blue", "green", "yellow", "white"]
    color_map = {
        "red": (220,50,50), "blue": (50,120,255), "green": (0,200,80),
        "yellow": (255,220,0), "white": (240,240,240)
    }
    difficulties = ["easy", "medium", "hard"]

    sound_label = "Sound: ON" if settings["sound"] else "Sound: OFF"
    btn_sound = draw_button(surface, sound_label, width//2, 170, 220, 48,
                            GREEN if settings["sound"] else RED)

    draw_text(surface, "Car Color:", 22, width//2, 240, GRAY)
    color_buttons = []
    for i, c in enumerate(colors):
        bx = width//2 - 120 + i*60
        rect = pygame.Rect(bx-20, 255, 40, 40)
        pygame.draw.rect(surface, color_map[c], rect, border_radius=6)
        if settings["car_color"] == c:
            pygame.draw.rect(surface, WHITE, rect, 3, border_radius=6)
        color_buttons.append((rect, c))

    draw_text(surface, "Difficulty:", 22, width//2, 320, GRAY)
    diff_buttons = []
    for i, d in enumerate(difficulties):
        bx = width//2 - 120 + i*120
        col = GREEN if settings["difficulty"] == d else DARK
        r = draw_button(surface, d.capitalize(), bx, 355, 100, 40, col)
        diff_buttons.append((r, d))

    btn_back = draw_button(surface, "← Back", width//2, 430, 180, 46)
    return btn_sound, color_buttons, diff_buttons, btn_back

def leaderboard_screen(surface, width, height, leaderboard):
    surface.fill((20, 20, 40))
    draw_text(surface, "🏆 Leaderboard", 44, width//2, 60, YELLOW)
    if not leaderboard:
        draw_text(surface, "No scores yet!", 26, width//2, height//2, GRAY)
    else:
        draw_text(surface, f"{'#':<4}{'Name':<16}{'Score':>8}{'Distance':>10}", 20,
                  width//2, 120, GRAY, center=False)
        for i, entry in enumerate(leaderboard[:10]):
            y = 155 + i * 32
            line = f"{i+1:<4}{entry['name']:<16}{entry['score']:>8}{entry['distance']:>9}m"
            color = YELLOW if i == 0 else WHITE
            draw_text(surface, line, 20, 60, y, color, center=False)
    btn_back = draw_button(surface, "← Back", width//2, height - 60, 180, 46)
    return btn_back

def game_over_screen(surface, width, height, score, distance, coins):
    surface.fill((20, 20, 40))
    draw_text(surface, "GAME OVER", 52, width//2, height//4, RED)
    draw_text(surface, f"Score:    {score}",    26, width//2, height//4 + 80,  WHITE)
    draw_text(surface, f"Distance: {int(distance)}m", 26, width//2, height//4 + 120, WHITE)
    draw_text(surface, f"Coins:    {coins}",    26, width//2, height//4 + 160, YELLOW)
    btn_retry = draw_button(surface, "↺  Retry",      width//2, height//4 + 240, 200, 50, GREEN)
    btn_menu  = draw_button(surface, "⌂  Main Menu",  width//2, height//4 + 305, 200, 50)
    return btn_retry, btn_menu