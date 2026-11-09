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
    SCORES,
    HINT_C,
    HINT_T,
    HINT_RECT,
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


def load_s():
    try:
        with open(SCORES, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    out = {}
    for m in ("normal", "hard"):
        d = data.get(m, {}) if isinstance(data, dict) else {}
        try:
            out[m] = {
                "coins": int(d.get("coins", 0)),
                "streak": int(d.get("streak", 0)),
            }
        except (TypeError, ValueError, AttributeError):
            out[m] = {"coins": 0, "streak": 0}
    return out


def save_scores(scores):
    try:
        with open(SCORES, "w", encoding="utf-8") as f:
            json.dump(scores, f)
    except OSError:
        pass


class Game:
    def __init__(self, art):
        self.art = art
        self.play = art.play
        self.discover = load_d()
        self.scores = load_s()
        self.state = "menu"  # menu/play/gameover
        self.mode = "normal"  # difficulty
        self.t = 0.0
        self.book = False
        self.reset_r()
        self.muted = False
        art.start_music(self.muted)

    # round
    def reset_r(self):
        self.slots = []
        self.particles = []
        self.result = None  # (potion id, s left)
        self.brewing_t = 0.0
        self.coins = 0
        self.streak = 0
        self.best_streak = 0
        self.new_bc = False
        self.new_bs = False
        self.hint_pid = None
        self.hint_shown = []
        self.hint_t = 0.0
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
        self.hint_t = 0.0  # glow off once brew
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
            self.end_game()

    def customer_leaves(self):
        self.customer = None
        self.next_ct = NEXT_CD
        self.hint_t = 0.0
        if self.lives <= 0:
            self.end_game()

    def record_score(self):
        if self.mode == "practice":
            return
        best = self.scores[self.mode]
        self.new_bc = self.coins > best["coins"]
        self.new_bs = self.best_streak > best["streak"]
        if self.new_bc:
            best["coins"] = self.coins
        if self.new_bs:
            best["streak"] = self.best_streak
        if self.new_bc or self.new_bs:
            save_scores(self.scores)

    def end_game(self):
        self.state = "gameover"
        self.record_score()

    # hint
    def use_hint(self):
        if self.state != "play" or self.brewing_t > 0:
            return
        if self.mode == "practice":
            todo = [p for p in ORDERABLE if p not in self.discover]
            if not todo:
                self.say("what? You already know all the recipe.", 2.0)
                return
            pid = self.hint_pid if self.hint_pid in todo else random.choice(todo)
            cost = 0
        else:
            c = self.customer
            if c is None:
                self.say("No customer right now", 1.5)
                return
            open_orders = [p for i, p in enumerate(c["orders"]) if not c["done"][i]]
            pid = open_orders[0]  # hint for first order still open
            cost = HINT_C
        key = next(k for k, v in RECIPES.items() if v == pid)
        if pid != self.hint_pid:  # new -> start hint over
            self.hint_pid = pid
            self.hint_shown = []
        left = [i for i in key if i not in self.hint_shown]
        if not left:  # nothing new, so it's free
            self.hint_t = HINT_T
            self.say(f"HM. You've seen all the ingredients for {POTIONS[pid][0]}", 2.0)
            return
        if self.coins < cost:
            self.say(f"A hint costs {cost} coins (better grind)", 1.5)
            return
        ing = random.choice(left)
        self.coins -= cost
        self.hint_shown.append(ing)
        self.hint_t = HINT_T
        self.say(
            f"Hint: {POTIONS[pid][0]} needs {ing.replace('_', ' ')}"
            f"({len(self.hint_shown)}/{len(key)})",
            3.0,
        )

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
        elif HINT_RECT.collidepoint(x, y):
            self.use_hint()

    def key(self, k):
        if k == pygame.K_ESCAPE:
            if self.book:
                self.book = False
            elif self.state == "menu":
                pygame.quit()
                sys.exit()
            else:
                if self.state == "play":
                    self.record_score()
                self.state = "menu"
        elif k == pygame.K_b:
            self.book = not self.book
        elif k == pygame.K_m:
            self.muted = not self.muted
            self.art.set_muted(self.muted)
            self.say("Music off" if self.muted else "Music on", 1.5)
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
        elif k == pygame.K_h:
            self.use_hint()

    # update
    def update(self, dt):
        self.t += dt
        if self.msg_t > 0:
            self.msg_t -= dt
        if self.dummy_t > 0:
            self.dummy_t -= dt
        if self.hint_t > 0:
            self.hint_t -= dt
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
