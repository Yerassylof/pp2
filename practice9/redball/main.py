import pygame, sys


pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Moving Ball Game")

clock = pygame.time.Clock()

ball_radius = 25
ball_x = 300
ball_y = 200
step = 20


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if ball_y - step - ball_radius >= 0:
                    ball_y -= step
            elif event.key == pygame.K_DOWN:
                if ball_y + step + ball_radius <= 400:
                    ball_y += step
            elif event.key == pygame.K_LEFT:
                if ball_x - step - ball_radius >= 0:
                    ball_x -= step
            elif event.key == pygame.K_RIGHT:
                if ball_x + step + ball_radius <= 600:
                    ball_x += step

    screen.fill((255, 255, 255))

    pygame.draw.circle(screen, (255, 0, 0), (ball_x, ball_y), ball_radius)

    pygame.display.flip()
    clock.tick(30) 