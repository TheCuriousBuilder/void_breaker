"""
VOID BREAKER  —  Maxed Out Edition
Single file. Requires: pygame, numpy

Controls:
  WASD / Arrows   Move
  Mouse           Aim
  LMB (hold)      Shoot
  SPACE           Dash (toward mouse if standing still)
  TAB / E         Open/close upgrade shop
  Q               Cycle weapon (if carrying multiple)
  ESC / P         Pause
  R               Restart (game over screen)
"""

import pygame, random, math, sys
pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    MIXER_OK = True
except Exception:
    MIXER_OK = False

# ══════════════════════════════════════════════════════════════════════════════
# WINDOW
# ══════════════════════════════════════════════════════════════════════════════
WIDTH, HEIGHT = 1280, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("VOID BREAKER")
clock  = pygame.time.Clock()

# ══════════════════════════════════════════════════════════════════════════════
# FONTS
# ══════════════════════════════════════════════════════════════════════════════
F_XS  = pygame.font.SysFont("consolas", 17)
F_SM  = pygame.font.SysFont("consolas", 23)
F_MD  = pygame.font.SysFont("consolas", 31)
F_LG  = pygame.font.SysFont("consolas", 52)
F_XL  = pygame.font.SysFont("consolas", 80)
F_XXL = pygame.font.SysFont("consolas", 112)

# ══════════════════════════════════════════════════════════════════════════════
# COLORS
# ══════════════════════════════════════════════════════════════════════════════
BLACK  = (8,   8,  18)
DARK   = (18,  18, 35)
DARKER = (12,  12, 25)
WHITE  = (220,225,255)
DIM    = (100,110,150)
RED    = (220, 55, 55)
DKRED  = (100, 15, 15)
GREEN  = (55, 210,100)
DKGRN  = (15,  80, 35)
BLUE   = (55, 140,255)
DKBLUE = (15,  35,100)
CYAN   = (55, 220,220)
YELLOW = (255,230, 55)
ORANGE = (255,140, 35)
PURPLE = (175, 75,255)
PINK   = (255, 75,175)
TEAL   = (35, 200,160)
GOLD   = (255,200, 50)
LIME   = (120,255, 60)

def clamp(v,lo,hi): return max(lo,min(hi,v))

# ══════════════════════════════════════════════════════════════════════════════
# SOUND
# ══════════════════════════════════════════════════════════════════════════════
SFX = {}
SOUND_ON = False

def _make(freq, ms, wave="sine", vol=0.25, decay=True):
    try:
        import numpy as np
        sr = 22050; n = int(sr*ms/1000)
        t  = np.linspace(0, ms/1000, n, False)
        if   wave=="sine":   s = np.sin(2*math.pi*freq*t)
        elif wave=="square": s = np.sign(np.sin(2*math.pi*freq*t))
        elif wave=="noise":  s = np.random.uniform(-1,1,n)
        elif wave=="sweep":  s = np.sin(2*math.pi*freq*(1+2*(1-t/(ms/1000)))*t)
        else:                s = np.sin(2*math.pi*freq*t)
        if decay: s *= np.linspace(1,0,n)
        s = (s*vol*32767).astype(np.int16)
        stereo = np.column_stack([s,s])
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None

if MIXER_OK:
    try:
        import numpy as _np
        SFX = {
            "shoot":    _make(800,  60,  "sine",   0.13),
            "shoot_sg": _make(200,  90,  "noise",  0.22),
            "shoot_lz": _make(1400, 38,  "sweep",  0.18),
            "shoot_rp": _make(650,  32,  "square", 0.09),
            "shoot_pl": _make(300,  80,  "sine",   0.20),
            "shoot_sn": _make(1800, 28,  "sweep",  0.16),
            "shoot_rk": _make(180,  120, "noise",  0.25),
            "explode":  _make(110,  220, "noise",  0.32),
            "hit":      _make(300,  75,  "noise",  0.18),
            "powerup":  _make(900,  280, "sine",   0.28),
            "boss_hit": _make(80,   160, "noise",  0.28),
            "dash":     _make(420,  110, "sweep",  0.18),
            "levelup":  _make(680,  380, "sine",   0.28),
            "shield":   _make(500,  200, "sine",   0.20),
            "warp":     _make(220,  350, "sweep",  0.22),
        }
        SOUND_ON = True
    except Exception:
        pass

def play(name):
    if SOUND_ON and name in SFX and SFX[name]:
        SFX[name].play()

# ══════════════════════════════════════════════════════════════════════════════
# WEAPONS  (7 types)
# ══════════════════════════════════════════════════════════════════════════════
WEAPONS = {
    "pistol":  {"name":"PISTOL",  "fire_rate":10, "speed":14, "damage":1,   "spread":0,    "count":1, "color":YELLOW, "sfx":"shoot",    "pierce":False},
    "shotgun": {"name":"SHOTGUN", "fire_rate":28, "speed":10, "damage":1,   "spread":0.38, "count":7, "color":ORANGE, "sfx":"shoot_sg", "pierce":False},
    "laser":   {"name":"LASER",   "fire_rate":4,  "speed":24, "damage":2,   "spread":0,    "count":1, "color":CYAN,   "sfx":"shoot_lz", "pierce":True},
    "rapid":   {"name":"RAPID",   "fire_rate":3,  "speed":16, "damage":1,   "spread":0.07, "count":1, "color":PINK,   "sfx":"shoot_rp", "pierce":False},
    "plasma":  {"name":"PLASMA",  "fire_rate":18, "speed":9,  "damage":5,   "spread":0,    "count":1, "color":PURPLE, "sfx":"shoot_pl", "pierce":False},
    "sniper":  {"name":"SNIPER",  "fire_rate":45, "speed":32, "damage":12,  "spread":0,    "count":1, "color":TEAL,   "sfx":"shoot_sn", "pierce":True},
    "rocket":  {"name":"ROCKET",  "fire_rate":50, "speed":7,  "damage":20,  "spread":0.05, "count":1, "color":RED,    "sfx":"shoot_rk", "pierce":False, "aoe":80},
}
WEAPON_ORDER = ["pistol","shotgun","laser","rapid","plasma","sniper","rocket"]

# ══════════════════════════════════════════════════════════════════════════════
# ENEMY TYPES  (7 types)
# ══════════════════════════════════════════════════════════════════════════════
ENEMY_TYPES = {
    "grunt":    {"color":RED,    "radius":18,"base_speed":1.8,"base_health":1, "damage":8,  "score":1, "shoots":False,"xp":10, "boss_drop":False},
    "scout":    {"color":ORANGE, "radius":13,"base_speed":3.2,"base_health":1, "damage":6,  "score":2, "shoots":False,"xp":15, "boss_drop":False},
    "brute":    {"color":DKRED,  "radius":30,"base_speed":1.0,"base_health":5, "damage":20, "score":4, "shoots":False,"xp":30, "boss_drop":True},
    "shooter":  {"color":PURPLE, "radius":16,"base_speed":1.3,"base_health":2, "damage":6,  "score":3, "shoots":True, "xp":20, "boss_drop":False},
    "specter":  {"color":TEAL,   "radius":14,"base_speed":2.5,"base_health":1, "damage":10, "score":3, "shoots":True, "xp":20, "boss_drop":False},
    "armored":  {"color":(80,80,120),"radius":22,"base_speed":1.5,"base_health":8,"damage":15,"score":5,"shoots":False,"xp":40,"boss_drop":True},
    "bomber":   {"color":(200,120,0),"radius":17,"base_speed":1.2,"base_health":2,"damage":30,"score":4,"shoots":False,"xp":35,"boss_drop":True,"explodes_on_death":True},
}
MAX_ENEMY_SPEED = 5.5

