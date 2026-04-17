import pygame
import sys
import os
from datetime import datetime

pygame.init()

# окно
screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Mickey Clock")

clock = pygame.time.Clock()

# путь к картинке
BASE_DIR = os.path.dirname(__file__)
IMAGE_PATH = os.path.join(BASE_DIR, "images", "sots", "image.jpeg")

# загрузка изображения
hand_image = pygame.image.load(IMAGE_PATH).convert_alpha()

# центр экрана
CENTER = (300, 300)

def draw_clock():
    now = datetime.now()
    minutes = now.minute
    seconds = now.second

    # углы
    minute_angle = -(minutes * 6)
    second_angle = -(seconds * 6)

    # поворот
    minute_hand = pygame.transform.rotate(hand_image, minute_angle)
    second_hand = pygame.transform.rotate(hand_image, second_angle)

    # центрирование
    minute_rect = minute_hand.get_rect(center=CENTER)
    second_rect = second_hand.get_rect(center=CENTER)

    # рисуем
    screen.blit(minute_hand, minute_rect)
    screen.blit(second_hand, second_rect)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))

    draw_clock()

    pygame.display.flip()
    clock.tick(1)