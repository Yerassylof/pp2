import pygame
import random
import numpy as np

# ── Sound generation ──────────────────────────────────────────────────────────
def _make_sound(wave):
    stereo = np.column_stack([wave, wave])
    return pygame.sndarray.make_sound(stereo)

def gen_engine_sound():
    sr = 44100
    t  = np.linspace(0, 1.0, sr, False)
    w  = (np.sin(2*np.pi*60*t)*0.5 +
          np.sin(2*np.pi*120*t)*0.25 +
          np.sin(2*np.pi*180*t)*0.1)
    w *= (1 + 0.1 * np.sin(2*np.pi*8*t))
    fade = np.ones(sr)
    ramp = int(sr * 0.02)
    fade[:ramp]  = np.linspace(0, 1, ramp)
    fade[-ramp:] = np.linspace(1, 0, ramp)
    return _make_sound((w * fade * 32767).astype(np.int16))

def gen_coin_sound():
    sr = 44100
    t  = np.linspace(0, 0.18, int(sr * 0.18), False)
    w  = np.sin(2*np.pi*880*t)*0.6 + np.sin(2*np.pi*1320*t)*0.3
    return _make_sound((w * np.exp(-8*t) * 32767).astype(np.int16))

def gen_crash_sound():
    sr = 44100
    t  = np.linspace(0, 0.4, int(sr * 0.4), False)
    w  = np.random.uniform(-1, 1, len(t))*0.5 + np.sin(2*np.pi*55*t)*0.8
    return _make_sound((w * np.exp(-6*t) * 32767).astype(np.int16))

def gen_powerup_sound():
    sr = 44100
    t  = np.linspace(0, 0.35, int(sr * 0.35), False)
    w  = np.sin(2*np.pi*(300 + 600*(t/0.35))*t)
    return _make_sound((w * np.exp(-3*t) * 32767).astype(np.int16))

# FIX: sounds generated inside a function so mixer is already init'd by main.py
_SOUND_READY = False
_ENGINE_SND  = None
_COIN_SND    = None
_CRASH_SND   = None
_POWERUP_SND = None
_engine_ch   = None
_sfx_ch      = None

def init_sounds():
    """Call this after pygame.mixer.init() has been called in main.py."""
    global _SOUND_READY, _ENGINE_SND, _COIN_SND, _CRASH_SND, _POWERUP_SND
    global _engine_ch, _sfx_ch
    try:
        _ENGINE_SND  = gen_engine_sound()
        _COIN_SND    = gen_coin_sound()
        _CRASH_SND   = gen_crash_sound()
        _POWERUP_SND = gen_powerup_sound()
        _engine_ch   = pygame.mixer.Channel(0)
        _sfx_ch      = pygame.mixer.Channel(1)
        _SOUND_READY = True
    except Exception as e:
        print(f"Sound init error: {e}")
        _SOUND_READY = False

# ── colours ───────────────────────────────────────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (160, 160, 160)
DARK   = (40,  40,  40)
GREEN  = (0,   200, 80)
RED    = (220, 50,  50)
YELLOW = (255, 220, 0)
BLUE   = (50,  120, 255)
ORANGE = (255, 140, 0)
PURPLE = (160, 60,  220)

CAR_COLORS = {
    "red":    (220, 50,  50),
    "blue":   (50,  120, 255),
    "green":  (0,   200, 80),
    "yellow": (255, 220, 0),
    "white":  (240, 240, 240),
}

LANE_COUNT = 5
ROAD_LEFT  = 80
ROAD_RIGHT = 320
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT

DIFFICULTY = {
    "easy":   {"traffic_interval": 120, "obstacle_interval": 180, "base_speed": 4},
    "medium": {"traffic_interval": 80,  "obstacle_interval": 120, "base_speed": 5},
    "hard":   {"traffic_interval": 50,  "obstacle_interval": 80,  "base_speed": 7},
}

