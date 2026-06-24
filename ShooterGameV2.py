import pygame
import random
import math
import os

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

WIDTH, HEIGHT = 1200, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("VOID BREAKER")
pygame.mouse.set_visible(True)

clock = pygame.time.Clock()
font_xs  = pygame.font.SysFont("consolas", 18)
font_sm  = pygame.font.SysFont("consolas", 24)
font_md  = pygame.font.SysFont("consolas", 32)
font_lg  = pygame.font.SysFont("consolas", 52)
font_xl  = pygame.font.SysFont("consolas", 80)
font_xxl = pygame.font.SysFont("consolas", 110)

# ── COLORS ────────────────────────────────────────────────────────────────────
BLACK     = (8,   8,   18)
DARK      = (18,  18,  35)
DARKER    = (12,  12,  25)
WHITE     = (220, 225, 255)
DIM       = (100, 110, 150)
RED       = (220, 55,  55)
DKRED     = (100, 15,  15)
GREEN     = (55,  210, 100)
DKGREEN   = (15,  80,  35)
BLUE      = (55,  140, 255)
DKBLUE    = (15,  35,  100)
CYAN      = (55,  220, 220)
YELLOW    = (255, 230, 55)
ORANGE    = (255, 140, 35)
PURPLE    = (175, 75,  255)
PINK      = (255, 75,  175)
TEAL      = (35,  200, 160)
GOLD      = (255, 200, 50)

# ── SOUND GENERATION ──────────────────────────────────────────────────────────
def make_sound(freq, duration_ms, wave="sine", volume=0.3, decay=True):
    sample_rate = 22050
    n = int(sample_rate * duration_ms / 1000)
    buf = []
    for i in range(n):
        t = i / sample_rate
        if wave == "sine":
            v = math.sin(2 * math.pi * freq * t)
        elif wave == "square":
            v = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        elif wave == "noise":
            v = random.uniform(-1, 1)
        elif wave == "sweep":
            f = freq * (1 + 2 * (1 - i/n))
            v = math.sin(2 * math.pi * f * t)
        else:
            v = math.sin(2 * math.pi * freq * t)
        if decay:
            v *= max(0, 1 - i / n)
        v = int(v * volume * 32767)
        v = max(-32768, min(32767, v))
        buf.append(v)
    stereo = []
    for s in buf:
        stereo.append(s)
        stereo.append(s)
    arr = __import__("array").array("h", stereo)
    snd = pygame.sndarray.make_sound(__import__("numpy").array(stereo, dtype="int16").reshape(-1, 2))
    return snd

try:
    import numpy as np
    SFX = {
        "shoot":    make_sound(800,  60,  "sine",   0.15),
        "shoot_sg": make_sound(200,  90,  "noise",  0.25),
        "shoot_lz": make_sound(1200, 40,  "sweep",  0.2),
        "shoot_rp": make_sound(600,  35,  "square", 0.1),
        "explode":  make_sound(120,  200, "noise",  0.35),
        "hit":      make_sound(300,  80,  "noise",  0.2),
        "powerup":  make_sound(880,  300, "sine",   0.3),
        "boss_hit": make_sound(80,   150, "noise",  0.3),
        "dash":     make_sound(400,  120, "sweep",  0.2),
        "levelup":  make_sound(660,  400, "sine",   0.3),
    }
    SOUND_ON = True
except Exception:
    SFX = {}
    SOUND_ON = False

def play(name):
    if SOUND_ON and name in SFX:
        SFX[name].play()

# ── WEAPONS ───────────────────────────────────────────────────────────────────
WEAPONS = {
    "pistol":  {"name": "PISTOL",  "fire_rate": 10, "speed": 14, "damage": 1,   "spread": 0,    "count": 1, "color": YELLOW, "sfx": "shoot"},
    "shotgun": {"name": "SHOTGUN", "fire_rate": 28, "speed": 10, "damage": 1,   "spread": 0.38, "count": 6, "color": ORANGE, "sfx": "shoot_sg"},
    "laser":   {"name": "LASER",   "fire_rate": 4,  "speed": 22, "damage": 2,   "spread": 0,    "count": 1, "color": CYAN,   "sfx": "shoot_lz"},
    "rapid":   {"name": "RAPID",   "fire_rate": 3,  "speed": 15, "damage": 1,   "spread": 0.06, "count": 1, "color": PINK,   "sfx": "shoot_rp"},
    "plasma":  {"name": "PLASMA",  "fire_rate": 18, "speed": 9,  "damage": 4,   "spread": 0,    "count": 1, "color": PURPLE, "sfx": "shoot_lz"},
}

WEAPON_ORDER = ["pistol", "shotgun", "laser", "rapid", "plasma"]

# ── ENEMY TYPES ───────────────────────────────────────────────────────────────
ENEMY_TYPES = {
    "grunt":   {"color": RED,    "radius": 18, "base_speed": 1.8, "base_health": 1, "damage": 8,  "score": 1,  "shoots": False, "xp": 10},
    "scout":   {"color": ORANGE, "radius": 13, "base_speed": 3.2, "base_health": 1, "damage": 6,  "score": 2,  "shoots": False, "xp": 15},
    "brute":   {"color": DKRED,  "radius": 30, "base_speed": 1.0, "base_health": 5, "damage": 20, "score": 4,  "shoots": False, "xp": 30},
    "shooter": {"color": PURPLE, "radius": 16, "base_speed": 1.3, "base_health": 2, "damage": 6,  "score": 3,  "shoots": True,  "xp": 20},
    "specter": {"color": TEAL,   "radius": 14, "base_speed": 2.5, "base_health": 1, "damage": 10, "score": 3,  "shoots": True,  "xp": 20},
}

