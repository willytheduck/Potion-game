import os
import pygame
from settings import ASSETS, FONT, ICON, W, H
from data import INGREDIENTS, POTIONS, CUSTOMERS


def try_load(name):
    try:
        return pygame.image.load(os.path.join(ASSETS, name)).convert_alpha()
    except (pygame.error, OSError):
        return None


class Assets:
    def __init__(self):
        self.font = pygame.font.Font(FONT, 12)
        self.big = pygame.font.Font(FONT, 26)
        self.load_images()

    def img(self, name, size, color, label=""):
        surf = try_load(name)
        if surf is not None:
            if surf.get_size() != size:
                surf = pygame.transform.scale(surf, size)
            return surf
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        pygame.draw.rect(surf, (20, 20, 30), surf.get_rect(), 1)
        if label:
            txt = self.font.render(label, False, (20, 20, 30))
            surf.blit(txt, txt.get_rect(center=surf.get_rect().center))
        return surf

    def load_images(self):
        bg = try_load("background.png")
        if bg is not None and bg.get_size() != (W, H):
            bg = pygame.transform.scale(bg, (W, H))
        self.bg = bg
        self.cauldron_frames = []
        sheet = try_load("cauldron.png")
        if sheet is not None:
            fw, fh = sheet.get_width() // 2, sheet.get_height() // 2
            for r in range(2):
                for c in range(2):
                    frame = sheet.subsurface((c * fw, r * fh, fw, fh)).copy()
                    if frame.get_size() != (64, 64):
                        frame = pygame.transform.scale(frame, (64, 64))
                    self.cauldron_frames.append(frame)
        else:
            for k in range(2):
                f = pygame.Surface((64, 64), pygame.SRCALPHA)
                pygame.draw.ellipse(f, (50, 50, 60), (2, 14, 60, 48))
                pygame.draw.ellipse(f, (70, 160, 70), (8, 14 + k, 48, 12))
                self.cauldron_frames.append(f)
        palette = [
            (220, 80, 80),
            (240, 150, 50),
            (230, 230, 220),
            (200, 200, 200),
            (255, 220, 80),
            (90, 180, 90),
            (120, 220, 120),
            (140, 120, 240),
        ]
        self.ing_img = {}
        for i, name in enumerate(INGREDIENTS):
            self.ing_img[name] = self.img(
                f"ingredient_{name}.png",
                (ICON, ICON),
                palette[i % len(palette)],
                name[:2],
            )
        self.potion_img = {
            pid: self.img(f"potion_{pid}.png", (32, 32), col)
            for pid, (_, col) in POTIONS.items()
        }
        self.customer_img = [
            self.img(f"customer_{i}.png", (32, 32), col)
            for i, (_, col) in enumerate(CUSTOMERS)
        ]
        self.boss_img = self.img("boss.png", (32, 32), (150, 30, 40), "BOSS")
        self.dummy_img = self.img("customer_1.png", (48, 64), (170, 130, 80), "dummy")
    
    def play(self,name):
        snd = self.sounds.get(name)
        if snd:
            snd.play()