def get_wave_pool(wave):
    if wave<=2:  return ["grunt"]
    if wave<=4:  return ["grunt","scout"]
    if wave<=6:  return ["grunt","scout","brute"]
    if wave<=8:  return ["grunt","scout","brute","shooter"]
    if wave<=11: return ["grunt","scout","brute","shooter","specter"]
    if wave<=14: return ["grunt","scout","brute","shooter","specter","armored"]
    return list(ENEMY_TYPES.keys())

# ══════════════════════════════════════════════════════════════════════════════
# BOSS DEFINITIONS  (5 unique bosses)
# ══════════════════════════════════════════════════════════════════════════════
BOSS_DEFS = {
    1: {"name":"THE WATCHER",   "color":ORANGE, "hp_base":800,  "phases":3, "orbit_r":280, "ring_bullets":12, "special":"ring"},
    2: {"name":"VOID TITAN",    "color":PURPLE, "hp_base":1400, "phases":3, "orbit_r":250, "ring_bullets":16, "special":"split"},
    3: {"name":"NOVA HERALD",   "color":CYAN,   "hp_base":2200, "phases":3, "orbit_r":300, "ring_bullets":20, "special":"laser_sweep"},
    4: {"name":"DEATH MATRIX",  "color":RED,    "hp_base":3200, "phases":3, "orbit_r":260, "ring_bullets":24, "special":"clone"},
    5: {"name":"THE VOID CORE", "color":WHITE,  "hp_base":5000, "phases":4, "orbit_r":320, "ring_bullets":32, "special":"all"},
}

# ══════════════════════════════════════════════════════════════════════════════
# UPGRADES  (8 upgrade types)
# ══════════════════════════════════════════════════════════════════════════════
UPGRADES = [
    {"key":pygame.K_1,"label":"SPEED",     "attr":"speed_level",    "color":GREEN,  "desc":"Move +1.2 faster",    "max":10},
    {"key":pygame.K_2,"label":"DAMAGE",    "attr":"damage_level",   "color":RED,    "desc":"Deal x1.4 damage",    "max":10},
    {"key":pygame.K_3,"label":"MAX HP",    "attr":"health_level",   "color":PINK,   "desc":"+35 max health",      "max":10},
    {"key":pygame.K_4,"label":"FIRE RATE", "attr":"firerate_level", "color":ORANGE, "desc":"Shoot faster",        "max":10},
    {"key":pygame.K_5,"label":"ARMOR",     "attr":"armor_level",    "color":CYAN,   "desc":"-8% damage taken",    "max":8},
    {"key":pygame.K_6,"label":"REGEN",     "attr":"regen_level",    "color":TEAL,   "desc":"+1.5 HP/sec",         "max":6},
    {"key":pygame.K_7,"label":"PIERCE",    "attr":"pierce_level",   "color":LIME,   "desc":"Bullets pierce +1",   "max":5},
    {"key":pygame.K_8,"label":"MAGNET",    "attr":"magnet_level",   "color":GOLD,   "desc":"Powerup pickup range","max":5},
]
def upgrade_cost(level): return max(1, level)

# ══════════════════════════════════════════════════════════════════════════════
# ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════════════════════
ACHIEVEMENTS = [
    {"id":"first_blood",  "name":"First Blood",   "desc":"Kill 1 enemy",          "condition": lambda g: g["kills"]>=1},
    {"id":"century",      "name":"Century",        "desc":"Kill 100 enemies",       "condition": lambda g: g["kills"]>=100},
    {"id":"boss_slayer",  "name":"Boss Slayer",    "desc":"Kill your first boss",   "condition": lambda g: g["bosses_killed"]>=1},
    {"id":"survivor",     "name":"Survivor",       "desc":"Reach wave 10",          "condition": lambda g: g["wave"]>=10},
    {"id":"veteran",      "name":"Veteran",        "desc":"Reach wave 20",          "condition": lambda g: g["wave"]>=20},
    {"id":"legendary",    "name":"Legendary",      "desc":"Score 1000",             "condition": lambda g: g["score"]>=1000},
    {"id":"max_level",    "name":"Ascended",       "desc":"Reach player level 10",  "condition": lambda g: g["player_level"]>=10},
    {"id":"weapon_master","name":"Arsenal",        "desc":"Pick up 5 weapons",      "condition": lambda g: g["weapons_picked"]>=5},
]

# ══════════════════════════════════════════════════════════════════════════════
# GAME STATE
# ══════════════════════════════════════════════════════════════════════════════
high_score = 0
high_wave  = 1
unlocked_achievements = set()

def reset_game():
    stars = [(random.randint(0,WIDTH), random.randint(0,HEIGHT),
              random.uniform(0.3,2.0), random.uniform(0.2,0.8)) for _ in range(180)]
    return {
        # Player
        "player_x": WIDTH//2, "player_y": HEIGHT//2,
        "health": 100, "max_health": 100,
        # Progress
        "score": 0, "xp": 0, "player_level": 1, "xp_to_next": 100,
        "wave": 1, "kills": 0, "bosses_killed": 0, "weapons_picked": 0,
        # Combat lists
        "bullets": [], "enemy_bullets": [], "enemies": [],
        "particles": [], "powerups": [], "floaters": [],
        # Boss
        "boss": None, "boss_def": None,
        # Timers
        "spawn_timer": 0, "shoot_timer": 0,
        "dash_cooldown": 0, "dash_active": 0,
        "invincible_timer": 0, "screen_shake": 0,
        "regen_timer": 0, "combo_timer": 0,
        # Weapon
        "weapon": "pistol", "weapon_timer": 0,
        "weapon_inventory": ["pistol"],   # collected weapons
        # Upgrades
        "speed_level":1,"damage_level":1,"health_level":1,"firerate_level":1,
        "armor_level":0,"regen_level":0,"pierce_level":0,"magnet_level":0,
        "upgrade_points": 2,
        # State flags
        "game_over": False, "paused": False,
        "in_shop": False, "shop_paused": False,
        "between_waves": False, "between_wave_timer": 0,
        "boss_wave": False,
        "wave_score_threshold": 25,
        # Visual
        "combo": 0,
        "background_stars": stars,
        "grid_offset": 0.0,
        "time": 0,
        # Stats for achievements
        "total_damage_dealt": 0,
    }

game = reset_game()

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def player_speed():      return 5 + game["speed_level"] * 1.2
def damage_mult():       return 1.0 + (game["damage_level"]-1)*0.4
def armor_red():         return 1.0 - game["armor_level"]*0.08
def pickup_range():      return 28 + game["magnet_level"]*18
def pierce_count():      return game["pierce_level"]