def get_wave_pool(wave):
    if wave <= 2:   return ["grunt"]
    if wave <= 4:   return ["grunt", "scout"]
    if wave <= 6:   return ["grunt", "scout", "brute"]
    if wave <= 9:   return ["grunt", "scout", "brute", "shooter"]
    return list(ENEMY_TYPES.keys())

# ── ENEMY SPEED CAP ───────────────────────────────────────────────────────────
MAX_ENEMY_SPEED = 5.5   # never faster than player base speed

# ── UPGRADE DEFINITIONS ───────────────────────────────────────────────────────
UPGRADES = [
    {"key": pygame.K_1, "label": "SPEED",      "attr": "speed_level",     "color": GREEN,  "desc": "Move +1 faster",        "max": 8},
    {"key": pygame.K_2, "label": "DAMAGE",     "attr": "damage_level",    "color": RED,    "desc": "Deal x1.4 damage",      "max": 8},
    {"key": pygame.K_3, "label": "MAX HP",     "attr": "health_level",    "color": PINK,   "desc": "+30 max health",        "max": 8},
    {"key": pygame.K_4, "label": "FIRE RATE",  "attr": "firerate_level",  "color": ORANGE, "desc": "Shoot faster",          "max": 8},
    {"key": pygame.K_5, "label": "ARMOR",      "attr": "armor_level",     "color": CYAN,   "desc": "-10% damage taken",     "max": 5},
    {"key": pygame.K_6, "label": "REGEN",      "attr": "regen_level",     "color": TEAL,   "desc": "+1 HP/sec",             "max": 5},
]

def upgrade_cost(level):
    return level  # cost = current level

# ── RESET ─────────────────────────────────────────────────────────────────────
def reset_game():
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
              random.uniform(0.3, 2.0), random.uniform(0.2, 0.8)) for _ in range(160)]
    return {
        "player_x": WIDTH // 2,
        "player_y": HEIGHT // 2,
        "health": 100,
        "max_health": 100,
        "score": 0,
        "xp": 0,
        "player_level": 1,
        "xp_to_next": 100,
        "wave": 1,
        "kills": 0,
        "bullets": [],
        "enemy_bullets": [],
        "enemies": [],
        "particles": [],
        "powerups": [],
        "boss": None,
        "spawn_timer": 0,
        "shoot_timer": 0,
        "dash_timer": 0,
        "dash_cooldown": 0,
        "dash_active": 0,
        "invincible_timer": 0,
        "screen_shake": 0,
        "weapon": "pistol",
        "weapon_timer": 0,
        "regen_timer": 0,
        # Upgrades
        "speed_level": 1,
        "damage_level": 1,
        "health_level": 1,
        "firerate_level": 1,
        "armor_level": 0,
        "regen_level": 0,
        "upgrade_points": 2,
        # State
        "game_over": False,
        "in_shop": False,
        "shop_paused": False,
        "between_waves": False,
        "between_wave_timer": 0,
        "boss_wave": False,
        "wave_score_threshold": 25,
        "floaters": [],        # floating damage/score numbers
        "combo": 0,
        "combo_timer": 0,
        "background_stars": stars,
        "grid_offset": 0,
        "time": 0,
    }

game = reset_game()
high_score = 0
high_wave   = 1

# ── HELPERS ───────────────────────────────────────────────────────────────────
def clamp(v, lo, hi): return max(lo, min(hi, v))

def player_speed():
    return 5 + game["speed_level"] * 1.2

def player_damage_mult():
    return 1.0 + (game["damage_level"] - 1) * 0.4

def armor_reduction():
    return 1.0 - game["armor_level"] * 0.10

def spawn_floater(x, y, text, color=WHITE, size=font_sm):
    game["floaters"].append({
        "x": x + random.randint(-15, 15),
        "y": y,
        "text": text,
        "color": color,
        "life": 55,
        "max_life": 55,
        "vy": -1.5,
    })

def add_xp(amount):
    game["xp"] += amount
    while game["xp"] >= game["xp_to_next"]:
        game["xp"] -= game["xp_to_next"]
        game["player_level"] += 1
        game["xp_to_next"] = int(game["xp_to_next"] * 1.4)
        game["upgrade_points"] += 2
        spawn_floater(game["player_x"], game["player_y"] - 30, "LEVEL UP! +2 pts", GOLD)
        play("levelup")

def apply_damage(amount):
    reduced = int(amount * armor_reduction())
    game["health"] -= reduced
    game["health"] = max(0, game["health"])
    return reduced

def spawn_enemy():
    side = random.randint(0, 3)
    margin = 60
    if side == 0:   x, y = random.randint(0, WIDTH), -margin
    elif side == 1: x, y = WIDTH + margin, random.randint(0, HEIGHT)
    elif side == 2: x, y = random.randint(0, WIDTH), HEIGHT + margin
    else:           x, y = -margin, random.randint(0, HEIGHT)

    etype = random.choice(get_wave_pool(game["wave"]))
    t = ENEMY_TYPES[etype]
    # Speed scales with wave but is capped
    spd = min(t["base_speed"] + game["wave"] * 0.12, MAX_ENEMY_SPEED)
    hp  = t["base_health"] + game["wave"] // 3
    game["enemies"].append({
        "x": x, "y": y, "type": etype,
        "speed": spd, "health": hp, "max_health": hp,
        "shoot_timer": random.randint(0, 80),
        "radius": t["radius"], "color": t["color"],
        "damage": t["damage"], "score": t["score"],
        "shoots": t["shoots"], "xp": t["xp"],
        "wobble": random.uniform(0, math.pi * 2),
    })

