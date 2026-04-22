import pygame, random, sys, time, os

pygame.init()

# Экран параметрлері
WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with Images")

clock = pygame.time.Clock()

# Жұмыс каталогын main.py тұрған жерге орнату
os.chdir(os.path.dirname(__file__))

# Суреттерді жүктеу
background = pygame.image.load("png/background.png")
snake_img = pygame.image.load("png/snake.png")
food_img = pygame.image.load("png/food.png")

# Масштабтау
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
snake_img = pygame.transform.scale(snake_img, (CELL_SIZE, CELL_SIZE))
food_img = pygame.transform.scale(food_img, (CELL_SIZE, CELL_SIZE))

# Жылан бастапқы параметрлері
snake = [(100, 100), (80, 100), (60, 100)]
direction = (CELL_SIZE, 0)

# Тамақ генерациясы (салмақ және таймермен)
def random_food():
    while True:
        x = random.randint(0, (WIDTH - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        y = random.randint(0, (HEIGHT - CELL_SIZE) // CELL_SIZE) * CELL_SIZE
        if (x, y) not in snake:
            weight = random.choice([1, 2, 5])   # әртүрлі салмақ
            expire_time = time.time() + 5       # 5 секундтан кейін жоғалады
            return (x, y), weight, expire_time

food, food_weight, food_timer = random_food()

# Ұпай
score = 0
font = pygame.font.SysFont("Arial", 24)

running = True
while running:
    screen.blit(background, (0, 0))  # фон суреті

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Басқару
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and direction != (0, CELL_SIZE):
        direction = (0, -CELL_SIZE)
    if keys[pygame.K_DOWN] and direction != (0, -CELL_SIZE):
        direction = (0, CELL_SIZE)
    if keys[pygame.K_LEFT] and direction != (CELL_SIZE, 0):
        direction = (-CELL_SIZE, 0)
    if keys[pygame.K_RIGHT] and direction != (-CELL_SIZE, 0):
        direction = (CELL_SIZE, 0)

    # Жылан қозғалысы
    new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    # Қабырғаға соғылу
    if (new_head[0] < 0 or new_head[0] >= WIDTH or
        new_head[1] < 0 or new_head[1] >= HEIGHT):
        print("Game Over! Snake hit the wall.")
        pygame.quit()
        sys.exit()

    # Өзіне соғылу
    if new_head in snake:
        print("Game Over! Snake hit itself.")
        pygame.quit()
        sys.exit()

    snake.insert(0, new_head)

    # Тамақ жеу
    if new_head == food:
        score += food_weight
        food, food_weight, food_timer = random_food()
    else:
        snake.pop()

    # Тамақ таймері: уақыт біткенде жоғалады
    if time.time() > food_timer:
        food, food_weight, food_timer = random_food()

    # Сызу
    for segment in snake:
        screen.blit(snake_img, (segment[0], segment[1]))
    screen.blit(food_img, food)

    # Ұпай және тамақ салмағын көрсету
    score_text = font.render(f"Score: {score}", True, (255,255,255))
    weight_text = font.render(f"Food:{food_weight}", True, (255,255,255))
    screen.blit(score_text, (10, 10))
    screen.blit(weight_text, (WIDTH-120, 10))

    pygame.display.update()
    clock.tick(5)