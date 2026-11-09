import os
import sys

import pygame


def resource_path(rel):
    # where bundled files (assets) live: inside the .exe, or next to your code
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def app_dir():
    # the folder next to the .exe (or next to your code) - for save files
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# screen
W, H = 320, 180
SCALE = 4
FPS = 60
ASSETS = resource_path("assets")
FONT = resource_path("assets/PixelifySans-VariableFont_wght.ttf")
SAVE = os.path.join(app_dir(), "discover.json")

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

# combo
COMBO_M = (1.0, 1.0, 1.5, 2.0)

#high score
SCORES = os.path.join(app_dir(), "scores.json")

#hint
HINT_C = 15 #coins/hint (practice is free)
HINT_T = 8.0 #hint for 8 seconds

#bgm
MUSIC_FILES = ("bgm.ogg","bgm.mp3","bgm.wav")
MUSIC_VOL = 0.6

# layout
CAULDRON_POS = (128, 64)
SLOT_R = [
    pygame.Rect(x, y, ICON, ICON)
    for (x, y) in ((52, 66), (90, 66), (52, 100), (90, 100))
]
HINT_RECT = pygame.Rect(14,66,34,14)
BREW_RECT = pygame.Rect(262, 96, 48, 14)
CLEAR_RECT = pygame.Rect(262, 114, 48, 14)
RESULT_POS = (206, 70)
DUMMY_POS = (262, 28)
MESSAGE_Y = 57