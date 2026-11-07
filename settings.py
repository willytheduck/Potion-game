import pygame

# screen
W, H = 320, 180
SCALE = 6
FPS = 60
ASSETS = "assets"
FONT = None
SAVE = "discover.json"

# brew
ICON = 32
MIN = 2  # need atleastt 2-4 ingredients
MAX = 4
BREW_T = 1.2  # seconds of brewing

# customers
PATIENCE = 40.0  # seconds for customer to wait
EXTRA_P = 25.0  # extra seconds
S_LIVES = 3
WRONG_LEAVES = True
NEXT_CD = 2.5

# DIFF
DIFF = {
    "normal": {"label": "Normal", "potions": (1, 1), "boss_chance": 0.0},
    "hard": {"label": "Hard", "potions": (1, 3), "boss_chance": 0.10},
}
BOSS_P = 4  # boss always order this much
BOSS_B = 50  # extra coins if finished

# layout
CAULDRON_POS = (128, 64)
SLOT_R = [
    pygame.Rect(x, y, ICON, ICON)
    for (x, y) in ((52, 66), (90, 66), (52, 100), (90, 100))
]
BREW_RECT = pygame.Rect(262, 96, 48, 14)
CLEAR_RECT = pygame.Rect(262, 114, 48, 14)
RESULT_POS = (206, 70)
DUMMY_POS = (262, 28)
MESSAGE_Y = 57