def lane_x(lane):
    return ROAD_LEFT + lane * LANE_WIDTH + LANE_WIDTH // 2

def draw_text(surface, text, size, x, y, color=WHITE, center=True):
    font = pygame.font.SysFont("Arial", size, bold=True)
    img  = font.render(text, True, color)
    r    = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surface.blit(img, r)

# ── Sprite classes ────────────────────────────────────────────────────────────
class PlayerCar(pygame.sprite.Sprite):
    def __init__(self, color_name, width, height):
        super().__init__()
        self.color  = CAR_COLORS.get(color_name, CAR_COLORS["red"])
        self.lane   = LANE_COUNT // 2
        self.width  = width
        self.height = height
        self.image  = self._make_image()
        self.rect   = self.image.get_rect()
        self.rect.centerx = lane_x(self.lane)
        self.rect.bottom  = height - 20
        self.move_cooldown = 0
        self.shield = False
        self.nitro  = False
        self.nitro_timer = 0

    def _make_image(self):
        img = pygame.Surface((36, 60), pygame.SRCALPHA)
        pygame.draw.rect(img, self.color,       (4, 10, 28, 44), border_radius=6)
        pygame.draw.rect(img, (200, 230, 255),  (8, 14, 20, 18), border_radius=3)
        pygame.draw.rect(img, BLACK, (4,  48, 10, 8), border_radius=3)
        pygame.draw.rect(img, BLACK, (22, 48, 10, 8), border_radius=3)
        pygame.draw.rect(img, BLACK, (4,  4,  10, 8), border_radius=3)
        pygame.draw.rect(img, BLACK, (22, 4,  10, 8), border_radius=3)
        return img

    def move(self, direction):
        if self.move_cooldown > 0:
            return
        self.lane = max(0, min(LANE_COUNT - 1, self.lane + direction))
        self.rect.centerx = lane_x(self.lane)
        self.move_cooldown = 12

    def update(self):
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        if self.nitro_timer > 0:
            self.nitro_timer -= 1
            if self.nitro_timer == 0:
                self.nitro = False
        if self.shield:
            pygame.draw.circle(
                pygame.display.get_surface(),
                (100, 180, 255), self.rect.center, 32, 3)


class TrafficCar(pygame.sprite.Sprite):
    COLORS = [(200,60,60),(60,100,200),(60,180,60),(180,180,60),(140,60,200)]

    def __init__(self, lane, speed):
        super().__init__()
        self.lane  = lane
        self.speed = speed
        self.image = self._make_image()
        self.rect  = self.image.get_rect()
        self.rect.centerx = lane_x(lane)
        self.rect.bottom  = -10

    def _make_image(self):
        color = random.choice(self.COLORS)
        img   = pygame.Surface((34, 58), pygame.SRCALPHA)
        pygame.draw.rect(img, color,          (3, 8,  28, 44), border_radius=6)
        pygame.draw.rect(img, (200, 230, 255),(7, 12, 20, 16), border_radius=3)
        pygame.draw.rect(img, BLACK, (3,  46, 10, 8), border_radius=3)
        pygame.draw.rect(img, BLACK, (21, 46, 10, 8), border_radius=3)
        return img

    def update(self, speed_multiplier=1.0):
        self.rect.y += int(self.speed * speed_multiplier)