def apply_dmg(amount):
    reduced = max(1, int(amount * armor_red()))
    game["health"] = max(0, game["health"] - reduced)
    return reduced

def spawn_floater(x, y, text, color=WHITE):
    game["floaters"].append({
        "x": x+random.randint(-14,14), "y": y,
        "text": text, "color": color,
        "life": 58, "max_life": 58, "vy": -1.6,
    })

def add_xp(amount):
    game["xp"] += amount
    while game["xp"] >= game["xp_to_next"]:
        game["xp"] -= game["xp_to_next"]
        game["player_level"] += 1
        game["xp_to_next"]   = int(game["xp_to_next"]*1.4)
        game["upgrade_points"] += 2
        spawn_floater(game["player_x"], game["player_y"]-35, "LEVEL UP! +2pts", GOLD)
        play("levelup")

def fire_weapon(px, py, angle):
    w   = WEAPONS[game["weapon"]]
    dmg = w["damage"] * damage_mult()
    pc  = pierce_count() + (1 if w.get("pierce") else 0)
    for _ in range(w["count"]):
        a  = angle + random.uniform(-w["spread"], w["spread"])
        game["bullets"].append({
            "x":px,"y":py,
            "vx":math.cos(a)*w["speed"],
            "vy":math.sin(a)*w["speed"],
            "damage":dmg,"color":w["color"],
            "weapon":game["weapon"],
            "trail":[],"pierce_left":pc,
            "aoe": w.get("aoe",0),
        })
    play(w["sfx"])

def create_explosion(x, y, color=YELLOW, count=22, speed_max=7):
    for _ in range(count):
        a  = random.uniform(0, math.pi*2)
        sp = random.uniform(1, speed_max)
        game["particles"].append({
            "x":x,"y":y,
            "vx":math.cos(a)*sp,"vy":math.sin(a)*sp,
            "life":random.randint(18,52),"max_life":52,
            "color":color,"size":random.randint(2,6),
        })
    for i in range(14):
        a = i*math.pi*2/14
        game["particles"].append({
            "x":x,"y":y,"vx":math.cos(a)*3,"vy":math.sin(a)*3,
            "life":22,"max_life":22,"color":WHITE,"size":3,
        })

def aoe_explosion(x, y, radius, dmg, ignore_boss=False):
    """Deal AOE damage to all enemies in radius."""
    for e in game["enemies"][:]:
        if math.hypot(e["x"]-x, e["y"]-y) < radius:
            e["health"] -= dmg
            spawn_floater(e["x"], e["y"]-e["radius"]-8, f"{int(dmg)}", RED)
            if e["health"] <= 0:
                kill_enemy(e)
    if not ignore_boss and game["boss"]:
        b = game["boss"]
        if math.hypot(b["x"]-x, b["y"]-y) < radius:
            b["health"] -= dmg//2

