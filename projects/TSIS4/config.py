# Window & grid
WIDTH        = 600
HEIGHT       = 600
CELL_SIZE    = 20
COLS         = WIDTH  // CELL_SIZE
ROWS         = HEIGHT // CELL_SIZE
FPS          = 10

# Colors
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
GRAY         = (40,  40,  40)
DARK         = (20,  20,  20)
GREEN        = (0,   200, 80)
RED          = (220, 50,  50)
YELLOW       = (255, 220, 0)
BLUE         = (50,  120, 255)
ORANGE       = (255, 140, 0)
PURPLE       = (160, 60,  220)
DARK_RED     = (120, 0,   0)

# DB
DB_CONFIG = {
    "dbname":   "snake_db",
    "user":     "postgres",
    "password": "Gg123456",   # ← поменяй на свой пароль
    "host":     "localhost",
    "port":     5432,
}