import pygame
import sys
from config import *
from game   import (SnakeGame, load_settings, save_settings,
                    screen_menu, screen_gameover, screen_leaderboard,
                    screen_settings, draw_button,
                    init_sounds, play_menu_music, stop_music)
from db     import init_db, save_session, get_leaderboard, get_personal_best

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🐍 Snake DB")

    # Init sounds after mixer is ready
    init_sounds()

    try:
        init_db()
        db_ok = True
    except Exception as e:
        print(f"DB error: {e}")
        db_ok = False

    settings   = load_settings()
    # FIX: ensure all keys exist with defaults
    settings.setdefault("snake_color", [0, 200, 80])
    settings.setdefault("grid",        True)
    settings.setdefault("sound",       False)

    state    = "menu"
    username = ""
    game     = None
    pb       = 0
    lb_rows  = []
    clock    = pygame.time.Clock()
    prev_state = None

    while True:
        mouse = pygame.mouse.get_pos()

        # Switch music when state changes
        if state != prev_state:
            if state == "menu":
                if settings["sound"]:
                    play_menu_music()
            elif state == "game":
                stop_music()
            elif state == "game_over":
                stop_music()
            prev_state = state

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── MENU ──────────────────────────────────────────────────────────
            if state == "menu":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.unicode.isprintable() and len(username) < 16:
                        username += event.unicode

                if event.type == pygame.MOUSEBUTTONDOWN:
                    bp, blb, bst, bq = screen_menu(screen, username)
                    if bp.collidepoint(mouse) and username.strip():
                        pb    = get_personal_best(username.strip()) if db_ok else 0
                        game  = SnakeGame(settings, username.strip(), pb, screen)
                        state = "game"
                    elif blb.collidepoint(mouse):
                        lb_rows = get_leaderboard() if db_ok else []
                        state   = "leaderboard"
                    elif bst.collidepoint(mouse):
                        state = "settings"
                    elif bq.collidepoint(mouse):
                        pygame.quit(); sys.exit()

            # ── SETTINGS ──────────────────────────────────────────────────────
            elif state == "settings":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    bg, bs, cbtns, bb = screen_settings(screen, settings)
                    if bg.collidepoint(mouse):
                        settings["grid"] = not settings["grid"]
                    elif bs.collidepoint(mouse):
                        settings["sound"] = not settings["sound"]
                        # FIX: actually toggle music when button pressed
                        if settings["sound"]:
                            play_menu_music()
                        else:
                            stop_music()
                    for rect, rgb in cbtns:
                        if rect.collidepoint(mouse):
                            settings["snake_color"] = rgb
                    if bb.collidepoint(mouse):
                        save_settings(settings)
                        state = "menu"

            # ── LEADERBOARD ───────────────────────────────────────────────────
            elif state == "leaderboard":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    bb = screen_leaderboard(screen, lb_rows)
                    if bb.collidepoint(mouse):
                        state = "menu"

            # ── GAME OVER ─────────────────────────────────────────────────────
            elif state == "game_over":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    br, bm = screen_gameover(screen, game.score, game.level, pb)
                    if br.collidepoint(mouse):
                        game  = SnakeGame(settings, username.strip(), pb, screen)
                        state = "game"
                    elif bm.collidepoint(mouse):
                        state = "menu"

            # ── GAME input ────────────────────────────────────────────────────
            elif state == "game" and event.type == pygame.KEYDOWN:
                d = game.dir
                if event.key in (pygame.K_UP,    pygame.K_w) and d != (0,  1):
                    game.next_dir = (0, -1)
                elif event.key in (pygame.K_DOWN,  pygame.K_s) and d != (0, -1):
                    game.next_dir = (0,  1)
                elif event.key in (pygame.K_LEFT,  pygame.K_a) and d != (1,  0):
                    game.next_dir = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and d != (-1, 0):
                    game.next_dir = (1,  0)

        # ── per-frame ─────────────────────────────────────────────────────────
        if state == "menu":
            screen_menu(screen, username)

        elif state == "settings":
            screen_settings(screen, settings)

        elif state == "leaderboard":
            screen_leaderboard(screen, lb_rows)

        elif state == "game_over":
            screen_gameover(screen, game.score, game.level, pb)

        elif state == "game":
            if game.alive:
                game.update()
                game.draw()
            else:
                if db_ok:
                    save_session(username.strip(), game.score, game.level)
                    pb = get_personal_best(username.strip())
                state = "game_over"

        pygame.display.flip()
        clock.tick(game.get_speed() if state == "game" and game else FPS)

if __name__ == "__main__":
    main()