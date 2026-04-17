import pygame, sys, os

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((600, 200))
pygame.display.set_caption("Simple Music Player")
font = pygame.font.SysFont("Arial", 24)

# ===== ПРАВИЛЬНЫЙ ПУТЬ =====
BASE_DIR = os.path.dirname(__file__)
TRACKS_DIR = os.path.join(BASE_DIR, "tracks")

playlist = [
    os.path.join(TRACKS_DIR, f)
    for f in os.listdir(TRACKS_DIR)
    if f.endswith(".mp3") or f.endswith(".wav")
]

if not playlist:
    print("Нет музыки в папке tracks!")
    sys.exit()

current_index = 0
pygame.mixer.music.load(playlist[current_index])

def play_track():
    pygame.mixer.music.play()

def stop_track():
    pygame.mixer.music.stop()

def next_track():
    global current_index
    current_index = (current_index + 1) % len(playlist)
    pygame.mixer.music.load(playlist[current_index])
    play_track()

def prev_track():
    global current_index
    current_index = (current_index - 1) % len(playlist)
    pygame.mixer.music.load(playlist[current_index])
    play_track()

def draw_ui():
    screen.fill((255, 255, 255))

    track_name = os.path.basename(playlist[current_index])
    text = font.render(f"Track: {track_name}", True, (0, 0, 0))
    screen.blit(text, (20, 50))

    if pygame.mixer.music.get_busy():
        pos = pygame.mixer.music.get_pos() // 1000
        progress = font.render(f"Position: {pos} sec", True, (0, 0, 0))
        screen.blit(progress, (20, 100))

    pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                play_track()
            elif event.key == pygame.K_s:
                stop_track()
            elif event.key == pygame.K_n:
                next_track()
            elif event.key == pygame.K_b:
                prev_track()
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()

    draw_ui()