def kill_enemy(e):
    global high_score
    if e not in game["enemies"]: return
    create_explosion(e["x"], e["y"], e["color"])
    play("explode")
    game["enemies"].remove(e)
    pts = e["score"]
    game["combo"] += 1
    game["combo_timer"] = 100
    combo_bonus = max(1, game["combo"]//3)
    pts *= combo_bonus
    game["score"] += pts
    game["kills"] += 1
    high_score = max(high_score, game["score"])
    add_xp(e["xp"])
    spawn_floater(e["x"], e["y"], f"+{pts}", GOLD)
    # Bomber death explosion
    if e.get("explodes_on_death"):
        aoe_explosion(e["x"], e["y"], 100, 25)
        create_explosion(e["x"], e["y"], ORANGE, count=40, speed_max=9)
    # General powerup drop (14%) — nuke excluded here
    if random.random() < 0.14:
        pt = random.choice(["health","shotgun","laser","rapid","plasma","sniper","rocket","shield","freeze"])
        game["powerups"].append({"x":e["x"],"y":e["y"],"type":pt,"bob":0,"life":600})
    # Nuke drops separately at 10%
    if random.random() < 0.10:
        game["powerups"].append({"x":e["x"],"y":e["y"],"type":"nuke","bob":0,"life":600})
    if random.random() < 0.07:
        game["upgrade_points"] += 1
        spawn_floater(e["x"], e["y"]-28, "+1 UPGRADE PT", CYAN)

def spawn_enemy():
    side = random.randint(0,3)
    margin = 65
    if   side==0: x,y = random.randint(0,WIDTH), -margin
    elif side==1: x,y = WIDTH+margin, random.randint(0,HEIGHT)
    elif side==2: x,y = random.randint(0,WIDTH), HEIGHT+margin
    else:         x,y = -margin, random.randint(0,HEIGHT)
    etype = random.choice(get_wave_pool(game["wave"]))
    t  = ENEMY_TYPES[etype]
    sp = min(t["base_speed"] + game["wave"]*0.11, MAX_ENEMY_SPEED)
    hp = t["base_health"] + game["wave"]//3
    game["enemies"].append({
        "x":x,"y":y,"type":etype,
        "speed":sp,"health":hp,"max_health":hp,
        "shoot_timer":random.randint(0,80),
        "radius":t["radius"],"color":t["color"],
        "damage":t["damage"],"score":t["score"],
        "shoots":t["shoots"],"xp":t["xp"],
        "wobble":random.uniform(0,math.pi*2),
        "explodes_on_death": t.get("explodes_on_death",False),
    })

def spawn_boss(wave):
    bd  = BOSS_DEFS.get(min(wave//5, len(BOSS_DEFS)), BOSS_DEFS[5])
    hp  = bd["hp_base"] + wave*20
    game["boss"] = {
        "x":WIDTH//2,"y":-120,
        "health":hp,"max_health":hp,
        "shoot_timer":0,"phase":1,
        "angle":0,"orbit_r":bd["orbit_r"],
        "wave":wave,"name":bd["name"],"color":bd["color"],
        "phases":bd["phases"],"ring_bullets":bd["ring_bullets"],
        "special":bd["special"],
        "laser_angle":0, "clones":[],
        "enrage":False,
    }
    game["boss_def"] = bd

def check_achievements():
    for ach in ACHIEVEMENTS:
        aid = ach["id"]
        if aid not in unlocked_achievements and ach["condition"](game):
            unlocked_achievements.add(aid)
            spawn_floater(WIDTH//2, HEIGHT//2-80,
                          f"ACHIEVEMENT: {ach['name']}", GOLD)
            play("levelup")

# ══════════════════════════════════════════════════════════════════════════════
# DRAW HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def draw_bar(surf, x,y,w,h, val,maxv, fill, bg=DARK, border=DIM, radius=4):
    pygame.draw.rect(surf, bg, (x,y,w,h), border_radius=radius)
    fw = int(w * clamp(val/max(maxv,1), 0, 1))
    if fw>0: pygame.draw.rect(surf, fill, (x,y,fw,h), border_radius=radius)
    pygame.draw.rect(surf, border, (x,y,w,h), 1, border_radius=radius)

def draw_panel(surf, x,y,w,h, alpha=205, color=DARK):
    s = pygame.Surface((w,h), pygame.SRCALPHA)
    s.fill((*color, alpha))
    surf.blit(s,(x,y))
    pygame.draw.rect(surf, DIM, (x,y,w,h), 1, border_radius=8)

def draw_background(surf, t, offset):
    surf.fill(BLACK)
    gc  = (20,22,45)
    sp  = 70
    off = int(offset) % sp
    for x in range(-sp+off, WIDTH+sp, sp):
        pygame.draw.line(surf, gc, (x,0),(x,HEIGHT))
    for y in range(-sp+off, HEIGHT+sp, sp):
        pygame.draw.line(surf, gc, (0,y),(WIDTH,y))
    for sx,sy,br,twk in game["background_stars"]:
        bri = int(abs(math.sin(t*twk*0.02))*br*90+20)
        bri = clamp(bri,10,110)
        pygame.draw.circle(surf,(bri,bri,bri+25),(int(sx),int(sy)),1)

def draw_hud(surf):
    # Health
    draw_bar(surf,20,20,270,22,game["health"],game["max_health"],GREEN,DKRED)
    surf.blit(F_XS.render(f"HP {game['health']}/{game['max_health']}",True,WHITE),(296,22))
    # XP
    draw_bar(surf,20,48,270,8,game["xp"],game["xp_to_next"],GOLD,DARKER)
    surf.blit(F_XS.render(f"LV {game['player_level']}  XP {game['xp']}/{game['xp_to_next']}",True,GOLD),(20,60))
    # Score/wave
    surf.blit(F_MD.render(f"SCORE {game['score']:>7}",True,WHITE),(20,82))
    surf.blit(F_SM.render(f"WAVE  {game['wave']:>4}",True,CYAN),(20,120))
    surf.blit(F_XS.render(f"BEST  {high_score}",True,DIM),(20,150))
    surf.blit(F_XS.render(f"KILLS {game['kills']}",True,DIM),(20,170))
    # Weapon + inventory
    w = WEAPONS[game["weapon"]]
    wt = F_MD.render(f"[ {w['name']} ]",True,w["color"])
    surf.blit(wt,(WIDTH-wt.get_width()-20,20))
    if game["weapon_timer"]>0:
        secs = math.ceil(game["weapon_timer"]/60)
        draw_bar(surf,WIDTH-wt.get_width()-20,56,wt.get_width(),6,game["weapon_timer"],600,w["color"])
        surf.blit(F_XS.render(f"{secs}s",True,w["color"]),(WIDTH-44,64))
    # Weapon inventory icons
    inv_x = WIDTH-20
    for wn in reversed(game["weapon_inventory"]):
        wdata = WEAPONS[wn]
        col   = wdata["color"] if wn==game["weapon"] else tuple(c//2 for c in wdata["color"])
        lbl   = F_XS.render(wdata["name"][:3],True,col)
        inv_x -= lbl.get_width()+8
        surf.blit(lbl,(inv_x,76))
    surf.blit(F_XS.render("[Q] cycle",True,DIM),(WIDTH-90,96))
    # Dash
    if game["dash_cooldown"]<=0:
        surf.blit(F_XS.render("DASH ready [SPACE]",True,BLUE),(20,HEIGHT-40))
    else:
        draw_bar(surf,20,HEIGHT-40,160,10,60-game["dash_cooldown"],60,BLUE,DKBLUE)
        surf.blit(F_XS.render("DASH",True,DIM),(188,HEIGHT-42))
    # Shop hint
    if game["upgrade_points"]>0:
        pulse = int(abs(math.sin(game["time"]*0.05))*28)
        col   = (clamp(200+pulse,0,255),clamp(175+pulse,0,255),55)
        ht    = F_SM.render(f"TAB  shop  [{game['upgrade_points']} pts]",True,col)
        surf.blit(ht,(WIDTH//2-ht.get_width()//2,HEIGHT-42))
    # Combo
    if game["combo"]>=3:
        ct = F_MD.render(f"x{game['combo']} COMBO",True,GOLD)
        surf.blit(ct,(WIDTH//2-ct.get_width()//2,HEIGHT-78))
    # Regen
    if game["regen_level"]>0:
        surf.blit(F_XS.render(f"REGEN +{game['regen_level']*1.5:.1f}/s",True,TEAL),(20,192))
    # Pierce
    if game["pierce_level"]>0:
        surf.blit(F_XS.render(f"PIERCE +{game['pierce_level']}",True,LIME),(20,210))
    # Pause hint
    surf.blit(F_XS.render("[ESC/P] pause",True,DIM),(WIDTH-120,HEIGHT-20))

def draw_shop(surf):
    draw_panel(surf,0,0,WIDTH,HEIGHT,215,BLACK)
    title = F_XL.render("UPGRADE SHOP",True,YELLOW)
    surf.blit(title,(WIDTH//2-title.get_width()//2,24))
    pts = F_LG.render(f"{game['upgrade_points']}  upgrade points",True,CYAN)
    surf.blit(pts,(WIDTH//2-pts.get_width()//2,110))

    cols=4; card_w,card_h=280,205
    total_w=cols*card_w+(cols-1)*14
    sx=WIDTH//2-total_w//2; sy=168

    for i,upg in enumerate(UPGRADES):
        col = i%cols; row = i//cols
        x = sx+col*(card_w+14); y = sy+row*(card_h+12)
        level  = game[upg["attr"]]
        maxed  = level>=upg["max"]
        cost   = upgrade_cost(level)
        can    = game["upgrade_points"]>=cost and not maxed
        bg     = (28,32,58) if can else (17,17,29)
        border = upg["color"] if can else (48,48,72)
        draw_panel(surf,x,y,card_w,card_h,230,(bg[0],bg[1],bg[2]))
        pygame.draw.rect(surf,border,(x,y,card_w,card_h),2,border_radius=8)
        ks = F_LG.render(str(i+1),True,upg["color"] if can else DIM)
        surf.blit(ks,(x+12,y+8))
        surf.blit(F_MD.render(upg["label"],True,WHITE),(x+12,y+68))
        surf.blit(F_XS.render(upg["desc"],True,DIM),(x+12,y+104))
        # pips
        pip_y=y+136
        for p in range(upg["max"]):
            pc2 = upg["color"] if p<level else (33,33,52)
            pygame.draw.rect(surf,pc2,(x+12+p*20,pip_y,14,8),border_radius=3)
        if maxed:
            surf.blit(F_SM.render("MAXED",True,GOLD),(x+12,y+158))
        else:
            cc = YELLOW if can else (88,88,108)
            surf.blit(F_SM.render(f"cost: {cost} pt{'s' if cost!=1 else ''}",True,cc),(x+12,y+158))

    hint=F_SM.render("1-8 upgrade     TAB/ESC resume",True,DIM)
    surf.blit(hint,(WIDTH//2-hint.get_width()//2,HEIGHT-44))

def draw_pause(surf):
    draw_panel(surf,0,0,WIDTH,HEIGHT,170,BLACK)
    pt = F_XL.render("PAUSED",True,WHITE)
    surf.blit(pt,(WIDTH//2-pt.get_width()//2,HEIGHT//2-60))
    ht = F_MD.render("ESC / P to resume",True,DIM)
    surf.blit(ht,(WIDTH//2-ht.get_width()//2,HEIGHT//2+20))

def draw_game_over(surf):
    draw_panel(surf,0,0,WIDTH,HEIGHT,200,BLACK)
    go=F_XXL.render("GAME OVER",True,RED)
    surf.blit(go,(WIDTH//2-go.get_width()//2,HEIGHT//2-150))
    surf.blit(F_LG.render(f"SCORE  {game['score']}      WAVE  {game['wave']}",True,WHITE),
              (WIDTH//2-280,HEIGHT//2-20))
    surf.blit(F_MD.render(f"ALL-TIME BEST:  {high_score}  (wave {high_wave})",True,GOLD),
              (WIDTH//2-270,HEIGHT//2+42))
    surf.blit(F_MD.render(f"KILLS: {game['kills']}   LEVEL: {game['player_level']}",True,DIM),
              (WIDTH//2-180,HEIGHT//2+88))
    # Achievements
    if unlocked_achievements:
        ach_names = [a["name"] for a in ACHIEVEMENTS if a["id"] in unlocked_achievements]
        at=F_XS.render("Achievements: "+", ".join(ach_names[:6]),True,GOLD)
        surf.blit(at,(WIDTH//2-at.get_width()//2,HEIGHT//2+130))
    rt=F_MD.render("R  --  restart",True,(155,160,205))
    surf.blit(rt,(WIDTH//2-rt.get_width()//2,HEIGHT//2+160))

def draw_between_wave(surf):
    draw_panel(surf,WIDTH//2-270,HEIGHT//2-65,540,130,205,DARKER)
    next_w = game["wave"]+1
    is_boss= next_w%5==0
    label  = f"BOSS WAVE {next_w}  --  {BOSS_DEFS.get(min(next_w//5,len(BOSS_DEFS)),BOSS_DEFS[5])['name']}" if is_boss else f"WAVE {next_w}"
    color  = RED if is_boss else CYAN
    t=F_LG.render(label,True,color)
    surf.blit(t,(WIDTH//2-t.get_width()//2,HEIGHT//2-48))
    pct=1-game["between_wave_timer"]/180
    draw_bar(surf,WIDTH//2-200,HEIGHT//2+32,400,12,pct,1.0,color,DARKER)

# ══════════════════════════════════════════════════════════════════════════════
# POWERUP TABLE
# ══════════════════════════════════════════════════════════════════════════════
POWERUP_COLORS = {
    "health":GREEN,"shotgun":ORANGE,"laser":CYAN,"rapid":PINK,
    "plasma":PURPLE,"sniper":TEAL,"rocket":RED,
    "shield":BLUE,"nuke":(255,80,80),"freeze":(100,180,255),
}
POWERUP_LABELS = {
    "health":"HP","shotgun":"SG","laser":"LZ","rapid":"RF",
    "plasma":"PL","sniper":"SN","rocket":"RK",
    "shield":"SH","nuke":"NK","freeze":"FZ",
}

def apply_powerup(ptype, px, py):
    if ptype == "health":
        heal = min(game["max_health"],game["health"]+40)-game["health"]
        game["health"] += heal
        spawn_floater(px,py-28,f"+{heal} HP",GREEN)
    elif ptype == "shield":
        game["invincible_timer"] = 210
        spawn_floater(px,py-28,"SHIELD!",BLUE)
        play("shield")
    elif ptype == "nuke":
        # ── FIXED: directly remove enemies, clear their bullets,
        #    no kill_enemy() to avoid score/XP spam and bomber chains ──
        for e in game["enemies"][:]:
            if e in game["enemies"]:
                create_explosion(e["x"], e["y"], e["color"], count=12)
                game["enemies"].remove(e)
        game["enemy_bullets"].clear()
        if game["boss"]:
            game["boss"]["health"] -= 200
        spawn_floater(px,py-28,"NUKE!",RED)
        play("explode")
    elif ptype == "freeze":
        # Slow all enemies
        for e in game["enemies"]:
            e["speed"] = max(0.3, e["speed"]*0.3)
        spawn_floater(px,py-28,"FREEZE!",CYAN)
    elif ptype in WEAPONS:
        if ptype not in game["weapon_inventory"]:
            game["weapon_inventory"].append(ptype)
        game["weapon"] = ptype
        game["weapon_timer"] = 700
        game["weapons_picked"] += 1
        spawn_floater(px,py-28,f"{WEAPONS[ptype]['name']}!",WEAPONS[ptype]["color"])
    play("powerup")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════════════════════
running = True

while running:
    dt = clock.tick(60)
    game["time"] += 1
    t_now = game["time"]

    # ── EVENTS ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            k = event.key

            # Restart
            if game["game_over"] and k==pygame.K_r:
                game = reset_game(); continue

            # Pause  (ESC or P)
            if k in (pygame.K_ESCAPE, pygame.K_p) and not game["game_over"]:
                if game["in_shop"]:
                    game["in_shop"]=False; game["shop_paused"]=False
                else:
                    game["paused"] = not game["paused"]

            # Shop (handle FIRST)
            if game["in_shop"]:
                if k in (pygame.K_TAB, pygame.K_e):
                    game["in_shop"]=False; game["shop_paused"]=False
                else:
                    for upg in UPGRADES:
                        if k==upg["key"]:
                            lv   = game[upg["attr"]]
                            cost = upgrade_cost(lv)
                            if game["upgrade_points"]>=cost and lv<upg["max"]:
                                game["upgrade_points"] -= cost
                                game[upg["attr"]] += 1
                                if upg["attr"]=="health_level":
                                    game["max_health"] += 35
                                    game["health"] = min(game["health"]+35,game["max_health"])
                                play("levelup")
            else:
                # Open shop
                if k in (pygame.K_TAB, pygame.K_e) and not game["game_over"] and not game["between_waves"] and not game["paused"]:
                    game["in_shop"]=True; game["shop_paused"]=True

                # Dash
                if k==pygame.K_SPACE and not game["game_over"] and not game["between_waves"] and not game["paused"]:
                    if game["dash_cooldown"]<=0:
                        game["dash_active"]=8

                # Cycle weapon
                if k==pygame.K_q and not game["game_over"]:
                    inv = game["weapon_inventory"]
                    if len(inv)>1:
                        idx = inv.index(game["weapon"]) if game["weapon"] in inv else 0
                        game["weapon"] = inv[(idx+1)%len(inv)]

    # ── SHOP / PAUSE SCREENS ──────────────────────────────────────────────────
    if game["shop_paused"] or game["in_shop"]:
        ds = pygame.Surface((WIDTH,HEIGHT))
        draw_background(ds, t_now, game["grid_offset"])
        draw_hud(ds); draw_shop(ds)
        screen.blit(ds,(0,0)); pygame.display.flip(); continue

    if game["game_over"]:
        ds = pygame.Surface((WIDTH,HEIGHT))
        draw_background(ds, t_now, game["grid_offset"])
        draw_game_over(ds)
        screen.blit(ds,(0,0)); pygame.display.flip(); continue

    if game["paused"]:
        ds = pygame.Surface((WIDTH,HEIGHT))
        draw_background(ds, t_now, game["grid_offset"])
        draw_hud(ds); draw_pause(ds)
        screen.blit(ds,(0,0)); pygame.display.flip(); continue

    if game["between_waves"]:
        game["between_wave_timer"] -= 1
        ds = pygame.Surface((WIDTH,HEIGHT))
        draw_background(ds, t_now, game["grid_offset"])
        draw_hud(ds); draw_between_wave(ds)
        screen.blit(ds,(0,0)); pygame.display.flip()
        if game["between_wave_timer"]<=0:
            game["between_waves"]=False
            game["wave"]+=1
            if game["wave"]%5==0:
                game["boss_wave"]=True
                spawn_boss(game["wave"])
        continue

    # ── UPDATE ────────────────────────────────────────────────────────────────
    game["grid_offset"] += 0.5
    if game["screen_shake"]>0: game["screen_shake"]-=1

    for tmr in ["shoot_timer","invincible_timer","weapon_timer"]:
        if game[tmr]>0: game[tmr]-=1
    if game["dash_active"]==0 and game["dash_cooldown"]>0:
        game["dash_cooldown"]-=1

    # Weapon expiry
    if game["weapon_timer"]<=0 and game["weapon"]!="pistol":
        game["weapon"]="pistol"

    # Regen
    if game["regen_level"]>0:
        game["regen_timer"]+=1
        if game["regen_timer"]>=60:
            game["regen_timer"]=0
            regen_amt = game["regen_level"]*1.5
            game["health"]=min(game["max_health"],int(game["health"]+regen_amt))

    # Combo decay
    if game["combo_timer"]>0:
        game["combo_timer"]-=1
        if game["combo_timer"]<=0:
            game["combo"]=0

    px,py = game["player_x"],game["player_y"]

    # ── MOVEMENT ──────────────────────────────────────────────────────────────
    keys = pygame.key.get_pressed()
    spd  = player_speed()
    dx=dy=0
    if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= spd
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += spd
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= spd
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += spd
    if dx and dy: dx*=0.707; dy*=0.707

    # Dash
    if game["dash_active"]>0:
        game["dash_active"]-=1
        if game["dash_cooldown"]==0:
            game["dash_cooldown"]=60
            create_explosion(px,py,BLUE,count=10,speed_max=4)
            play("dash")
        if dx==0 and dy==0:
            mx2,my2=pygame.mouse.get_pos()
            da=math.atan2(my2-py,mx2-px)
            dx=math.cos(da)*spd; dy=math.sin(da)*spd
        dx*=5.0; dy*=5.0

    game["player_x"]=clamp(px+dx,22,WIDTH-22)
    game["player_y"]=clamp(py+dy,22,HEIGHT-22)
    px,py=game["player_x"],game["player_y"]

    # ── SHOOTING ──────────────────────────────────────────────────────────────
    fr = max(1, WEAPONS[game["weapon"]]["fire_rate"]-(game["firerate_level"]-1)*2)
    if pygame.mouse.get_pressed()[0] and game["shoot_timer"]<=0:
        mx,my=pygame.mouse.get_pos()
        fire_weapon(px,py,math.atan2(my-py,mx-px))
        game["shoot_timer"]=fr

    # ── ENEMY SPAWNING ────────────────────────────────────────────────────────
    if not game["boss_wave"]:
        game["spawn_timer"]+=1
        delay = max(10, 65-game["wave"]*2)
        if game["spawn_timer"]>=delay:
            game["spawn_timer"]=0
            count = 1+game["wave"]//8
            for _ in range(count): spawn_enemy()

    # Wave threshold
    nwt = game["wave_score_threshold"]+game["wave"]*20
    if not game["boss_wave"] and game["score"]>=nwt:
        game["wave_score_threshold"]=nwt
        game["between_waves"]=True
        game["between_wave_timer"]=180

    # ── PLAYER BULLETS ────────────────────────────────────────────────────────
    for b in game["bullets"][:]:
        b["trail"].append((int(b["x"]),int(b["y"])))
        if len(b["trail"])>6: b["trail"].pop(0)
        b["x"]+=b["vx"]; b["y"]+=b["vy"]
        if b["x"]<-40 or b["x"]>WIDTH+40 or b["y"]<-40 or b["y"]>HEIGHT+40:
            if b in game["bullets"]: game["bullets"].remove(b)

    # ── ENEMY BULLETS ─────────────────────────────────────────────────────────
    for b in game["enemy_bullets"][:]:
        b["x"]+=b["vx"]; b["y"]+=b["vy"]
        if b["x"]<0 or b["x"]>WIDTH or b["y"]<0 or b["y"]>HEIGHT:
            if b in game["enemy_bullets"]: game["enemy_bullets"].remove(b); continue
        if game["invincible_timer"]<=0 and math.hypot(px-b["x"],py-b["y"])<20:
            dmg=apply_dmg(b["damage"])
            spawn_floater(px,py-20,f"-{dmg}",RED)
            game["invincible_timer"]=22; game["screen_shake"]=7; play("hit")
            if b in game["enemy_bullets"]: game["enemy_bullets"].remove(b)

    # ── ENEMIES ───────────────────────────────────────────────────────────────
    for e in game["enemies"][:]:
        e["wobble"]+=0.05
        ddx=px-e["x"]; ddy=py-e["y"]
        dist=math.hypot(ddx,ddy)
        if dist>0:
            if e["type"]=="specter":
                perp_x=-ddy/dist; perp_y=ddx/dist
                straf=math.sin(e["wobble"]*2)*1.5
                e["x"]+=(ddx/dist*e["speed"]*0.6+perp_x*straf)
                e["y"]+=(ddy/dist*e["speed"]*0.6+perp_y*straf)
            elif e["type"]=="armored":
                # Zigzag
                zz=math.sin(e["wobble"]*3)*2
                e["x"]+=ddx/dist*e["speed"]+zz*(-ddy/dist)
                e["y"]+=ddy/dist*e["speed"]+zz*(ddx/dist)
            else:
                e["x"]+=ddx/dist*e["speed"]
                e["y"]+=ddy/dist*e["speed"]

        # Melee
        if dist<e["radius"]+20 and game["invincible_timer"]<=0:
            dmg=apply_dmg(e["damage"])
            spawn_floater(px,py-20,f"-{dmg}",RED)
            game["invincible_timer"]=35; game["screen_shake"]=9; play("hit")

        # Ranged
        if e["shoots"]:
            e["shoot_timer"]+=1
            rate=75 if e["type"]=="shooter" else 55
            if e["shoot_timer"]>=rate:
                e["shoot_timer"]=0
                ang=math.atan2(py-e["y"],px-e["x"])
                spreads=[-0.2,0,0.2] if e["type"]=="specter" else [0]
                for sp in spreads:
                    game["enemy_bullets"].append({
                        "x":e["x"],"y":e["y"],
                        "vx":math.cos(ang+sp)*5,"vy":math.sin(ang+sp)*5,
                        "damage":e["damage"],
                    })

        # Bullet collisions
        for b in game["bullets"][:]:
            if b not in game["bullets"]: continue
            if math.hypot(b["x"]-e["x"],b["y"]-e["y"])<e["radius"]+5:
                e["health"]-=b["damage"]
                game["total_damage_dealt"]+=b["damage"]
                spawn_floater(e["x"],e["y"]-e["radius"]-10,f"{int(b['damage'])}",b["color"])
                # AOE for rocket
                if b.get("aoe",0)>0:
                    aoe_explosion(b["x"],b["y"],b["aoe"],b["damage"]*0.6)
                    create_explosion(b["x"],b["y"],ORANGE,count=30,speed_max=8)
                if b.get("pierce_left",0)>0:
                    b["pierce_left"]-=1
                else:
                    if b in game["bullets"]: game["bullets"].remove(b)
                if e["health"]<=0:
                    kill_enemy(e)
                break

    # ── BOSS ──────────────────────────────────────────────────────────────────
    boss = game["boss"]
    if boss:
        boss["angle"]+=0.018
        # Enrage below 20%
        if boss["health"]<boss["max_health"]*0.2 and not boss["enrage"]:
            boss["enrage"]=True
            spawn_floater(boss["x"],boss["y"]-80,"ENRAGE!",RED)

        spd_mult = 1.8 if boss["enrage"] else 1.0
        tx = WIDTH//2+math.cos(boss["angle"])*boss["orbit_r"]
        ty = 150+math.sin(boss["angle"]*0.6)*100
        boss["x"]+=(tx-boss["x"])*0.025*spd_mult
        boss["y"]+=(ty-boss["y"])*0.025*spd_mult

        # Phase transitions
        ph_thresholds = [0.66, 0.33, 0.10][:boss["phases"]-1]
        for i,thresh in enumerate(ph_thresholds):
            if boss["health"]<boss["max_health"]*thresh and boss["phase"]<i+2:
                boss["phase"]=i+2
                create_explosion(boss["x"],boss["y"],boss["color"],count=40)

        boss["shoot_timer"]+=1
        base_rates={1:45,2:30,3:20,4:14}
        rate=max(8, base_rates.get(boss["phase"],20)-(20 if boss["enrage"] else 0))

        if boss["shoot_timer"]>=rate:
            boss["shoot_timer"]=0
            ang=math.atan2(py-boss["y"],px-boss["x"])
            spec=boss.get("special","ring")

            if boss["phase"]==1:
                game["enemy_bullets"].append({"x":boss["x"],"y":boss["y"],
                    "vx":math.cos(ang)*6,"vy":math.sin(ang)*6,"damage":12})

            elif boss["phase"]==2:
                spreads=[-0.35,-0.175,0,0.175,0.35]
                for sp in spreads:
                    game["enemy_bullets"].append({"x":boss["x"],"y":boss["y"],
                        "vx":math.cos(ang+sp)*7,"vy":math.sin(ang+sp)*7,"damage":9})

            elif boss["phase"]==3:
                rb=boss["ring_bullets"]
                for i in range(rb):
                    a2=i*math.pi*2/rb+boss["angle"]
                    game["enemy_bullets"].append({"x":boss["x"],"y":boss["y"],
                        "vx":math.cos(a2)*6,"vy":math.sin(a2)*6,"damage":7})
                # Also aimed
                game["enemy_bullets"].append({"x":boss["x"],"y":boss["y"],
                    "vx":math.cos(ang)*8,"vy":math.sin(ang)*8,"damage":14})

            elif boss["phase"]==4:
                # All patterns simultaneously
                for sp in [-0.3,0,0.3]:
                    game["enemy_bullets"].append({"x":boss["x"],"y":boss["y"],
                        "vx":math.cos(ang+sp)*8,"vy":math.sin(ang+sp)*8,"damage":10})
                rb=boss["ring_bullets"]
                for i in range(rb):
                    a2=i*math.pi*2/rb+boss["angle"]
                    game["enemy_bullets"].append({"x":boss["x"],"y":boss["y"],
                        "vx":math.cos(a2)*5,"vy":math.sin(a2)*5,"damage":6})
                # Spawn minions in phase 4
                if random.random()<0.15:
                    spawn_enemy()

        # Boss hit by bullets
        for b in game["bullets"][:]:
            if b not in game["bullets"]: continue
            if math.hypot(b["x"]-boss["x"],b["y"]-boss["y"])<62:
                boss["health"]-=b["damage"]
                game["total_damage_dealt"]+=b["damage"]
                create_explosion(b["x"],b["y"],YELLOW,count=6,speed_max=3)
                spawn_floater(b["x"],b["y"],f"{int(b['damage'])}",ORANGE)
                play("boss_hit")
                if b.get("aoe",0)>0:
                    boss["health"]-=b["damage"]*0.4
                if b.get("pierce_left",0)>0:
                    b["pierce_left"]-=1
                elif b in game["bullets"]:
                    game["bullets"].remove(b)
                if boss["health"]<=0:
                    create_explosion(boss["x"],boss["y"],boss["color"],count=90,speed_max=14)
                    create_explosion(boss["x"],boss["y"],WHITE,count=35,speed_max=9)
                    game["screen_shake"]=28; play("explode")
                    bname=boss["name"]
                    game["boss"]=None; boss=None
                    game["boss_wave"]=False
                    game["score"]+=80; game["kills"]+=1
                    game["bosses_killed"]+=1
                    high_score=max(high_score,game["score"])
                    add_xp(300)
                    game["upgrade_points"]+=4
                    spawn_floater(WIDTH//2,HEIGHT//2-65,f"{bname} DEFEATED! +4pts",GOLD)
                    game["in_shop"]=True; game["shop_paused"]=True
                    break

        if boss and math.hypot(px-boss["x"],py-boss["y"])<70 and game["invincible_timer"]<=0:
            dmg=apply_dmg(20)
            spawn_floater(px,py-22,f"-{dmg}",RED)
            game["invincible_timer"]=48; game["screen_shake"]=15

    # ── PARTICLES ─────────────────────────────────────────────────────────────
    for p in game["particles"][:]:
        p["x"]+=p["vx"]; p["y"]+=p["vy"]
        p["vx"]*=0.91;   p["vy"]*=0.91
        p["life"]-=1
        if p["life"]<=0: game["particles"].remove(p)

    # ── FLOATERS ──────────────────────────────────────────────────────────────
    for f in game["floaters"][:]:
        f["y"]+=f["vy"]; f["life"]-=1
        if f["life"]<=0: game["floaters"].remove(f)

    # ── POWERUPS ──────────────────────────────────────────────────────────────
    pr = pickup_range()
    for p in game["powerups"][:]:
        p["bob"]=p.get("bob",0)+0.07
        p["life"]=p.get("life",600)-1
        if p["life"]<=0:
            game["powerups"].remove(p); continue
        if math.hypot(px-p["x"],py-p["y"])<pr:
            apply_powerup(p["type"],px,py)
            game["powerups"].remove(p)

    # ── DEATH ─────────────────────────────────────────────────────────────────
    if game["health"]<=0:
        game["health"]=0; game["game_over"]=True
        high_wave=max(high_wave,game["wave"])

    # ── ACHIEVEMENTS ──────────────────────────────────────────────────────────
    check_achievements()

    # ══════════════════════════════════════════════════════════════════════════
    # DRAW
    # ══════════════════════════════════════════════════════════════════════════
    shake_x = random.randint(-game["screen_shake"],game["screen_shake"]) if game["screen_shake"]>0 else 0
    shake_y = random.randint(-game["screen_shake"],game["screen_shake"]) if game["screen_shake"]>0 else 0

    ds = pygame.Surface((WIDTH,HEIGHT))
    draw_background(ds, t_now, game["grid_offset"])

    # Particles
    for p in game["particles"]:
        frac=p["life"]/p["max_life"]
        r,g,b2=p["color"]
        c=(int(r*frac),int(g*frac),int(b2*frac))
        pygame.draw.circle(ds,c,(int(p["x"]),int(p["y"])),max(1,p["size"]))

    # Powerups
    for p in game["powerups"]:
        col   = POWERUP_COLORS.get(p["type"],WHITE)
        pulse = int(abs(math.sin(t_now*0.07))*5)
        bob   = math.sin(p["bob"])*5
        cx,cy = int(p["x"]),int(p["y"]+bob)
        # Lifetime ring
        life_frac = p.get("life",600)/600
        lc = tuple(int(c*life_frac) for c in col)
        pygame.draw.circle(ds,lc,(cx,cy),18+pulse,3)
        lbl=F_XS.render(POWERUP_LABELS.get(p["type"],"?"),True,col)
        ds.blit(lbl,(cx-lbl.get_width()//2,cy-lbl.get_height()//2))

    # Enemy bullets
    for b in game["enemy_bullets"]:
        pygame.draw.circle(ds,RED,(int(b["x"]),int(b["y"])),6)
        pygame.draw.circle(ds,ORANGE,(int(b["x"]),int(b["y"])),3)

    # Enemies
    for e in game["enemies"]:
        ex,ey=int(e["x"]),int(e["y"]); r2=e["radius"]
        # Armored: extra outer ring
        if e["type"]=="armored":
            pygame.draw.circle(ds,(60,60,100),(ex,ey),r2+4)
        pygame.draw.circle(ds,e["color"],(ex,ey),r2)
        inner=tuple(min(255,c+55) for c in e["color"])
        pygame.draw.circle(ds,inner,(ex,ey),r2//2)
        if e["type"] in ("shooter","specter"):
            atp=math.atan2(py-ey,px-ex)
            ex2=ex+int(math.cos(atp)*(r2*0.4)); ey2=ey+int(math.sin(atp)*(r2*0.4))
            pygame.draw.circle(ds,WHITE,(ex2,ey2),4)
            pygame.draw.circle(ds,BLACK,(ex2,ey2),2)
        if e["type"]=="bomber":
            # Flashing warning
            if t_now%20<10:
                pygame.draw.circle(ds,RED,(ex,ey),r2,2)
        if e["health"]<e["max_health"]:
            draw_bar(ds,ex-22,ey-r2-12,44,6,e["health"],e["max_health"],GREEN)

    # Boss
    if boss:
        bx,by=int(boss["x"]),int(boss["y"])
        pulse=int(abs(math.sin(t_now*0.06))*10)
        bc=boss["color"]
        enrage_flash = boss["enrage"] and (t_now%8<4)
        draw_col = RED if enrage_flash else bc
        pygame.draw.circle(ds,draw_col,(bx,by),62+pulse)
        pygame.draw.circle(ds,YELLOW,(bx,by),44)
        pygame.draw.circle(ds,draw_col,(bx,by),28)
        pygame.draw.circle(ds,WHITE,(bx,by),11)
        # Orbit rings
        rings=boss["ring_bullets"]
        for i in range(rings):
            a=boss["angle"]*3+i*math.pi*2/rings
            rr=80+pulse//2
            pygame.draw.circle(ds,YELLOW,(int(bx+math.cos(a)*rr),int(by+math.sin(a)*rr)),5)
        # Boss HP
        bar_col=RED if boss["enrage"] else bc
        draw_bar(ds,WIDTH//2-230,16,460,28,boss["health"],boss["max_health"],bar_col,DKRED)
        bl=F_SM.render(f"{boss['name']}  PHASE {boss['phase']}" + ("  [ENRAGE]" if boss["enrage"] else ""),True,YELLOW)
        ds.blit(bl,(WIDTH//2-bl.get_width()//2,48))

    # Player bullets (trails)
    for b in game["bullets"]:
        col=b["color"]
        for j,(tx2,ty2) in enumerate(b["trail"]):
            af=(j+1)/(len(b["trail"])+1)
            tc=tuple(int(c*af*0.5) for c in col)
            pygame.draw.circle(ds,tc,(tx2,ty2),max(1,int(4*af)))
        sz=7 if b["weapon"]=="plasma" else (5 if b["weapon"] in("laser","shotgun","sniper") else 5)
        pygame.draw.circle(ds,WHITE,(int(b["x"]),int(b["y"])),sz-1)
        pygame.draw.circle(ds,col,(int(b["x"]),int(b["y"])),sz-2)
        # Rocket glow
        if b["weapon"]=="rocket":
            pygame.draw.circle(ds,ORANGE,(int(b["x"]),int(b["y"])),sz+3,1)

    # Player
    flash=game["invincible_timer"]>0 and (t_now//5)%2==0
    if not flash:
        shield_on=game["invincible_timer"]>60
        if shield_on:
            sp2=int(abs(math.sin(t_now*0.1))*4)
            pygame.draw.circle(ds,BLUE,(int(px),int(py)),32+sp2,2)
        pygame.draw.circle(ds,BLUE,(int(px),int(py)),20)
        pygame.draw.circle(ds,CYAN,(int(px),int(py)),11)
        mx2,my2=pygame.mouse.get_pos()
        angle=math.atan2(my2-py,mx2-px)
        gx=px+math.cos(angle)*30; gy=py+math.sin(angle)*30
        wc=WEAPONS[game["weapon"]]["color"]
        pygame.draw.line(ds,wc,(int(px),int(py)),(int(gx),int(gy)),6)
        pygame.draw.line(ds,WHITE,(int(px),int(py)),(int(gx),int(gy)),2)
        # Dash trail
        if game["dash_cooldown"]>40:
            for i in range(4):
                tx3=px-math.cos(angle)*(i+1)*10
                ty3=py-math.sin(angle)*(i+1)*10
                a3=max(0,100-i*28)
                pygame.draw.circle(ds,(30,80,a3),(int(tx3),int(ty3)),max(2,11-i*3))

    # Floaters
    for f in game["floaters"]:
        af=f["life"]/f["max_life"]
        cf=tuple(int(c*af) for c in f["color"])
        ft=F_SM.render(f["text"],True,cf)
        ds.blit(ft,(int(f["x"])-ft.get_width()//2,int(f["y"])))

    draw_hud(ds)
    screen.blit(ds,(shake_x,shake_y))
    pygame.display.flip()

pygame.quit()
sys.exit()