class Obstacle(pygame.sprite.Sprite):
    TYPES = ["oil", "barrier", "pothole"]

    def __init__(self, lane, speed, otype=None):
        super().__init__()
        self.otype = otype or random.choice(self.TYPES)
        self.lane  = lane
        self.speed = speed
        self.image = self._make_image()
        self.rect  = self.image.get_rect()
        self.rect.centerx = lane_x(lane)
        self.rect.bottom  = -5

    def _make_image(self):
        img = pygame.Surface((38, 22), pygame.SRCALPHA)
        if self.otype == "oil":
            pygame.draw.ellipse(img, (30, 30, 80, 200),  (2, 4, 34, 14))
            pygame.draw.ellipse(img, (80, 80, 180, 120), (6, 6, 24, 8))
        elif self.otype == "barrier":
            pygame.draw.rect(img, (220, 60, 60), (0, 6, 38, 10), border_radius=4)
            for i in range(0, 38, 10):
                pygame.draw.rect(img, WHITE, (i, 6, 5, 10))
        else:
            pygame.draw.ellipse(img, (30, 30, 30), (4, 2, 30, 18))
            pygame.draw.ellipse(img, (60, 60, 60), (8, 6, 20, 10))
        return img

    def update(self, speed_multiplier=1.0):
        self.rect.y += int(self.speed * speed_multiplier)


