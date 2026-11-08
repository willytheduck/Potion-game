import math
import pygame
from settings import (
    W,
    H,
    SCALE,
    PATIENCE,
    SLOT_R,
    BREW_RECT,
    CLEAR_RECT,
    CAULDRON_POS,
    RESULT_POS,
    DUMMY_POS,
    MESSAGE_Y,
    DIFF,
)
from data import POTIONS, RECIPES
from game import ING_RECTS


def txt(surf, font, s, pos, color=(255, 255, 255), center=False):
    shadow = font.render(s, False, (15, 10, 25))
    img = font.render(s, False, color)
    r = img.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surf.blit(shadow, r.move(1, 1))
    surf.blit(img, r)


def draw(surf, game, art):
    draw_bg(surf, art)
    if game.state == "menu":
        draw_menu(surf, game, art)
    else:
        draw_game(surf, game, art)
        if game.state == "gameover":
            draw_gameover(surf, game, art)
    if game.book:
        draw_book(surf, game, art)


def draw_bg(surf, art):
    if art.bg is not None:
        surf.blit(art.bg, (0, 0))
        return
    surf.fill((38, 24, 56))
    pygame.draw.circle(surf, (240, 230, 170), (270, 28), 14)
    pygame.draw.rect(surf, (60, 40, 40), (0, 138, W, 42))
    pygame.draw.rect(surf, (30, 20, 30), (0, 138, W, 2))


