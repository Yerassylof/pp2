import pygame
import random
import json
import os
import numpy as np
from config import *

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    return {"snake_color": list(GREEN), "grid": True, "sound": False}

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

# ── Sound generation (no files needed) ───────────────────────────────────────
def _make_snd(wave):
    stereo = np.column_stack([wave, wave])
    return pygame.sndarray.make_sound(stereo)

def _gen_eat_sound():
    sr = 44100
    t  = np.linspace(0, 0.12, int(sr * 0.12), False)
    w  = np.sin(2*np.pi*660*t)*0.5 + np.sin(2*np.pi*880*t)*0.3
    return _make_snd((w * np.exp(-10*t) * 32767).astype(np.int16))

def _gen_die_sound():
    sr = 44100
    t  = np.linspace(0, 0.5, int(sr * 0.5), False)
    w  = np.random.uniform(-1, 1, len(t))*0.4 + np.sin(2*np.pi*80*t)*0.6
    return _make_snd((w * np.exp(-5*t) * 32767).astype(np.int16))

def _gen_powerup_sound():
    sr = 44100
    t  = np.linspace(0, 0.3, int(sr * 0.3), False)
    w  = np.sin(2*np.pi*(400 + 500*(t/0.3))*t)
    return _make_snd((w * np.exp(-3*t) * 32767).astype(np.int16))

def _gen_poison_sound():
    sr = 44100
    t  = np.linspace(0, 0.3, int(sr * 0.3), False)
    w  = np.sin(2*np.pi*(400 - 300*(t/0.3))*t)
    return _make_snd((w * np.exp(-4*t) * 32767).astype(np.int16))

def _gen_levelup_sound():
    sr = 44100
    t  = np.linspace(0, 0.4, int(sr * 0.4), False)
    w  = (np.sin(2*np.pi*523*t)*0.4 +
          np.sin(2*np.pi*659*t)*0.3 +
          np.sin(2*np.pi*784*t)*0.3)
    fade = np.exp(-3*t)
    return _make_snd((w * fade * 32767).astype(np.int16))

def _gen_menu_music():
    """Short pleasant chord — plays once when entering menu."""
    sr  = 44100
    dur = 0.6
    t   = np.linspace(0, dur, int(sr * dur), False)
    w   = (np.sin(2*np.pi*523*t)*0.35 +   # C5
           np.sin(2*np.pi*659*t)*0.25 +   # E5
           np.sin(2*np.pi*784*t)*0.20)    # G5
    envelope = np.exp(-5*t)
    w *= envelope
    return _make_snd((w * 32767).astype(np.int16))

# Initialize sounds after mixer is ready (called from main.py)
_SOUND_READY  = False
_SND_EAT      = None
_SND_DIE      = None
_SND_POWERUP  = None
_SND_POISON   = None
_SND_LEVELUP  = None
_SND_MENU     = None
_sfx_ch       = None
_music_ch     = None

def init_sounds():
    global _SOUND_READY, _SND_EAT, _SND_DIE, _SND_POWERUP
    global _SND_POISON, _SND_LEVELUP, _SND_MENU, _sfx_ch, _music_ch
    try:
        _SND_EAT     = _gen_eat_sound()
        _SND_DIE     = _gen_die_sound()
        _SND_POWERUP = _gen_powerup_sound()
        _SND_POISON  = _gen_poison_sound()
        _SND_LEVELUP = _gen_levelup_sound()
        _SND_MENU    = _gen_menu_music()
        _sfx_ch      = pygame.mixer.Channel(0)
        _music_ch    = pygame.mixer.Channel(1)
        _SOUND_READY = True
    except Exception as e:
        print(f"Sound init error: {e}")
        _SOUND_READY = False

def play_sfx(snd):
    if _SOUND_READY and snd:
        _sfx_ch.play(snd)

def play_menu_music():
    """Play once — не зацикливать."""
    if _SOUND_READY and _SND_MENU:
        _music_ch.play(_SND_MENU, loops=0)  # loops=0 = один раз

def stop_music():
    if _SOUND_READY:
        _music_ch.stop()

# ── helpers ───────────────────────────────────────────────────────────────────
def draw_text(surf, text, size, x, y, color=WHITE, center=True):
    font = pygame.font.SysFont("Arial", size, bold=True)
    img  = font.render(text, True, color)
    r    = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)