def spawn_boss(wave):
    hp = 60 + wave * 15
    game["boss"] = {
        "x": WIDTH // 2, "y": -100,
        "health": hp, "max_health": hp,
        "shoot_timer": 0, "phase": 1,
        "angle": 0, "orbit_r": 280,
        "wave": wave,
    }

def create_explosion(x, y, color=YELLOW, count=20, speed_max=7):
    for _ in range(count):
        a   = random.uniform(0, math.pi * 2)
        spd = random.uniform(1, speed_max)
        game["particles"].append({
            "x": x, "y": y,
            "vx": math.cos(a) * spd,
            "vy": math.sin(a) * spd,
            "life": random.randint(18, 50),
            "max_life": 50,
            "color": color,
            "size": random.randint(2, 6),
            "type": "spark",
        })
    # ring pulse
    for i in range(12):
        a = i * math.pi * 2 / 12
        game["particles"].append({
            "x": x, "y": y,
            "vx": math.cos(a) * 3,
            "vy": math.sin(a) * 3,
            "life": 20, "max_life": 20,
            "color": WHITE, "size": 3, "type": "ring",
        })

def fire_weapon(px, py, angle):
    w   = WEAPONS[game["weapon"]]
    dmg = w["damage"] * player_damage_mult()
    for _ in range(w["count"]):
        a  = angle + random.uniform(-w["spread"], w["spread"])
        vx = math.cos(a) * w["speed"]
        vy = math.sin(a) * w["speed"]
        game["bullets"].append({
            "x": px, "y": py, "vx": vx, "vy": vy,
            "damage": dmg, "color": w["color"],
            "weapon": game["weapon"],
            "trail": [],
        })
    play(w["sfx"])

# ── DRAW HELPERS ──────────────────────────────────────────────────────────────
def draw_bar(surf, x, y, w, h, val, maxv, fill, bg=DARK, border=DIM, radius=4):
    pygame.draw.rect(surf, bg, (x, y, w, h), border_radius=radius)
    fw = int(w * clamp(val / max(maxv, 1), 0, 1))
    if fw > 0:
        pygame.draw.rect(surf, fill, (x, y, fw, h), border_radius=radius)
    pygame.draw.rect(surf, border, (x, y, w, h), 1, border_radius=radius)

def draw_panel(surf, x, y, w, h, alpha=200, color=DARK):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((*color, alpha))
    surf.blit(s, (x, y))
    pygame.draw.rect(surf, DIM, (x, y, w, h), 1, border_radius=8)

def draw_background(surf, t, offset):
    surf.fill(BLACK)
    # Grid
    gc = (20, 22, 45)
    sp = 70
    off = int(offset) % sp
    for x in range(-sp + off, WIDTH + sp, sp):
        pygame.draw.line(surf, gc, (x, 0), (x, HEIGHT))
    for y in range(-sp + off, HEIGHT + sp, sp):
        pygame.draw.line(surf, gc, (0, y), (WIDTH, y))
    # Stars with twinkle
    for sx, sy, br, twk in game["background_stars"]:
        bri = int(abs(math.sin(t * twk * 0.02)) * br * 90 + 20)
        bri = clamp(bri, 10, 110)
        pygame.draw.circle(surf, (bri, bri, bri + 25), (int(sx), int(sy)), 1)

