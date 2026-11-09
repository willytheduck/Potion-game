import json
import random
import sys
import pygame

from settings import (
    MIN,
    MAX,
    BREW_T,
    PATIENCE,
    EXTRA_P,
    S_LIVES,
    WRONG_LEAVES,
    NEXT_CD,
    DIFF,
    BOSS_P,
    BOSS_B,
    SAVE,
    SLOT_R,
    BREW_RECT,
    CLEAR_RECT,
    CAULDRON_POS,
    COMBO_M,
)
from data import INGREDIENTS, POTIONS, RECIPES, EFFECTS, CUSTOMERS, ORDERABLE, R
from settings import ICON, W

_step = min(36, (W - 24 - ICON) // max(1, len(INGREDIENTS) - 1))
ING_RECTS = {
    name: pygame.Rect(12 + i * _step, 134, ICON, ICON)
    for i, name in enumerate(INGREDIENTS)
}


def load_d():
    try:
        with open(SAVE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (OSError, ValueError):
        return set()


def save_d(found):
    try:
        with open(SAVE, "w", encoding="utf-8") as f:
            json.dump(sorted(found), f)
    except OSError:
        pass


class Game:
    def __init__(self, art):
        self.art = art
        self.play = art.play
        self.discover = load_d()
        self.state = "menu"  # menu/play/gameover
        self.mode = "normal"  # difficulty
        self.t = 0.0
        self.book = False
        self.reset_r()

    # round
    def reset_r(self):
        self.slots = []
        self.particles = []
        self.result = None  # (potion id, s left)
        self.brewing_t = 0.0
        self.coins = 0
        self.streak = 0
        self.best_streak = 0
        self.lives = S_LIVES
        self.customer = None
        self.next_ct = 0.5
        self.msg = ""
        self.msg_t = 0.0
        self.dummy_t = 0.0
        self.dummy_color = (255, 255, 255)

    def start_mode(self, mode):
        self.reset_r()
        self.mode = mode
        self.state = "play"
        self.book = False

    def say(self, txt, secs=2.5):
        self.msg, self.msg_t = txt, secs

    def combo_mult(self):
        return COMBO_M[min(self.streak, len(COMBO_M) - 1)]

    # brewing
    def current_p(self):
        return RECIPES.get(R(*self.slots), "sludge")

    def start_brew(self):
        if self.brewing_t > 0:
            return
        if len(self.slots) < MIN:
            self.say(f"You need to add atleast {MIN} ingredients bro", 1.5)
            return
        self.brewing_t = BREW_T

    def finish_b(self):
        pid = self.current_p()
        self.slots = []
        self.result = (pid, 3.0)
        if pid != "sludge" and pid not in self.discover:
            self.discover.add(pid)
            save_d(self.discover)
            self.say(f"New recipe: {POTIONS[pid][0]}! nice", 2.5)
        if self.mode == "practice":
            self.dummy_t = 2.0
            self.dummy_color = POTIONS[pid][1]
            self.say(EFFECTS[pid], 3.0)
        elif self.customer:
            self.server(pid)

    # customer
    def spwn_customer(self):
        cfg = DIFF[self.mode]
        is_boss = random.random() < cfg["boss_chance"]
        count = BOSS_P if is_boss else random.randint(*cfg["potions"])
        orders = random.sample(ORDERABLE, count)  # no rep
        patience = PATIENCE + EXTRA_P * (count - 1)
        self.customer = {
            "idx": random.randrange(len(CUSTOMERS)),
            "orders": orders,
            "done": [False] * count,
            "patience": patience,
            "max": patience,
            "boss": is_boss,
        }
        if is_boss:
            self.say("A WILD BOSS HAS APPEARED!", 2.5)

    def customer_name(self):
        c = self.customer
        return "Boss" if c["boss"] else CUSTOMERS[c["idx"]][0]

    def server(self, pid):
        c = self.customer
        name = self.customer_name()
        for i, want in enumerate(c["orders"]):
            if not c["done"][i] and want == pid:
                c["done"][i] = True
                self.streak += 1
                self.best_streak = max(self.best_streak, self.streak)
                mult = self.combo_mult()
                base = 10 + int(10 * max(0.0, c["patience"]) / c["max"])
                gain = int(base * mult)
                tag = f" x{mult:g}" if mult > 1 else ""
                self.coins += gain
                if all(c["done"]):
                    extra = BOSS_B if c["boss"] else 0
                    self.coins += extra
                    self.say(f"{name}: PERFECTO! +{gain +extra} coins{tag} (good job!)")
                    self.customer_leaves()
                else:
                    left = c["done"].count(False)
                    self.say(f"{name}: nice! {left} more to go! (+{gain}{tag})")
                return
        # wrong potion
        self.streak = 0
        self.lives -= 1
        self.say(f"{name}: What the hell is this? I didn't order this!")
        if WRONG_LEAVES:
            self.customer_leaves()
        elif self.lives <= 0:
            self.state = "gameover"

    def customer_leaves(self):
        self.customer = None
        self.next_ct = NEXT_CD
        if self.lives <= 0:
            self.state = "gameover"

    # input
    def click(self, x, y):
        if self.state != "play" or self.brewing_t > 0:
            return
        for name, rect in ING_RECTS.items():
            if rect.collidepoint(x, y):
                if name not in self.slots and len(self.slots) < MAX:
                    self.slots.append(name)
                return
        for i, rect in enumerate(SLOT_R):
            if rect.collidepoint(x, y) and i < len(self.slots):
                self.slots.pop(i)
                return
        if BREW_RECT.collidepoint(x, y):
            self.start_brew()
        elif CLEAR_RECT.collidepoint(x, y):
            self.slots = []

    def key(self, k):
        if k == pygame.K_ESCAPE:
            if self.book:
                self.book = False
            elif self.state == "menu":
                pygame.quit()
                sys.exit()
            else:
                self.state = "menu"
        elif k == pygame.K_b:
            self.book = not self.book
        elif self.state in ("menu", "gameover"):
            if k == pygame.K_1:
                self.start_mode("normal")
            elif k == pygame.K_2:
                self.start_mode("hard")
            elif k == pygame.K_3:
                self.start_mode("practice")
            elif k == pygame.K_RETURN and self.state == "gameover":
                self.start_mode(self.mode)  # retry same mode
        elif k in (pygame.K_SPACE, pygame.K_RETURN):
            self.start_brew()
        elif k == pygame.K_c and self.brewing_t <= 0:
            self.slots = []

    # update
    def update(self, dt):
        self.t += dt
        if self.msg_t > 0:
            self.msg_t -= dt
        if self.dummy_t > 0:
            self.dummy_t -= dt
        if self.result:
            pid, left = self.result
            left -= dt
            self.result = (pid, left) if left > 0 else None
        if self.brewing_t > 0:
            self.brewing_t -= dt
            if self.brewing_t <= 0:
                self.finish_b()
        # bubbles
        rate = 0.5 if self.brewing_t > 0 else 0.07
        if random.random() < rate:
            self.particles.append(
                {
                    "x": CAULDRON_POS[0] + random.randint(14, 50),
                    "y": CAULDRON_POS[1] + 20.0,
                    "vy": random.uniform(14, 30),
                    "r": random.choice((1, 1, 2)),
                    "life": random.uniform(0.6, 1.2),
                }
            )
        for p in self.particles:
            p["y"] -= p["vy"] * dt
            p["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]

        # customers (not practice mode)
        if self.state == "play" and self.mode != "practice":
            if self.customer is None:
                self.next_ct -= dt
                if self.next_ct <= 0:
                    self.spwn_customer()
            elif self.brewing_t <= 0:
                self.customer["patience"] -= dt
                if self.customer["patience"] <= 0:
                    self.streak = 0
                    self.lives -= 1
                    self.say(
                        f"{self.customer_name()} got tired of waiting! DO IT FASTER"
                    )
                    self.play("fail")
                    self.customer_leaves()