def draw_button(surf, text, x, y, w=200, h=48, color=GRAY, tc=WHITE):
    r = pygame.Rect(x - w//2, y - h//2, w, h)
    pygame.draw.rect(surf, color, r, border_radius=10)
    pygame.draw.rect(surf, WHITE, r, 2, border_radius=10)
    draw_text(surf, text, 22, x, y, tc)
    return r

def cell(col, row):
    return pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

def rand_cell(exclude=None):
    exclude = exclude or set()
    while True:
        c = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
        if c not in exclude:
            return c

# ── Beautiful gradient menu background ───────────────────────────────────────
def draw_menu_bg(surf):
    """Draw a dark teal-to-purple gradient background with subtle dots."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(10  + ratio * 30)
        g = int(30  + ratio * 10)
        b = int(60  + ratio * 40)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    # Subtle grid dots
    for cx in range(0, WIDTH, 40):
        for cy in range(0, HEIGHT, 40):
            pygame.draw.circle(surf, (255, 255, 255, 20), (cx, cy), 1)

# ── screens ───────────────────────────────────────────────────────────────────
def screen_menu(surf, username):
    # Beautiful gradient background instead of plain black
    draw_menu_bg(surf)

    # Decorative snake icon line
    for i in range(8):
        cx = WIDTH//2 - 70 + i*20
        pygame.draw.rect(surf, GREEN,
                         pygame.Rect(cx, HEIGHT//5 - 45, 16, 16), border_radius=4)

    draw_text(surf, "🐍  SNAKE", 60, WIDTH//2, HEIGHT//5, GREEN)
    draw_text(surf, "Enter name:", 22, WIDTH//2, HEIGHT//2 - 70, GRAY)
    draw_text(surf, username + "|", 28, WIDTH//2, HEIGHT//2 - 38, WHITE)

    bp  = draw_button(surf, "▶  Play",        WIDTH//2, HEIGHT//2 + 30,  220, 50, GREEN)
    blb = draw_button(surf, "🏆  Leaderboard", WIDTH//2, HEIGHT//2 + 95,  220, 50,
                      (50, 80, 120))
    bst = draw_button(surf, "⚙  Settings",    WIDTH//2, HEIGHT//2 + 160, 220, 50,
                      (70, 60, 110))
    bq  = draw_button(surf, "✖  Quit",        WIDTH//2, HEIGHT//2 + 225, 220, 50, RED)
    return bp, blb, bst, bq

def screen_gameover(surf, score, level, personal_best):
    draw_menu_bg(surf)
    draw_text(surf, "GAME OVER", 54, WIDTH//2, HEIGHT//4, RED)
    draw_text(surf, f"Score:   {score}",         26, WIDTH//2, HEIGHT//4 + 80)
    draw_text(surf, f"Level:   {level}",         26, WIDTH//2, HEIGHT//4 + 120)
    draw_text(surf, f"Best:    {personal_best}", 26, WIDTH//2, HEIGHT//4 + 160, YELLOW)
    br = draw_button(surf, "↺  Retry",     WIDTH//2, HEIGHT//4 + 240, 200, 50, GREEN)
    bm = draw_button(surf, "⌂  Main Menu", WIDTH//2, HEIGHT//4 + 300, 200, 50,
                     (50, 80, 120))
    return br, bm

def screen_leaderboard(surf, rows):
    draw_menu_bg(surf)
    draw_text(surf, "🏆 Leaderboard", 44, WIDTH//2, 55, YELLOW)
    headers = f"{'#':<3} {'Name':<14} {'Score':>6} {'Lvl':>4} {'Date':>12}"
    draw_text(surf, headers, 17, 30, 105, GRAY, center=False)
    for i, (name, score, lvl, date) in enumerate(rows):
        y   = 135 + i * 34
        col = YELLOW if i == 0 else WHITE
        line = f"{i+1:<3} {name:<14} {score:>6} {lvl:>4} {date:>12}"
        draw_text(surf, line, 17, 30, y, col, center=False)
    bb = draw_button(surf, "← Back", WIDTH//2, HEIGHT - 45, 180, 44,
                     (50, 80, 120))
    return bb

def screen_settings(surf, settings):
    draw_menu_bg(surf)
    draw_text(surf, "Settings", 44, WIDTH//2, 65, YELLOW)

    grid_lbl  = "Grid: ON"  if settings.get("grid", True)  else "Grid: OFF"
    sound_lbl = "Sound: ON" if settings.get("sound", False) else "Sound: OFF"

    bg = draw_button(surf, grid_lbl,  WIDTH//2, 180, 220, 48,
                     GREEN if settings.get("grid", True) else RED)
    bs = draw_button(surf, sound_lbl, WIDTH//2, 244, 220, 48,
                     GREEN if settings.get("sound", False) else RED)

    # FIX: Snake color text — ярче чтобы было видно
    draw_text(surf, "Snake color:", 22, WIDTH//2, 310, WHITE)

    color_opts = [
        ("Green",  [0, 200, 80]),
        ("Blue",   [50, 120, 255]),
        ("Yellow", [255, 220, 0]),
        ("White",  [240, 240, 240]),
    ]
    color_btns = []
    for i, (lbl, rgb) in enumerate(color_opts):
        bx = 100 + i * 110
        r  = pygame.Rect(bx - 30, 335, 60, 36)
        pygame.draw.rect(surf, tuple(rgb), r, border_radius=6)
        if settings.get("snake_color", [0,200,80]) == rgb:
            pygame.draw.rect(surf, WHITE, r, 3, border_radius=6)
        # FIX: надписи ниже цветов — y=385 вместо 372
        draw_text(surf, lbl, 14, bx, 385, WHITE)
        color_btns.append((r, rgb))

    bb = draw_button(surf, "Save & Back", WIDTH//2, 450, 200, 48, (50, 80, 120))
    return bg, bs, color_btns, bb


# ── main Game class ───────────────────────────────────────────────────────────
class SnakeGame:
    FOOD_WEIGHTS = [(1, GREEN), (3, ORANGE), (5, PURPLE)]

    def __init__(self, settings, username, personal_best, screen):
        self.settings      = settings
        self.username      = username
        self.personal_best = personal_best
        self.screen        = screen
        self.snake_color   = tuple(settings["snake_color"])
        self.reset()

    def reset(self):
        cx, cy        = COLS//2, ROWS//2
        self.body     = [(cx, cy), (cx-1, cy), (cx-2, cy)]
        self.dir      = (1, 0)
        self.next_dir = (1, 0)
        self.score    = 0
        self.level    = 1
        self.foods    = []
        self.poison   = None
        self.powerup_field  = None
        self.active_powerup = None
        self.obstacles      = set()
        self.alive          = True
        self.food_eaten     = 0
        self.shield_used    = False
        self._spawn_food()
        self._spawn_food()

    def _occupied(self):
        s = set(self.body) | self.obstacles
        for f in self.foods:   s.add(f["pos"])
        if self.poison:        s.add(self.poison["pos"])
        if self.powerup_field: s.add(self.powerup_field["pos"])
        return s

    def _spawn_food(self):
        pos  = rand_cell(self._occupied())
        pick = random.choices(self.FOOD_WEIGHTS, weights=[6, 3, 1])[0]
        value, color = pick
        self.foods.append({"pos": pos, "value": value, "color": color,
                           "spawn_time": pygame.time.get_ticks()})

    def _spawn_poison(self):
        if self.poison is None:
            pos = rand_cell(self._occupied())
            self.poison = {"pos": pos, "spawn_time": pygame.time.get_ticks()}

    def _spawn_powerup(self):
        if self.powerup_field is None:
            pos   = rand_cell(self._occupied())
            ptype = random.choice(["speed", "slow", "shield"])
            self.powerup_field = {"pos": pos, "ptype": ptype,
                                  "spawn_time": pygame.time.get_ticks()}

    def _spawn_obstacles(self):
        self.obstacles.clear()
        blocked = set(self.body)
        count   = 5 + self.level * 2
        for _ in range(count * 10):
            if len(self.obstacles) >= count:
                break
            c = rand_cell(blocked | self.obstacles)
            hx, hy = self.body[0]
            if abs(c[0]-hx) < 3 and abs(c[1]-hy) < 3:
                continue
            self.obstacles.add(c)

    def get_speed(self):
        base = min(5 + self.level * 2, 25)
        now  = pygame.time.get_ticks()
        if self.active_powerup:
            pt = self.active_powerup["ptype"]
            if now < self.active_powerup["end_time"]:
                if pt == "speed": base = min(base + 8, 30)
                if pt == "slow":  base = max(base - 4, 3)
            else:
                self.active_powerup = None
        return base

    def update(self):
        now = pygame.time.get_ticks()
        sound_enabled = self.settings.get("sound", False)

        # expire food/poison/powerup
        self.foods = [f for f in self.foods if now - f["spawn_time"] < 8000]
        if not self.foods:
            self._spawn_food()
        if self.poison and now - self.poison["spawn_time"] > 8000:
            self.poison = None
        if self.powerup_field and now - self.powerup_field["spawn_time"] > 8000:
            self.powerup_field = None

        # random spawns
        if random.random() < 0.015 and len(self.foods) < 3:
            self._spawn_food()
        if random.random() < 0.008:
            self._spawn_poison()
        if random.random() < 0.005 and self.powerup_field is None:
            self._spawn_powerup()

        # move
        self.dir = self.next_dir
        hx, hy   = self.body[0]
        dx, dy   = self.dir
        nx, ny   = hx + dx, hy + dy

        # wall collision
        if nx < 0 or nx >= COLS or ny < 0 or ny >= ROWS:
            if (self.active_powerup and
                    self.active_powerup["ptype"] == "shield" and
                    now < self.active_powerup["end_time"] and
                    not self.shield_used):
                self.shield_used    = True
                self.active_powerup = None
                nx = max(0, min(COLS-1, nx))
                ny = max(0, min(ROWS-1, ny))
            else:
                if sound_enabled: play_sfx(_SND_DIE)
                self.alive = False; return

        # self collision
        if (nx, ny) in set(self.body[:-1]):
            if (self.active_powerup and
                    self.active_powerup["ptype"] == "shield" and
                    now < self.active_powerup["end_time"] and
                    not self.shield_used):
                self.shield_used    = True
                self.active_powerup = None
            else:
                if sound_enabled: play_sfx(_SND_DIE)
                self.alive = False; return

        # obstacle collision
        if (nx, ny) in self.obstacles:
            if sound_enabled: play_sfx(_SND_DIE)
            self.alive = False; return

        self.body.insert(0, (nx, ny))

        ate = False

        # eat food
        for f in self.foods:
            if (nx, ny) == f["pos"]:
                self.score      += f["value"]
                self.food_eaten += 1
                self.foods.remove(f)
                self._spawn_food()
                if sound_enabled: play_sfx(_SND_EAT)
                ate = True

                # level up
                new_level = 1 + self.food_eaten // 5
                if new_level > self.level:
                    self.level = new_level
                    if sound_enabled: play_sfx(_SND_LEVELUP)
                    if self.level >= 3:
                        self._spawn_obstacles()
                break

        # eat poison
        if self.poison and (nx, ny) == self.poison["pos"]:
            self.poison = None
            self.body   = self.body[:-2] if len(self.body) > 3 else self.body[:1]
            if sound_enabled: play_sfx(_SND_POISON)
            if len(self.body) <= 1:
                self.alive = False; return
            ate = True

        # eat powerup
        if self.powerup_field and (nx, ny) == self.powerup_field["pos"]:
            ptype = self.powerup_field["ptype"]
            self.powerup_field  = None
            self.active_powerup = {"ptype": ptype, "end_time": now + 5000}
            self.shield_used    = False
            if sound_enabled: play_sfx(_SND_POWERUP)
            ate = True

        if not ate:
            self.body.pop()

    def draw(self):
        s = self.screen
        s.fill(DARK)

        if self.settings["grid"]:
            for c in range(COLS):
                for r in range(ROWS):
                    pygame.draw.rect(s, (35, 35, 35), cell(c, r), 1)

        for (c, r) in self.obstacles:
            pygame.draw.rect(s, (100, 80, 60), cell(c, r))
            pygame.draw.rect(s, (60, 40, 20),  cell(c, r), 2)

        for f in self.foods:
            pygame.draw.ellipse(s, f["color"], cell(*f["pos"]))

        if self.poison:
            r = cell(*self.poison["pos"])
            pygame.draw.ellipse(s, DARK_RED, r)
            draw_text(s, "☠", 14, r.centerx, r.centery, WHITE)

        if self.powerup_field:
            r     = cell(*self.powerup_field["pos"])
            icons = {"speed": (ORANGE, "⚡"), "slow": (BLUE, "🐌"),
                     "shield": (PURPLE, "🛡")}
            col, icon = icons[self.powerup_field["ptype"]]
            pygame.draw.rect(s, col, r, border_radius=4)
            draw_text(s, icon, 13, r.centerx, r.centery)

        for i, (c, r) in enumerate(self.body):
            color = self.snake_color if i > 0 else WHITE
            pygame.draw.rect(s, color, cell(c, r), border_radius=4)

        now = pygame.time.get_ticks()
        draw_text(s, f"Score: {self.score}",         18, 5, 5,  WHITE,  center=False)
        draw_text(s, f"Level: {self.level}",         18, 5, 27, YELLOW, center=False)
        draw_text(s, f"Best:  {self.personal_best}", 18, 5, 49, GREEN,  center=False)

        if self.active_powerup:
            pt  = self.active_powerup["ptype"]
            rem = max(0, (self.active_powerup["end_time"] - now) // 1000)
            icons = {"speed": "⚡ Speed", "slow": "🐌 Slow", "shield": "🛡 Shield"}
            draw_text(s, f"{icons[pt]} {rem}s", 18, WIDTH - 5, 5,
                      ORANGE if pt == "speed" else BLUE if pt == "slow" else PURPLE,
                      center=False)