def draw_hud(surf):
    # Health
    draw_bar(surf, 20, 20, 260, 20, game["health"], game["max_health"], GREEN, DKRED)
    hp_txt = font_xs.render(f"HP {game['health']}/{game['max_health']}", True, WHITE)
    surf.blit(hp_txt, (286, 22))

    # XP bar
    draw_bar(surf, 20, 46, 260, 8, game["xp"], game["xp_to_next"], GOLD, DARKER)
    lv_txt = font_xs.render(f"LV {game['player_level']}  XP {game['xp']}/{game['xp_to_next']}", True, GOLD)
    surf.blit(lv_txt, (20, 58))

    # Score / wave
    surf.blit(font_md.render(f"SCORE  {game['score']:>6}", True, WHITE), (20, 80))
    surf.blit(font_sm.render(f"WAVE   {game['wave']:>3}", True, CYAN),  (20, 118))
    surf.blit(font_xs.render(f"BEST   {high_score}",      True, DIM),   (20, 146))
    surf.blit(font_xs.render(f"KILLS  {game['kills']}",   True, DIM),   (20, 166))

    # Weapon
    w = WEAPONS[game["weapon"]]
    wtxt = font_md.render(f"[ {w['name']} ]", True, w["color"])
    surf.blit(wtxt, (WIDTH - wtxt.get_width() - 20, 20))
    if game["weapon_timer"] > 0:
        secs = math.ceil(game["weapon_timer"] / 60)
        draw_bar(surf, WIDTH - wtxt.get_width() - 20, 56, wtxt.get_width(), 6, game["weapon_timer"], 600, w["color"])
        surf.blit(font_xs.render(f"{secs}s", True, w["color"]), (WIDTH - 40, 64))

    # Dash bar
    cd = 60
    if game["dash_cooldown"] <= 0:
        surf.blit(font_xs.render("DASH  ready  [SPACE]", True, BLUE), (20, HEIGHT - 38))
    else:
        draw_bar(surf, 20, HEIGHT - 38, 160, 10, cd - game["dash_cooldown"], cd, BLUE, DKBLUE)
        surf.blit(font_xs.render("DASH", True, DIM), (188, HEIGHT - 40))

    # Upgrade points badge
    if game["upgrade_points"] > 0:
        badge = font_sm.render(f"TAB  shop  [{game['upgrade_points']} pts]", True, YELLOW)
        bx = WIDTH // 2 - badge.get_width() // 2
        pulse = int(abs(math.sin(game["time"] * 0.05)) * 30)
        col = (clamp(200 + pulse, 0, 255), clamp(180 + pulse, 0, 255), 55)
        surf.blit(font_sm.render(f"TAB  shop  [{game['upgrade_points']} pts]", True, col), (bx, HEIGHT - 40))

    # Combo
    if game["combo"] >= 3:
        ct = font_md.render(f"x{game['combo']} COMBO", True, GOLD)
        surf.blit(ct, (WIDTH // 2 - ct.get_width() // 2, HEIGHT - 75))

    # Regen indicator
    if game["regen_level"] > 0:
        surf.blit(font_xs.render(f"REGEN +{game['regen_level']}/s", True, TEAL), (20, 188))


def draw_shop(surf):
    draw_panel(surf, 0, 0, WIDTH, HEIGHT, 210, BLACK)

    title = font_xl.render("UPGRADE SHOP", True, YELLOW)
    surf.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    pts = font_lg.render(f"{game['upgrade_points']}  upgrade points", True, CYAN)
    surf.blit(pts, (WIDTH // 2 - pts.get_width() // 2, 120))

    cols = 3
    card_w, card_h = 330, 210
    total_w = cols * card_w + (cols - 1) * 18
    start_x = WIDTH // 2 - total_w // 2
    start_y = 185

    for i, upg in enumerate(UPGRADES):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + 18)
        y = start_y + row * (card_h + 14)

        level    = game[upg["attr"]]
        maxed    = level >= upg["max"]
        cost     = upgrade_cost(level)
        can_buy  = game["upgrade_points"] >= cost and not maxed

        bg    = (28, 32, 58) if can_buy else (18, 18, 30)
        border = upg["color"] if can_buy else (50, 50, 75)
        draw_panel(surf, x, y, card_w, card_h, 230, (bg[0], bg[1], bg[2]))
        pygame.draw.rect(surf, border, (x, y, card_w, card_h), 2, border_radius=8)

        # Key hint
        key_s = font_lg.render(str(i + 1), True, upg["color"] if can_buy else DIM)
        surf.blit(key_s, (x + 14, y + 10))

        # Label
        surf.blit(font_md.render(upg["label"], True, WHITE), (x + 14, y + 72))
        surf.blit(font_xs.render(upg["desc"], True, DIM),    (x + 14, y + 108))

        # Level pips
        pip_y = y + 140
        for p in range(upg["max"]):
            col2 = upg["color"] if p < level else (35, 35, 55)
            pygame.draw.rect(surf, col2, (x + 14 + p * 22, pip_y, 16, 8), border_radius=3)

        # Cost / maxed
        if maxed:
            surf.blit(font_sm.render("MAXED", True, GOLD), (x + 14, y + 162))
        else:
            cost_col = YELLOW if can_buy else (90, 90, 110)
            surf.blit(font_sm.render(f"cost: {cost} pt{'s' if cost!=1 else ''}", True, cost_col), (x + 14, y + 162))

    hint = font_sm.render("1-6 to upgrade     TAB / ESC to resume", True, DIM)
    surf.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 48))


def draw_game_over(surf):
    draw_panel(surf, 0, 0, WIDTH, HEIGHT, 195, BLACK)
    go = font_xxl.render("GAME OVER", True, RED)
    surf.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT // 2 - 140))
    surf.blit(font_lg.render(f"SCORE  {game['score']}      WAVE  {game['wave']}", True, WHITE),
              (WIDTH // 2 - 280, HEIGHT // 2 - 20))
    surf.blit(font_md.render(f"ALL-TIME BEST:  {high_score}  (wave {high_wave})", True, GOLD),
              (WIDTH // 2 - 270, HEIGHT // 2 + 48))
    surf.blit(font_md.render(f"KILLS: {game['kills']}   LEVEL: {game['player_level']}", True, DIM),
              (WIDTH // 2 - 180, HEIGHT // 2 + 90))
    r = font_md.render("R  —  restart", True, (160, 165, 210))
    surf.blit(r, (WIDTH // 2 - r.get_width() // 2, HEIGHT // 2 + 145))


def draw_between_wave(surf):
    draw_panel(surf, WIDTH//2 - 260, HEIGHT//2 - 60, 520, 120, 200, DARKER)
    next_wave = game["wave"] + 1
    is_boss = next_wave % 5 == 0
    label = f"BOSS INCOMING  —  WAVE {next_wave}" if is_boss else f"WAVE {next_wave}"
    color = RED if is_boss else CYAN
    t = font_lg.render(label, True, color)
    surf.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 40))
    pct = 1 - game["between_wave_timer"] / 180
    draw_bar(surf, WIDTH//2 - 200, HEIGHT//2 + 30, 400, 10, pct, 1.0, color, DARKER)

# ── MAIN LOOP ─────────────────────────────────────────────────────────────────
running = True

while running:
    dt = clock.tick(60)
    game["time"] += 1

    # ── EVENTS ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # Restart
            if game["game_over"] and event.key == pygame.K_r:
                game = reset_game()
                continue

            # Shop key presses (handle FIRST, before toggle)
            if game["in_shop"]:
                if event.key in (pygame.K_ESCAPE, pygame.K_TAB, pygame.K_e):
                    game["in_shop"] = False
                    game["shop_paused"] = False
                else:
                    for upg in UPGRADES:
                        if event.key == upg["key"]:
                            level = game[upg["attr"]]
                            cost  = upgrade_cost(level)
                            if game["upgrade_points"] >= cost and level < upg["max"]:
                                game["upgrade_points"] -= cost
                                game[upg["attr"]] += 1
                                if upg["attr"] == "health_level":
                                    game["max_health"] += 30
                                    game["health"] = min(game["health"] + 30, game["max_health"])
                                play("levelup")
            else:
                # Toggle shop open
                if not game["game_over"] and not game["between_waves"]:
                    if event.key in (pygame.K_TAB, pygame.K_e):
                        game["in_shop"] = True
                        game["shop_paused"] = True
                # Dash on SPACE keydown (reliable vs held-key check)
                if event.key == pygame.K_SPACE and not game["game_over"] and not game["between_waves"]:
                    if game["dash_cooldown"] <= 0:
                        game["dash_active"] = 8

    # ── PAUSED IN SHOP ────────────────────────────────────────────────────────
    if game["shop_paused"] or game["in_shop"]:
        draw_surface = pygame.Surface((WIDTH, HEIGHT))
        draw_background(draw_surface, game["time"], game["grid_offset"])
        draw_hud(draw_surface)
        draw_shop(draw_surface)
        screen.blit(draw_surface, (0, 0))
        pygame.display.flip()
        continue

    if game["game_over"]:
        draw_surface = pygame.Surface((WIDTH, HEIGHT))
        draw_background(draw_surface, game["time"], game["grid_offset"])
        draw_game_over(draw_surface)
        screen.blit(draw_surface, (0, 0))
        pygame.display.flip()
        continue

    # ── BETWEEN WAVES ─────────────────────────────────────────────────────────
    if game["between_waves"]:
        game["between_wave_timer"] -= 1
        draw_surface = pygame.Surface((WIDTH, HEIGHT))
        draw_background(draw_surface, game["time"], game["grid_offset"])
        draw_hud(draw_surface)
        draw_between_wave(draw_surface)
        screen.blit(draw_surface, (0, 0))
        pygame.display.flip()
        if game["between_wave_timer"] <= 0:
            game["between_waves"] = False
            game["wave"] += 1
            if game["wave"] % 5 == 0:
                game["boss_wave"] = True
                spawn_boss(game["wave"])
        continue

    # ── GAMEPLAY UPDATE ───────────────────────────────────────────────────────
    game["grid_offset"] += 0.5
    if game["screen_shake"] > 0:
        game["screen_shake"] -= 1

    for timer in ["shoot_timer", "invincible_timer", "weapon_timer"]:
        if game[timer] > 0:
            game[timer] -= 1
    # Dash cooldown only counts down when not actively dashing
    if game["dash_active"] == 0 and game["dash_cooldown"] > 0:
        game["dash_cooldown"] -= 1

    # Weapon expiry
    if game["weapon_timer"] <= 0 and game["weapon"] != "pistol":
        game["weapon"] = "pistol"

    # HP regen
    if game["regen_level"] > 0:
        game["regen_timer"] += 1
        if game["regen_timer"] >= 60:
            game["regen_timer"] = 0
            game["health"] = min(game["max_health"], game["health"] + game["regen_level"])

    # Combo decay
    if game["combo_timer"] > 0:
        game["combo_timer"] -= 1
        if game["combo_timer"] <= 0:
            game["combo"] = 0

    px, py = game["player_x"], game["player_y"]

    # ── MOVEMENT ──────────────────────────────────────────────────────────────
    keys   = pygame.key.get_pressed()
    spd    = player_speed()
    dx, dy = 0, 0
    if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= spd
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += spd
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= spd
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += spd

    # Diagonal normalise
    if dx != 0 and dy != 0:
        dx *= 0.707
        dy *= 0.707

    # Dash — triggered by KEYDOWN event, lasts dash_active frames
    if game["dash_active"] > 0:
        game["dash_active"] -= 1
        if game["dash_cooldown"] == 0:
            # First frame: set cooldown and fire particles
            game["dash_cooldown"] = 60
            create_explosion(px, py, BLUE, count=10, speed_max=4)
            play("dash")
        # If no directional input, dash toward mouse
        if dx == 0 and dy == 0:
            mx2, my2 = pygame.mouse.get_pos()
            da = math.atan2(my2 - py, mx2 - px)
            dx = math.cos(da) * spd
            dy = math.sin(da) * spd
        dx *= 5.0
        dy *= 5.0

    game["player_x"] = clamp(px + dx, 22, WIDTH  - 22)
    game["player_y"] = clamp(py + dy, 22, HEIGHT - 22)
    px, py = game["player_x"], game["player_y"]

    # ── SHOOTING ──────────────────────────────────────────────────────────────
    fr_bonus = max(1, WEAPONS[game["weapon"]]["fire_rate"] - (game["firerate_level"] - 1) * 2)
    buttons  = pygame.mouse.get_pressed()
    if buttons[0] and game["shoot_timer"] <= 0:
        mx, my = pygame.mouse.get_pos()
        angle  = math.atan2(my - py, mx - px)
        fire_weapon(px, py, angle)
        game["shoot_timer"] = fr_bonus

    # ── SPAWN ENEMIES ─────────────────────────────────────────────────────────
    if not game["boss_wave"]:
        game["spawn_timer"] += 1
        spawn_delay = max(12, 65 - game["wave"] * 2)
        if game["spawn_timer"] >= spawn_delay:
            game["spawn_timer"] = 0
            count = 1 + (game["wave"] // 8)
            for _ in range(count):
                spawn_enemy()

    # Wave progression via score
    new_wave_threshold = game["wave_score_threshold"] + game["wave"] * 20
    if not game["boss_wave"] and game["score"] >= new_wave_threshold:
        game["wave_score_threshold"] = new_wave_threshold
        game["between_waves"] = True
        game["between_wave_timer"] = 180

    # ── PLAYER BULLETS ────────────────────────────────────────────────────────
    for b in game["bullets"][:]:
        b["trail"].append((int(b["x"]), int(b["y"])))
        if len(b["trail"]) > 5:
            b["trail"].pop(0)
        b["x"] += b["vx"]
        b["y"] += b["vy"]
        if b["x"] < -30 or b["x"] > WIDTH+30 or b["y"] < -30 or b["y"] > HEIGHT+30:
            if b in game["bullets"]: game["bullets"].remove(b)

    # ── ENEMY BULLETS ─────────────────────────────────────────────────────────
    for b in game["enemy_bullets"][:]:
        b["x"] += b["vx"]
        b["y"] += b["vy"]
        if b["x"] < 0 or b["x"] > WIDTH or b["y"] < 0 or b["y"] > HEIGHT:
            if b in game["enemy_bullets"]: game["enemy_bullets"].remove(b)
            continue
        if game["invincible_timer"] <= 0:
            if math.hypot(px - b["x"], py - b["y"]) < 20:
                dmg = apply_damage(b["damage"])
                spawn_floater(px, py - 20, f"-{dmg}", RED)
                game["invincible_timer"] = 22
                game["screen_shake"]     = 7
                play("hit")
                if b in game["enemy_bullets"]: game["enemy_bullets"].remove(b)

    # ── ENEMIES ───────────────────────────────────────────────────────────────
    for e in game["enemies"][:]:
        e["wobble"] += 0.05
        ddx = px - e["x"]
        ddy = py - e["y"]
        dist = math.hypot(ddx, ddy)
        if dist > 0:
            # Specter strafe sideways
            if e["type"] == "specter":
                perp_x = -ddy / dist
                perp_y =  ddx / dist
                straf  = math.sin(e["wobble"] * 2) * 1.5
                e["x"] += (ddx / dist * e["speed"] * 0.6 + perp_x * straf)
                e["y"] += (ddy / dist * e["speed"] * 0.6 + perp_y * straf)
            else:
                e["x"] += ddx / dist * e["speed"]
                e["y"] += ddy / dist * e["speed"]

        # Melee
        if dist < e["radius"] + 20 and game["invincible_timer"] <= 0:
            dmg = apply_damage(e["damage"])
            spawn_floater(px, py - 20, f"-{dmg}", RED)
            game["invincible_timer"] = 35
            game["screen_shake"]     = 9
            play("hit")

        # Shooter fires
        if e["shoots"]:
            e["shoot_timer"] += 1
            rate = 75 if e["type"] == "shooter" else 55
            if e["shoot_timer"] >= rate:
                e["shoot_timer"] = 0
                ang = math.atan2(py - e["y"], px - e["x"])
                if e["type"] == "specter":
                    for sp in [-0.2, 0, 0.2]:
                        game["enemy_bullets"].append({
                            "x": e["x"], "y": e["y"],
                            "vx": math.cos(ang+sp)*5,
                            "vy": math.sin(ang+sp)*5,
                            "damage": e["damage"],
                        })
                else:
                    game["enemy_bullets"].append({
                        "x": e["x"], "y": e["y"],
                        "vx": math.cos(ang)*4.5,
                        "vy": math.sin(ang)*4.5,
                        "damage": e["damage"],
                    })

        # Bullet collision
        for b in game["bullets"][:]:
            if b not in game["bullets"]: continue
            if math.hypot(b["x"] - e["x"], b["y"] - e["y"]) < e["radius"] + 5:
                e["health"] -= b["damage"]
                spawn_floater(e["x"], e["y"] - e["radius"] - 10,
                              f"{int(b['damage'])}", b["color"])
                if b["weapon"] != "laser" and b in game["bullets"]:
                    game["bullets"].remove(b)
                if e["health"] <= 0:
                    create_explosion(e["x"], e["y"], e["color"])
                    play("explode")
                    if e in game["enemies"]: game["enemies"].remove(e)
                    pts = e["score"]
                    game["combo"] += 1
                    game["combo_timer"] = 90
                    combo_bonus = max(1, game["combo"] // 3)
                    pts *= combo_bonus
                    game["score"]  += pts
                    game["kills"]  += 1
                    high_score = max(high_score, game["score"])
                    add_xp(e["xp"])
                    spawn_floater(e["x"], e["y"], f"+{pts}", GOLD)
                    # Powerup drop
                    if random.random() < 0.13:
                        pt = random.choice(["health","shotgun","laser","rapid","plasma","shield"])
                        game["powerups"].append({"x": e["x"], "y": e["y"], "type": pt, "bob": 0})
                    # Upgrade point
                    if random.random() < 0.06:
                        game["upgrade_points"] += 1
                        spawn_floater(e["x"], e["y"]-30, "+1 UPGRADE PT", CYAN)
                    break

    # ── BOSS ──────────────────────────────────────────────────────────────────
    boss = game["boss"]
    if boss:
        boss["angle"] += 0.018
        # Orbit pattern
        tx = WIDTH // 2 + math.cos(boss["angle"]) * boss["orbit_r"]
        ty = 160 + math.sin(boss["angle"] * 0.6) * 100
        boss["x"] += (tx - boss["x"]) * 0.025
        boss["y"] += (ty - boss["y"]) * 0.025

        if boss["health"] < boss["max_health"] * 0.5:
            boss["phase"] = 2
        if boss["health"] < boss["max_health"] * 0.2:
            boss["phase"] = 3

        boss["shoot_timer"] += 1
        rates = {1: 45, 2: 28, 3: 18}
        if boss["shoot_timer"] >= rates[boss["phase"]]:
            boss["shoot_timer"] = 0
            ang = math.atan2(py - boss["y"], px - boss["x"])
            if boss["phase"] == 1:
                game["enemy_bullets"].append({"x": boss["x"], "y": boss["y"],
                    "vx": math.cos(ang)*6, "vy": math.sin(ang)*6, "damage": 12})
            elif boss["phase"] == 2:
                for sp in [-0.3, -0.15, 0, 0.15, 0.3]:
                    game["enemy_bullets"].append({"x": boss["x"], "y": boss["y"],
                        "vx": math.cos(ang+sp)*7, "vy": math.sin(ang+sp)*7, "damage": 9})
            else:
                # Ring of death
                for i in range(12):
                    a2 = i * math.pi * 2 / 12 + boss["angle"]
                    game["enemy_bullets"].append({"x": boss["x"], "y": boss["y"],
                        "vx": math.cos(a2)*6, "vy": math.sin(a2)*6, "damage": 7})

        # Boss takes hits
        for b in game["bullets"][:]:
            if b not in game["bullets"]: continue
            if math.hypot(b["x"] - boss["x"], b["y"] - boss["y"]) < 58:
                boss["health"] -= b["damage"]
                create_explosion(b["x"], b["y"], YELLOW, count=6, speed_max=3)
                spawn_floater(b["x"], b["y"], f"{int(b['damage'])}", ORANGE)
                play("boss_hit")
                if b["weapon"] != "laser" and b in game["bullets"]:
                    game["bullets"].remove(b)
                if boss["health"] <= 0:
                    create_explosion(boss["x"], boss["y"], ORANGE, count=80, speed_max=12)
                    create_explosion(boss["x"], boss["y"], WHITE,  count=30, speed_max=8)
                    game["screen_shake"] = 25
                    play("explode")
                    game["boss"] = None
                    boss = None
                    game["boss_wave"] = False
                    game["score"]    += 50
                    game["kills"]    += 1
                    high_score = max(high_score, game["score"])
                    add_xp(200)
                    game["upgrade_points"] += 3
                    spawn_floater(WIDTH//2, HEIGHT//2 - 60, "BOSS DOWN! +3 PTS", GOLD)
                    game["in_shop"]      = True
                    game["shop_paused"]  = True
                    break

        if boss and math.hypot(px - boss["x"], py - boss["y"]) < 68 and game["invincible_timer"] <= 0:
            dmg = apply_damage(18)
            spawn_floater(px, py - 20, f"-{dmg}", RED)
            game["invincible_timer"] = 45
            game["screen_shake"]     = 14

    # ── PARTICLES ─────────────────────────────────────────────────────────────
    for p in game["particles"][:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vx"] *= 0.91
        p["vy"] *= 0.91
        p["life"] -= 1
        if p["life"] <= 0:
            game["particles"].remove(p)

    # ── FLOATERS ──────────────────────────────────────────────────────────────
    for f in game["floaters"][:]:
        f["y"] += f["vy"]
        f["life"] -= 1
        if f["life"] <= 0:
            game["floaters"].remove(f)

    # ── POWERUPS ──────────────────────────────────────────────────────────────
    POWERUP_COLORS = {
        "health": GREEN, "shotgun": ORANGE, "laser": CYAN,
        "rapid": PINK, "plasma": PURPLE, "shield": BLUE,
    }
    POWERUP_LABELS = {
        "health": "HP", "shotgun": "SG", "laser": "LZ",
        "rapid": "RF", "plasma": "PL", "shield": "SH",
    }
    for p in game["powerups"][:]:
        p["bob"] = p.get("bob", 0) + 0.07
        if math.hypot(px - p["x"], py - p["y"]) < 28:
            t = p["type"]
            if t == "health":
                heal = min(game["max_health"], game["health"] + 35) - game["health"]
                game["health"] += heal
                spawn_floater(px, py - 25, f"+{heal} HP", GREEN)
            elif t == "shield":
                game["invincible_timer"] = 180
                spawn_floater(px, py - 25, "SHIELD!", BLUE)
            elif t in WEAPONS:
                game["weapon"]       = t
                game["weapon_timer"] = 600
                spawn_floater(px, py - 25, f"{WEAPONS[t]['name']}!", WEAPONS[t]["color"])
            play("powerup")
            game["powerups"].remove(p)

    # Death
    if game["health"] <= 0:
        game["health"]  = 0
        game["game_over"] = True
        high_wave = max(high_wave, game["wave"])

    # ── DRAW ──────────────────────────────────────────────────────────────────
    shake_x = random.randint(-game["screen_shake"], game["screen_shake"]) if game["screen_shake"] > 0 else 0
    shake_y = random.randint(-game["screen_shake"], game["screen_shake"]) if game["screen_shake"] > 0 else 0

    draw_surf = pygame.Surface((WIDTH, HEIGHT))
    draw_background(draw_surf, game["time"], game["grid_offset"])

    # Particles
    for p in game["particles"]:
        frac = p["life"] / p["max_life"]
        r, g, b2 = p["color"]
        c = (int(r*frac), int(g*frac), int(b2*frac))
        pygame.draw.circle(draw_surf, c, (int(p["x"]), int(p["y"])), max(1, p["size"]))

    # Powerups
    t_now = game["time"]
    for p in game["powerups"]:
        col   = POWERUP_COLORS.get(p["type"], WHITE)
        pulse = int(abs(math.sin(t_now * 0.07)) * 5)
        bob   = math.sin(p["bob"]) * 5
        cx, cy = int(p["x"]), int(p["y"] + bob)
        pygame.draw.circle(draw_surf, col, (cx, cy), 16 + pulse, 3)
        lbl = font_xs.render(POWERUP_LABELS.get(p["type"], "?"), True, col)
        draw_surf.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

    # Enemy bullets
    for b in game["enemy_bullets"]:
        pygame.draw.circle(draw_surf, RED,    (int(b["x"]), int(b["y"])), 6)
        pygame.draw.circle(draw_surf, ORANGE, (int(b["x"]), int(b["y"])), 3)

    # Enemies
    for e in game["enemies"]:
        ex, ey = int(e["x"]), int(e["y"])
        r2 = e["radius"]
        pygame.draw.circle(draw_surf, e["color"], (ex, ey), r2)
        inner = tuple(min(255, c + 55) for c in e["color"])
        pygame.draw.circle(draw_surf, inner, (ex, ey), r2 // 2)
        # Eye
        if e["type"] in ("shooter", "specter"):
            ang_to_player = math.atan2(py - ey, px - ex)
            ex2 = ex + int(math.cos(ang_to_player) * (r2 * 0.4))
            ey2 = ey + int(math.sin(ang_to_player) * (r2 * 0.4))
            pygame.draw.circle(draw_surf, WHITE, (ex2, ey2), 4)
            pygame.draw.circle(draw_surf, BLACK, (ex2, ey2), 2)
        if e["health"] < e["max_health"]:
            draw_bar(draw_surf, ex - 22, ey - r2 - 12, 44, 6, e["health"], e["max_health"], GREEN)

    # Boss
    if boss:
        bx, by = int(boss["x"]), int(boss["y"])
        pulse = int(abs(math.sin(t_now * 0.06)) * 10)
        phase_colors = {1: ORANGE, 2: RED, 3: (220, 20, 20)}
        bc = phase_colors[boss["phase"]]
        pygame.draw.circle(draw_surf, bc,     (bx, by), 58 + pulse)
        pygame.draw.circle(draw_surf, YELLOW, (bx, by), 42)
        pygame.draw.circle(draw_surf, bc,     (bx, by), 26)
        pygame.draw.circle(draw_surf, WHITE,  (bx, by), 10)
        # Orbit ring
        rings = 8 + (boss["phase"] - 1) * 4
        for i in range(rings):
            a = boss["angle"] * 3 + i * math.pi * 2 / rings
            rr = 75 + pulse // 2
            pygame.draw.circle(draw_surf, YELLOW, (int(bx + math.cos(a)*rr), int(by + math.sin(a)*rr)), 5)
        # Boss HP bar
        draw_bar(draw_surf, WIDTH//2 - 220, 18, 440, 26, boss["health"], boss["max_health"], bc, DKRED)
        phase_lbl = font_sm.render(f"BOSS  PHASE {boss['phase']}", True, YELLOW)
        draw_surf.blit(phase_lbl, (WIDTH//2 - phase_lbl.get_width()//2, 48))

    # Player bullets (with trails)
    for b in game["bullets"]:
        col = b["color"]
        for j, (tx, ty) in enumerate(b["trail"]):
            alpha_frac = (j + 1) / (len(b["trail"]) + 1)
            tc = tuple(int(c * alpha_frac * 0.5) for c in col)
            pygame.draw.circle(draw_surf, tc, (tx, ty), max(1, int(4 * alpha_frac)))
        size = 6 if b["weapon"] == "plasma" else (4 if b["weapon"] in ("laser","shotgun") else 5)
        pygame.draw.circle(draw_surf, WHITE, (int(b["x"]), int(b["y"])), size - 1)
        pygame.draw.circle(draw_surf, col,   (int(b["x"]), int(b["y"])), size - 2)

    # Player
    flash = game["invincible_timer"] > 0 and (t_now // 5) % 2 == 0
    if not flash:
        shield_on = game["invincible_timer"] > 60
        if shield_on:
            sp = int(abs(math.sin(t_now * 0.1)) * 4)
            pygame.draw.circle(draw_surf, BLUE, (int(px), int(py)), 30 + sp, 2)
        pygame.draw.circle(draw_surf, BLUE, (int(px), int(py)), 20)
        pygame.draw.circle(draw_surf, CYAN, (int(px), int(py)), 11)
        # Gun
        mx2, my2 = pygame.mouse.get_pos()
        angle = math.atan2(my2 - py, mx2 - px)
        gx = px + math.cos(angle) * 30
        gy = py + math.sin(angle) * 30
        wc = WEAPONS[game["weapon"]]["color"]
        pygame.draw.line(draw_surf, wc,   (int(px), int(py)), (int(gx), int(gy)), 6)
        pygame.draw.line(draw_surf, WHITE, (int(px), int(py)), (int(gx), int(gy)), 2)
        # Dash ghost trail
        if game["dash_cooldown"] > 40:
            for i in range(4):
                tx2 = px - math.cos(angle) * (i+1) * 10
                ty2 = py - math.sin(angle) * (i+1) * 10
                a   = max(0, 100 - i * 28)
                pygame.draw.circle(draw_surf, (30, 80, a), (int(tx2), int(ty2)), max(2, 11-i*3))

    # Floaters
    for f in game["floaters"]:
        alpha_f = f["life"] / f["max_life"]
        col_f = tuple(int(c * alpha_f) for c in f["color"])
        txt = font_sm.render(f["text"], True, col_f)
        draw_surf.blit(txt, (int(f["x"]) - txt.get_width()//2, int(f["y"])))

    # HUD
    draw_hud(draw_surf)

    screen.blit(draw_surf, (shake_x, shake_y))
    pygame.display.flip()

pygame.quit()
