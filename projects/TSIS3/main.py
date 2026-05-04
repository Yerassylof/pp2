import pygame
import sys
import numpy as np

from racer       import Game
from ui          import (main_menu_screen, name_entry_screen, settings_screen,
                         leaderboard_screen, game_over_screen)
from persistence import load_settings, save_settings, load_leaderboard, save_score

WIDTH, HEIGHT = 400, 600
FPS = 60

def _gen_menu_music():
    """Short pleasant 'ding' chord — plays once at startup only."""
    try:
        sr  = 44100
        dur = 0.8
        t   = np.linspace(0, dur, int(sr * dur), False)
        w   = (np.sin(2*np.pi*523.0*t) * 0.4 +
               np.sin(2*np.pi*659.0*t) * 0.3 +
               np.sin(2*np.pi*784.0*t) * 0.2)
        envelope = np.exp(-4 * t)
        w *= envelope
        stereo = np.column_stack([(w * 32767).astype(np.int16)] * 2)
        return pygame.sndarray.make_sound(stereo)
    except Exception as e:
        print(f"Menu music error: {e}")
        return None

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    from racer import init_sounds
    init_sounds()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🏎 Racer")
    clock  = pygame.time.Clock()

    settings = load_settings()
    settings.setdefault("car_color",  "red")
    settings.setdefault("sound",      True)
    settings.setdefault("difficulty", "medium")

    _menu_music       = _gen_menu_music()
    _music_ch         = pygame.mixer.Channel(2)
    # FIX: флаг — звук играет только один раз за всю сессию
    _menu_played_once = False

    def start_menu_music():
        nonlocal _menu_played_once
        if settings["sound"] and _menu_music and not _menu_played_once:
            _music_ch.play(_menu_music, loops=0)
            _menu_played_once = True

    def stop_music():
        _music_ch.stop()

    start_menu_music()

    state       = "menu"
    username    = ""
    game        = None
    final_score = 0
    final_dist  = 0
    final_coins = 0
    prev_state  = None

    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        # Switch music when state changes
        if state != prev_state:
            if state == "menu":
                start_menu_music()  # сыграет только если ещё не играл
            elif state == "game":
                stop_music()
            elif state == "game_over":
                stop_music()
            prev_state = state

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if state == "menu":
                btns = main_menu_screen(screen, WIDTH, HEIGHT)
                pygame.display.flip()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    bp, bl, bs, bq = btns
                    if bp.collidepoint(mouse_pos):
                        state = "name_entry"; username = ""
                    elif bl.collidepoint(mouse_pos): state = "leaderboard"
                    elif bs.collidepoint(mouse_pos): state = "settings"
                    elif bq.collidepoint(mouse_pos): pygame.quit(); sys.exit()

            elif state == "name_entry":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and username.strip():
                        game  = Game(settings, username.strip(), screen)
                        state = "game"
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.unicode.isprintable() and len(username) < 16:
                        username += event.unicode

            elif state == "game":
                pass

            elif state == "game_over":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    br, bm = game_over_screen(screen, WIDTH, HEIGHT,
                                              final_score, final_dist, final_coins)
                    pygame.display.flip()
                    if br.collidepoint(mouse_pos):
                        game  = Game(settings, username, screen)
                        state = "game"
                    elif bm.collidepoint(mouse_pos):
                        state = "menu"

            elif state == "leaderboard":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    lb  = load_leaderboard()
                    btn = leaderboard_screen(screen, WIDTH, HEIGHT, lb)
                    pygame.display.flip()
                    if btn.collidepoint(mouse_pos):
                        state = "menu"

            elif state == "settings":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    btn_sound, color_btns, diff_btns, btn_back = settings_screen(
                        screen, WIDTH, HEIGHT, settings)
                    pygame.display.flip()
                    if btn_sound.collidepoint(mouse_pos):
                        settings["sound"] = not settings["sound"]
                        save_settings(settings)
                        # Sound ON/OFF не перезапускает звук меню
                        if not settings["sound"]:
                            pygame.mixer.stop()
                    for rect, c in color_btns:
                        if rect.collidepoint(mouse_pos):
                            settings["car_color"] = c
                            save_settings(settings)
                    for rect, d in diff_btns:
                        if rect.collidepoint(mouse_pos):
                            settings["difficulty"] = d
                            save_settings(settings)
                    if btn_back.collidepoint(mouse_pos):
                        state = "menu"

        if state == "menu":
            main_menu_screen(screen, WIDTH, HEIGHT)

        elif state == "name_entry":
            name_entry_screen(screen, WIDTH, HEIGHT, username)

        elif state == "game":
            if game and game.alive:
                keys = pygame.key.get_pressed()
                game.update(keys)
                game.draw()
            elif game and not game.alive:
                final_score = game.score
                final_dist  = game.distance
                final_coins = game.coins
                save_score(username, final_score, final_dist)
                state = "game_over"

        elif state == "game_over":
            game_over_screen(screen, WIDTH, HEIGHT, final_score, final_dist, final_coins)

        elif state == "leaderboard":
            lb = load_leaderboard()
            leaderboard_screen(screen, WIDTH, HEIGHT, lb)

        elif state == "settings":
            settings_screen(screen, WIDTH, HEIGHT, settings)

        pygame.display.flip()

if __name__ == "__main__":
    main()