def draw_menu(surf, game, art):
    f = art.font
    txt(surf, art.big, "POTION BREWING", (W // 2, 40, (255, 190, 70), True))
    txt(surf, f, "1 - Normal (1 potion each)"(W // 2, 80), center=True)
    txt(surf, f, "2 - Hard(1-3 potions, bosses!)", (W // 2, 96), center=True)
    txt(surf, f, "3 - Practice on the dummy", (W // 2, 112), center=True)
    txt(surf, f, "B - Recipe book   ESC - Quit", (W // 2, 140), (180, 170, 200), True)
    found = f"Recipes found: {len(game.discovered)}/{len(POTIONS)-1}"
    txt(surf, f, found, (W // 2, 160), (140, 220, 140), True)


def draw_game(surf, game, art):
    f = art.font
    mx, my = pygame.mouse.get_pos()
    mx, my = mx // SCALE, my // SCALE

    # cauldron n bubbles
    speed = 8 if game.brewing_t > 0 else 4
    frames = art.cauldron_frame
    surf.blit(frames[int(game.t * speed) % len(frames)], CAULDRON_POS)
    col = (110, 220, 110)
    if game.result and game.brewing_t <= 0:
        col = POTIONS[game.result[0]][1]
    for p in game.particles:
        pygame.draw.circle(surf, col, (int(p["x"]), int(p["y"])), p["r"])

    # slot
    for i, rect in enumerate(SLOT_R):
        pygame.draw.rect(surf, (25, 18, 38), rect)
        pygame.draw.rect(surf, (120, 100, 150), rect, 1)
        if i < len(game.slots):
            surf.blit(art.ing_img[game.slots[i]], rect)

    # shelf
    for name, rect in ING_RECTS.items():
        surf.blit(art.ing_img[name], rect)
        if rect.collidepoint(mx, my):
            pygame.draw.rect(surf, (255, 255, 120), rect.inflate(2, 2), 1)
            txt(surf, f, name.replace("_", " "), (rect.centerx, 130), center=True)

    # buttons
    for rect, label, color in (
        (BREW_RECT, "BREW", (90, 170, 90)),
        (CLEAR_RECT, "CLEAR", (170, 90, 90)),
    ):
        hot = rect.collidepoint(mx, my)
        pygame.draw.rect(surf, (255, 255, 255) if hot else color, rect)
        pygame.draw.rect(surf, (20, 20, 30), rect, 1)
        txt(surf, f, label, rect.center, (20, 20, 30) if hot else (255, 255, 255), True)

    # result potion
    if game.result and game.brewing_t <= 0:
        pid, _ = game.result
        surf.blit(art.potion_img[pid], RESULT_POS)
        txt(
            surf,
            f,
            POTIONS[pid][0],
            (RESULT_POS[0] + 16, RESULT_POS[1] + 40),
            POTIONS[pid][1],
            True,
        )

    # mode specific
    if game.mode == "practice":
        draw_dummy(surf, game, art)
        txt(surf, f, "PRACTICE - B: book    ESC: menu", (16, 16), (180, 170, 200))
    else:
        draw_customer(surf, game, art)
        txt(surf, f, f"Coins: {game.coins}", (244, 16), (255, 220, 80))
        txt(surf, f, f"Lives: {game.lives}", (244, 28), (255, 110, 110))
        txt(surf, f, DIFF[game.mode]["label"], (244, 40), (180, 170, 200))

    if game.brewing_t > 0:
        txt(surf, f, "Brewing...", (W // 2, MESSAGE_Y), (255, 240, 160), True)
    elif game.msg_t > 0:
        txt(surf, f, game.msg, (W // 2, MESSAGE_Y), (255, 240, 160), True)


def draw_customer(surf, game, art):
    c = game.customer
    if c is None:
        return
    f = art.font
    portrait = art.boss_img if c["boss"] else art.customer_img[c["idx"]]
    surf.blit(portrait, (16, 14))

    n = len(c["orders"])
    rows = 1 if n <= 2 else 2
    bubble = pygame.Rect(54, 16, 190, 10 + 12 * rows)
    fill = (255, 215, 215) if c["boss"] else (245, 240, 225)
    pygame.draw.rect(surf, fill, bubble)
    pygame.draw.rect(surf, (20, 20, 30), bubble, 1)

    if n == 1:
        name = POTIONS[c["orders"][0]][0]
        txt(
            surf,
            f,
            f"One {name} potion, please!",
            (bubble.x + 5, bubble.y + 5),
            (20, 20, 30),
        )
    else:
        for i, pid in enumerate(c["orders"]):
            x = bubble.x + 5 + (i % 2) * 92
            y = bubble.y + 5 + (i // 2) * 12
            name = POTIONS[pid][0]
            if c["done"][i]:
                txt(surf, f, name, (x, y), (150, 150, 150))
                w = f.size(name)[0]
                pygame.draw.line(surf, (90, 90, 90), (x, y + 5), (x + w, y + 5))
            else:
                txt(surf, f, name, (x, y), (20, 20, 30))

    # patience bar
    frac = max(0.0, c["patience"] / c["max"])
    bar = pygame.Rect(16, 48, 32, 4)
    pygame.draw.rect(surf, (40, 30, 50), bar)
    color = (
        (90, 200, 90)
        if frac > 0.5
        else (230, 190, 60) if frac > 0.25 else (220, 70, 70)
    )
    pygame.draw.rect(surf, color, (bar.x, bar.y, int(bar.w * frac), bar.h))
    if c["boss"]:
        txt(surf, f, "BOSS", (32, 58), (255, 110, 110), True)


def draw_dummy(surf, game, art):
    dummy = art.dummy_img
    if game.dummy_t > 0:
        dummy = dummy.copy()
        tint = tuple(v // 3 for v in game.dummy_color)
        dummy.fill(tint, special_flags=pygame.BLEND_RGB_ADD)
    shake = int(math.sin(game.t * 40) * 2) if game.dummy_t > 0 else 0
    surf.blit(dummy, (DUMMY_POS[0] + shake, DUMMY_POS[1]))


def draw_gameover(surf, game, art):
    f = art.font
    shade = pygame.Surface((W, H), pygame.SRCALPHA)
    shade.fill((10, 5, 20, 190))
    surf.blit(shade, (0, 0))
    txt(surf, art.big, "GAME OVER", (W // 2, 50), (255, 100, 100), True)
    label = DIFF[game.mode]["label"]
    txt(
        surf,
        f,
        f"{label} mode - you earned {game.coins} coins (Amazing! :D)",
        (W // 2, 86),
        center=True,
    )
    txt(surf, f, "ENTER - Retry    ESC - Menu", (W // 2, 110), (180, 170, 200), True)
    txt(
        surf,
        f,
        "1 Normal    2 Hard     3 Practice",
        (W // 2, 124),
        (180, 170, 200),
        True,
    )


def draw_book(surf, game, art):
    f = art.font
    panel = pygame.Rect(16, 8, W - 32, H - 16)
    pygame.draw.rect(surf, (35, 24, 50), panel)
    pygame.draw.rect(surf, (200, 170, 90), panel, 2)
    txt(surf, f, "RECIPE BOOK    (B to close)", (W // 2, 20), (255, 200, 90), True)
    y = 34
    for pid, (name, color) in POTIONS.items():
        if pid == "sludge":
            continue
        if pid in game.discovered:
            key = next(k for k, v in RECIPES.items() if v == pid)
            line = " + ".join(i.replace("_", " ") for i in key)
            txt(surf, f, name, (28, y), color)
            txt(surf, f, line, (110, y), (230, 230, 230))
        else:
            txt(surf, f, "???", (28, y), (110, 100, 130))
        y += 18