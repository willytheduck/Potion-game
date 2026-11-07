from settings import MIN, MAX, BOSS_P

INGREDIENTS = [
    "mushroom",
    "pumpkin",
    "lolipop",
    "bone", 
    "skull", 
    "herb", 
    "slime",
    "crystal",
]

POTIONS = {
    "healing": ("Healing", (230,70,90)),
    "speed": ("Speed", (250,210,60)),
    "night_vision": ("Night Vision", (120,90,230)),
    "strength": ("Strength", (240,130,40)),
    "invisibility": ("Invisibility", (150,220,230)),
    "love": ("Love", (255,130,200)),
    "sludge": ("Murky Sludge", (95,85,60)), #failed
}

ORDERABLE = [p for p in POTIONS if p != "sludge"]

def R(*ings):
    #mushroom+pumpkin = pumpkin+mushroom
    return tuple(sorted(ings))

RECIPES = {
    R("mushroom", "pumpkin"): "healing",
    R("mushroom", "lolipop"): "love",
    R("pumpkin", "lolipop"): "night_vision",
    R("herb", "lolipop", "slime"): "speed",
    R("bone", "skull", "pumpkin"): "strength",
    R("crystal", "slime", "herb", "mushroom"): "invisibility",
}

EFFECTS = {
    "healing": "The dummy: I feel refreshed...!",
    "speed": "The dummy: I AM SPEEEED!",
    "night_vision": "The dummy: I CAN SEE EVERYTHING IN 4K EVEN IN THE DARK!",
    "strength": "The dummy: I FEEL POWAFULL!",
    "invisibility": "The dummy: boooo......",
    "love": "The dummy: wanna go out someday....?",
    "sludge": "The dummy: ew, the hell is that.",
}

CUSTOMERS = [ # A WITCH BURN EM
    ("Green Witch", (110,190,60)),
    ("Blue Witch", (100,170,230)),
    ("Pink Witch", (230,110,170)),
]

#for catching typos
for _key, _pid in RECIPES.items():
    assert _pid in POTIONS, f"unknown potion id {_pid}"
    assert MIN <= len(_key) <= MAX, f"bad size {_key}"
    for _ing in _key:
        assert _ing in INGREDIENTS, f"unknown ingredient {_ing}"
assert len(ORDERABLE) >= BOSS_P, "need at least as many potion as a boss orders"