class Coin(pygame.sprite.Sprite):
    WEIGHTS = [(1, YELLOW), (3, ORANGE), (5, (180, 60, 220))]

    def __init__(self, lane, speed):
        super().__init__()
        self.lane  = lane
        self.speed = speed
        pick = random.choices(self.WEIGHTS, weights=[6, 3, 1])[0]
        self.value, color = pick
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (10, 10), 9)
        draw_text(self.image, str(self.value), 10, 10, 10, BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = lane_x(lane)
        self.rect.bottom  = -5

    def update(self, speed_multiplier=1.0):
        self.rect.y += int(self.speed * speed_multiplier)


class PowerUp(pygame.sprite.Sprite):
    TYPES = {
        "nitro":  (ORANGE, "N"),
        "shield": (BLUE,   "S"),
        "repair": (GREEN,  "R"),
    }

    def __init__(self, lane, speed, ptype=None):
        super().__init__()
        self.ptype = ptype or random.choice(list(self.TYPES))
        color, letter = self.TYPES[self.ptype]
        self.speed = speed
        self.lane  = lane
        self.timer = 300
        self.image = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, 28, 28), border_radius=7)
        draw_text(self.image, letter, 18, 14, 14, WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = lane_x(lane)
        self.rect.bottom  = -5

    def update(self, speed_multiplier=1.0):
        self.rect.y += int(self.speed * speed_multiplier)
        self.timer -= 1


class NitroStrip(pygame.sprite.Sprite):
    def __init__(self, lane, speed):
        super().__init__()
        self.speed = speed
        self.image = pygame.Surface((LANE_WIDTH - 4, 18), pygame.SRCALPHA)
        self.image.fill((0, 230, 80, 160))
        self.rect  = self.image.get_rect()
        self.rect.centerx = lane_x(lane)
        self.rect.bottom  = -5

    def update(self, speed_multiplier=1.0):
        self.rect.y += int(self.speed * speed_multiplier)


# ── Main Game class ───────────────────────────────────────────────────────────
class Game:
    WIDTH  = 400
    HEIGHT = 600

    def __init__(self, settings, username, screen):
        self.settings   = settings
        self.username   = username
        self.screen     = screen
        self.diff       = DIFFICULTY[settings.get("difficulty", "medium")]
        self.base_speed = self.diff["base_speed"]
        self.speed_mult = 1.0

        self.player = PlayerCar(settings.get("car_color", "red"), self.WIDTH, self.HEIGHT)

        self.all_sprites  = pygame.sprite.Group()
        self.traffic      = pygame.sprite.Group()
        self.obstacles    = pygame.sprite.Group()
        self.coins_grp    = pygame.sprite.Group()
        self.powerups     = pygame.sprite.Group()
        self.nitro_strips = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        self.stripe_y  = [i * 60 for i in range(11)]
        self.road_speed = self.base_speed

        self.traffic_timer   = 0
        self.obstacle_timer  = 0
        self.coin_timer      = 0
        self.powerup_timer   = 0
        self.nitro_s_timer   = 0
        self.difficulty_tick = 0

        self.score    = 0
        self.coins    = 0
        self.distance = 0.0
        self.alive    = True
        self.active_powerup       = None
        self.active_powerup_timer = 0

        # Start engine sound loop
        if _SOUND_READY and settings.get("sound", True):
            _engine_ch.play(_ENGINE_SND, loops=-1)

    def _safe_lane(self):
        occupied = set()
        for s in list(self.traffic) + list(self.obstacles):
            if s.rect.y < 200:
                occupied.add(s.lane)
        lanes = [l for l in range(LANE_COUNT) if l not in occupied]
        return random.choice(lanes) if lanes else random.randint(0, LANE_COUNT - 1)

    def _spawn_traffic(self):
        lane  = self._safe_lane()
        speed = self.base_speed + random.randint(0, 2)
        car   = TrafficCar(lane, speed)
        self.traffic.add(car); self.all_sprites.add(car)

    def _spawn_obstacle(self):
        lane = self._safe_lane()
        obs  = Obstacle(lane, self.base_speed)
        self.obstacles.add(obs); self.all_sprites.add(obs)

    def _spawn_coin(self):
        lane = random.randint(0, LANE_COUNT - 1)
        c    = Coin(lane, self.base_speed)
        self.coins_grp.add(c); self.all_sprites.add(c)

    def _spawn_powerup(self):
        if len(self.powerups) == 0:
            lane = random.randint(0, LANE_COUNT - 1)
            p    = PowerUp(lane, self.base_speed)
            self.powerups.add(p); self.all_sprites.add(p)

    def _spawn_nitro_strip(self):
        lane = random.randint(0, LANE_COUNT - 1)
        ns   = NitroStrip(lane, self.base_speed)
        self.nitro_strips.add(ns); self.all_sprites.add(ns)

    def _activate_powerup(self, ptype):
        self.active_powerup       = ptype
        self.active_powerup_timer = 180 if ptype == "nitro" else (999 if ptype == "shield" else 1)
        if ptype == "nitro":
            self.player.nitro       = True
            self.player.nitro_timer = 180
        elif ptype == "shield":
            self.player.shield = True
        elif ptype == "repair":
            for obs in self.obstacles:
                obs.kill(); break
            self.active_powerup       = None
            self.active_powerup_timer = 0

    def _draw_road(self):
        s = self.screen
        pygame.draw.rect(s, (60, 60, 60), (ROAD_LEFT, 0, ROAD_WIDTH, self.HEIGHT))
        for i in range(1, LANE_COUNT):
            x = ROAD_LEFT + i * LANE_WIDTH
            for sy in self.stripe_y:
                pygame.draw.rect(s, (200, 200, 100), (x - 2, sy, 4, 30))
        pygame.draw.rect(s, (220, 50, 50), (ROAD_LEFT - 15, 0, 15, self.HEIGHT))
        pygame.draw.rect(s, (220, 50, 50), (ROAD_RIGHT,     0, 15, self.HEIGHT))

    def _scroll_road(self):
        for i in range(len(self.stripe_y)):
            self.stripe_y[i] += self.road_speed
            if self.stripe_y[i] > self.HEIGHT:
                self.stripe_y[i] -= self.HEIGHT + 30

    def _draw_hud(self):
        s = self.screen
        draw_text(s, f"Score: {self.score}",         18, 5, 10, WHITE,  center=False)
        draw_text(s, f"Coins: {self.coins}",         18, 5, 32, YELLOW, center=False)
        draw_text(s, f"Dist:  {int(self.distance)}m",18, 5, 54, GREEN,  center=False)
        if self.active_powerup and self.active_powerup_timer > 0:
            label = f"[{self.active_powerup.upper()}] {self.active_powerup_timer//60}s"
            draw_text(s, label, 18, self.WIDTH - 5, 10,
                      ORANGE if self.active_powerup == "nitro" else
                      BLUE   if self.active_powerup == "shield" else GREEN,
                      center=False)

    def update(self, keys):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.player.move(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.player.move(1)

        self.road_speed = self.base_speed + (1 if self.player.nitro else 0)
        self.speed_mult = 1.0
        self._scroll_road()
        self.distance += self.road_speed * 0.05

        ti = self.diff["traffic_interval"]
        oi = self.diff["obstacle_interval"]

        self.traffic_timer   += 1
        self.obstacle_timer  += 1
        self.coin_timer      += 1
        self.powerup_timer   += 1
        self.nitro_s_timer   += 1
        self.difficulty_tick += 1

        if self.traffic_timer  >= ti:  self._spawn_traffic();    self.traffic_timer  = 0
        if self.obstacle_timer >= oi:  self._spawn_obstacle();   self.obstacle_timer = 0
        if self.coin_timer     >= 60:  self._spawn_coin();       self.coin_timer     = 0
        if self.powerup_timer  >= 240: self._spawn_powerup();    self.powerup_timer  = 0
        if self.nitro_s_timer  >= 300: self._spawn_nitro_strip(); self.nitro_s_timer = 0

        if self.difficulty_tick >= 600:
            self.base_speed = min(self.base_speed + 0.5, 15)
            self.difficulty_tick = 0

        for t  in self.traffic:      t.update()
        for o  in self.obstacles:    o.update()
        for c  in self.coins_grp:    c.update()
        for p  in self.powerups:     p.update()
        for ns in self.nitro_strips: ns.update()
        self.player.update()

        for grp in (self.traffic, self.obstacles, self.coins_grp, self.nitro_strips):
            for s in grp:
                if s.rect.top > self.HEIGHT:
                    s.kill()
        for p in self.powerups:
            if p.rect.top > self.HEIGHT or p.timer <= 0:
                p.kill()

        if self.active_powerup and self.active_powerup != "repair":
            self.active_powerup_timer -= 1
            if self.active_powerup_timer <= 0:
                self.active_powerup = None
                self.player.nitro   = False
                self.player.shield  = False

        # Coin collection
        for c in pygame.sprite.spritecollide(self.player, self.coins_grp, True):
            self.coins += c.value
            self.score += c.value * 10
            if _SOUND_READY: _sfx_ch.play(_COIN_SND)

        # Powerup collection
        for p in pygame.sprite.spritecollide(self.player, self.powerups, True):
            if self.active_powerup is None:
                self._activate_powerup(p.ptype)
                if _SOUND_READY: _sfx_ch.play(_POWERUP_SND)

        # Nitro strip
        for ns in pygame.sprite.spritecollide(self.player, self.nitro_strips, True):
            if not self.player.nitro:
                self.player.nitro         = True
                self.player.nitro_timer   = 120
                self.active_powerup       = "nitro"
                self.active_powerup_timer = 120

        # Collision with traffic
        if pygame.sprite.spritecollide(self.player, self.traffic, False,
                                       pygame.sprite.collide_mask):
            if self.player.shield:
                self.player.shield  = False
                self.active_powerup = None
                for t in pygame.sprite.spritecollide(self.player, self.traffic, True):
                    break
            else:
                if _SOUND_READY: _sfx_ch.play(_CRASH_SND)
                self.alive = False

        # Collision with obstacles
        if pygame.sprite.spritecollide(self.player, self.obstacles, False):
            if self.player.shield:
                self.player.shield  = False
                self.active_powerup = None
                for o in pygame.sprite.spritecollide(self.player, self.obstacles, True):
                    break
            else:
                if _SOUND_READY: _sfx_ch.play(_CRASH_SND)
                self.alive = False

        self.score = self.coins * 10 + int(self.distance)

    def draw(self):
        self.screen.fill((30, 30, 30))
        self._draw_road()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect)
        if self.player.shield:
            pygame.draw.circle(self.screen, (100, 180, 255),
                               self.player.rect.center, 28, 3)
        self._draw_hud()