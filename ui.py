import math
import pygame
from settings import (W, H, SCALE,PATIENCE,SLOT_R,BREW_RECT,CLEAR_RECT, CAULDRON_POS,RESULT_POS,DUMMY_POS,MESSAGE_Y,DIFF)
from data import POTIONS, RECIPES
from game import ING_RECTS

def txt(surf, font, s, pos, color=(255,255,255), center=False):
    shadow = font.render(s,False,(15,10,25))
    img = font.render(s, False,color)
    r = img.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surf.blit(shadow, r.move(1,1))
    surf.blit(img,r)

def draw(surf, game, art):
    draw_bg(surf,art)
    if game.state == "menu":
        draw_menu(surf,game,art)
    else:
        draw_game(surf,game,art)
        if game.state == "gameover":
            draw_gameover(surf, game, art)
    if game.book:
        draw_book(surf,game,art)

def draw_bg(surf,art):
    if art.bg is not None:
        surf.blit(art.bg, (0,0))
        return
    surf.fill((38,24,56))
    pygame.draw.circle(surf,(240,230,170), (270,28),14)
    pygame.draw.rect(surf, (60,40,40), (0,138,W,42))
    pygame.draw.rect(surf,(30,20,30), (0,138,W,2))

def draw_menu(surf,game,art):
    f = art.font
    txt(surf,art.big,"POTION BREWING", (W//2,40, (255,190,70), True))
    txt(surf,f,"1 - Normal (1 potion each)"m (W//2, 80), center=True)
    txt(surf, f, "2 - Hard(1-3 potions, bosses!)", (W//2,96), center=True)
    txt(surf, f, "3 - Practice on the dummy", (W//2,112), center=True)
    txt(surf, f, "B - Recipe book   ESC - Quit", (W//2, 140), (180,170,200), True)
    