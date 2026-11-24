---
title: "Barista Cafe game"
excerpt: "Step into a cozy fantasy-themed coffee shop where every adventurer needs their daily brew.<br/><img src='/images/Screenshot 2026-11-25 002026.png'>"
collection: portfolio
---

import pygame
import random
import math
import sys

# ==============================================================================
# INITIALIZATION & CONSTANTS
# ==============================================================================
pygame.init()

SCREEN_WIDTH = 1220
SCREEN_HEIGHT = 720
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Barista Cafe - Character & Clean Layout Edition")
clock = pygame.time.Clock()

# Warm Cozy Cafe Palette
BRICK_WALL = (134, 82, 58)
BRICK_DARK = (106, 62, 44)
BRICK_LIGHT = (156, 98, 70)
MORTAR_COL = (118, 72, 50)

ARCH_FRAME = (204, 176, 146)
ARCH_TRIM = (108, 78, 54)
SKY_MORNING = (248, 228, 192)
SUN_SOFT = (255, 248, 226)
EXT_BUILDING = (218, 190, 160)
EXT_TREE = (138, 152, 94)
EXT_TREE_DARK = (112, 128, 74)

WOOD_COUNTER_TOP = (194, 134, 84)
WOOD_COUNTER_HIGHLIGHT = (214, 156, 104)
WOOD_COUNTER_EDGE = (138, 84, 46)
WOOD_COUNTER_FRONT = (106, 62, 34)
WOOD_GRAIN = (168, 112, 66)
WOOD_DARK = (62, 34, 18)
BOARD_TRAY = (216, 166, 116)

BRASS_GOLD = (216, 168, 78)
BRASS_LIGHT = (250, 222, 142)
COPPER_DARK = (156, 84, 46)
COPPER_LIGHT = (214, 136, 86)
CHALKBOARD_BG = (48, 46, 44)

# Drink & Ingredient Colors
COL_ESPRESSO = (66, 34, 18)
COL_MATCHA = (94, 156, 62)
COL_CHOCOLATE = (110, 54, 26)
COL_WATER = (136, 204, 244)
COL_MILK = (252, 249, 242)
COL_OAT_MILK = (234, 216, 184)
COL_WHIPPED = (255, 252, 246)
COL_CARAMEL = (212, 122, 26)

PARCHMENT_BG = (248, 238, 220)
PARCHMENT_DARK = (226, 210, 184)
GOLD_BORDER = (164, 126, 78)
HUD_BAR_BG = (238, 224, 202)
HUD_PILL_BG = (112, 78, 54)

BTN_SERVE = (118, 112, 98)
BTN_SERVE_READY = (76, 146, 88)
BTN_SERVE_HOVER = (96, 168, 108)
BTN_TRASH = (156, 62, 54)
BTN_TRASH_HOVER = (182, 78, 68)

TEXT_DARK = (50, 32, 18)
TEXT_BROWN = (102, 64, 38)
TEXT_WHITE = (255, 252, 245)
TEXT_CREAM = (246, 232, 206)

# Safe Cross-Platform Fonts
FONT_TITLE = pygame.font.Font(None, 62)
FONT_HEADER = pygame.font.Font(None, 30)
FONT_MED = pygame.font.Font(None, 24)
FONT_SMALL = pygame.font.Font(None, 20)
FONT_TINY = pygame.font.Font(None, 16)

# Menu Recipes
MENU_RECIPES = [
    {"name": "Hot Americano", "cup": "Hot Cup", "base": "Espresso", "liquid": "Water", "topping": "None", "price": 10},
    {"name": "Iced Americano", "cup": "Iced Cup", "base": "Espresso", "liquid": "Water", "topping": "None", "price": 11},
    {"name": "Hot Cafe Latte", "cup": "Hot Cup", "base": "Espresso", "liquid": "Milk", "topping": "None", "price": 12},
    {"name": "Iced Oat Latte", "cup": "Iced Cup", "base": "Espresso", "liquid": "Oat Milk", "topping": "None", "price": 14},
    {"name": "Caramel Macchiato", "cup": "Hot Cup", "base": "Espresso", "liquid": "Milk", "topping": "Caramel", "price": 15},
    {"name": "Iced Matcha Whip", "cup": "Iced Cup", "base": "Matcha", "liquid": "Oat Milk", "topping": "Whipped Cream", "price": 16},
    {"name": "Hot Matcha Latte", "cup": "Hot Cup", "base": "Matcha", "liquid": "Milk", "topping": "None", "price": 13},
    {"name": "Hot Choco Whip", "cup": "Hot Cup", "base": "Chocolate", "liquid": "Milk", "topping": "Whipped Cream", "price": 14},
    {"name": "Iced Caramel Mocha", "cup": "Iced Cup", "base": "Chocolate", "liquid": "Oat Milk", "topping": "Caramel", "price": 16},
]

# Distinct Character Roster (Inspired by Fantasy Adventurer Archetypes)
CHARACTER_ROSTER = [
    {
        "id": "elara",
        "name": "Elara",
        "age": 25,
        "height_offset": 0,
        "skin": (248, 212, 184),
        "skin_shadow": (222, 178, 148),
        "hair": (132, 78, 46),
        "outfit": (152, 134, 98),
        "cloak": (78, 84, 88),
    },
    {
        "id": "leo",
        "name": "Leo",
        "age": 8,
        "height_offset": 26,  # Shorter kid stature
        "skin": (252, 216, 186),
        "skin_shadow": (226, 182, 150),
        "hair": (42, 44, 48),
        "outfit": (94, 152, 82),
        "cloak": (146, 96, 58),  # Backpack strap color
    },
    {
        "id": "kael",
        "name": "Kael",
        "age": 35,
        "height_offset": -14,  # Taller muscular warrior stature
        "skin": (236, 192, 158),
        "skin_shadow": (206, 158, 124),
        "hair": (58, 52, 48),
        "outfit": (118, 76, 52),
        "cloak": (68, 74, 72),
    },
    {
        "id": "iris",
        "name": "Iris",
        "age": 70,
        "height_offset": 4,
        "skin": (246, 214, 192),
        "skin_shadow": (218, 180, 156),
        "hair": (228, 230, 235),
        "outfit": (68, 92, 128),
        "cloak": (128, 114, 96),
    },
]

# ==============================================================================
# GRAPHICS & ICON HELPERS
# ==============================================================================

def draw_rounded_rect(surface, color, rect, radius=12, border_width=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_width > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=radius)

def draw_soft_shadow(surface, rect_or_ellipse, is_ellipse=True, alpha=65):
    sh_surf = pygame.Surface((rect_or_ellipse[2], rect_or_ellipse[3]), pygame.SRCALPHA)
    if is_ellipse:
        pygame.draw.ellipse(sh_surf, (32, 18, 10, alpha), (0, 0, rect_or_ellipse[2], rect_or_ellipse[3]))
    else:
        pygame.draw.rect(sh_surf, (32, 18, 10, alpha), (0, 0, rect_or_ellipse[2], rect_or_ellipse[3]), border_radius=12)
    surface.blit(sh_surf, (rect_or_ellipse[0], rect_or_ellipse[1]))

def blend_colors(c1, c2, ratio=0.5):
    return (
        int(c1[0] * (1 - ratio) + c2[0] * ratio),
        int(c1[1] * (1 - ratio) + c2[1] * ratio),
        int(c1[2] * (1 - ratio) + c2[2] * ratio),
    )

def get_ingredient_color(name):
    mapping = {
        "Espresso": COL_ESPRESSO,
        "Matcha": COL_MATCHA,
        "Chocolate": COL_CHOCOLATE,
        "Water": COL_WATER,
        "Milk": COL_MILK,
        "Oat Milk": COL_OAT_MILK,
    }
    return mapping.get(name, (200, 200, 200))

def draw_illustrated_icon(surface, item, cx, cy, scale=1.0):
    s = scale
    if item == "Hot Cup":
        pygame.draw.ellipse(surface, (238, 228, 214), (cx - int(18*s), cy + int(7*s), int(36*s), int(10*s)))
        pygame.draw.ellipse(surface, TEXT_DARK, (cx - int(18*s), cy + int(7*s), int(36*s), int(10*s)), 1)
        mug = pygame.Rect(cx - int(13*s), cy - int(8*s), int(26*s), int(19*s))
        pygame.draw.rect(surface, (248, 242, 232), mug, border_bottom_left_radius=8, border_bottom_right_radius=8)
        pygame.draw.rect(surface, TEXT_DARK, mug, width=2, border_bottom_left_radius=8, border_bottom_right_radius=8)
        pygame.draw.arc(surface, TEXT_DARK, (cx + int(10*s), cy - int(5*s), int(10*s), int(12*s)), -math.pi/2, math.pi/2, 2)
        pygame.draw.ellipse(surface, (196, 138, 78), (cx - int(11*s), cy - int(10*s), int(22*s), int(6*s)))

    elif item == "Iced Cup":
        pts = [(cx - int(11*s), cy - int(12*s)), (cx + int(11*s), cy - int(12*s)),
               (cx + int(8*s), cy + int(13*s)), (cx - int(8*s), cy + int(13*s))]
        pygame.draw.polygon(surface, (204, 238, 255), pts)
        pygame.draw.rect(surface, (242, 252, 255), (cx - int(6*s), cy - int(6*s), int(6*s), int(6*s)), border_radius=2)
        pygame.draw.rect(surface, (242, 252, 255), (cx + int(1*s), cy - int(2*s), int(6*s), int(6*s)), border_radius=2)
        pygame.draw.polygon(surface, TEXT_DARK, pts, 2)

    elif item in ("Espresso", "Matcha"):
        pygame.draw.ellipse(surface, (232, 220, 204), (cx - int(17*s), cy + int(7*s), int(34*s), int(9*s)))
        cup = pygame.Rect(cx - int(12*s), cy - int(6*s), int(24*s), int(16*s))
        pygame.draw.rect(surface, (245, 238, 228), cup, border_bottom_left_radius=7, border_bottom_right_radius=7)
        pygame.draw.rect(surface, TEXT_DARK, cup, width=2, border_bottom_left_radius=7, border_bottom_right_radius=7)
        liq_col = COL_ESPRESSO if item == "Espresso" else COL_MATCHA
        pygame.draw.ellipse(surface, liq_col, (cx - int(10*s), cy - int(8*s), int(20*s), int(6*s)))

    elif item == "Chocolate":
        bar = pygame.Rect(cx - int(13*s), cy - int(10*s), int(26*s), int(20*s))
        draw_rounded_rect(surface, COL_CHOCOLATE, bar, radius=4, border_width=2, border_color=TEXT_DARK)
        pygame.draw.line(surface, (152, 84, 48), (cx, bar.top + 2), (cx, bar.bottom - 2), 2)
        pygame.draw.line(surface, (152, 84, 48), (bar.left + 2, cy), (bar.right - 2, cy), 2)

    elif item == "Water":
        pygame.draw.circle(surface, COL_WATER, (cx, cy + int(4*s)), int(10*s))
        pygame.draw.polygon(surface, COL_WATER, [(cx - int(10*s), cy + int(3*s)), (cx + int(10*s), cy + int(3*s)), (cx, cy - int(13*s))])
        pygame.draw.circle(surface, TEXT_WHITE, (cx - int(3*s), cy + int(3*s)), int(3*s))

    elif item in ("Milk", "Oat Milk"):
        col = COL_MILK if item == "Milk" else COL_OAT_MILK
        body = pygame.Rect(cx - int(9*s), cy - int(4*s), int(18*s), int(18*s))
        neck = pygame.Rect(cx - int(5*s), cy - int(12*s), int(10*s), int(10*s))
        draw_rounded_rect(surface, col, body, radius=4, border_width=2, border_color=TEXT_DARK)
        pygame.draw.rect(surface, col, neck)
        pygame.draw.rect(surface, TEXT_DARK, neck, 2)
        pygame.draw.rect(surface, (186, 136, 76), (cx - int(6*s), cy - int(14*s), int(12*s), int(4*s)), border_radius=2)

    elif item == "Whipped Cream":
        pygame.draw.ellipse(surface, COL_WHIPPED, (cx - int(14*s), cy + int(1*s), int(28*s), int(11*s)))
        pygame.draw.ellipse(surface, TEXT_DARK, (cx - int(14*s), cy + int(1*s), int(28*s), int(11*s)), 1)
        pygame.draw.ellipse(surface, COL_WHIPPED, (cx - int(10*s), cy - int(6*s), int(20*s), int(10*s)))
        pygame.draw.ellipse(surface, TEXT_DARK, (cx - int(10*s), cy - int(6*s), int(20*s), int(10*s)), 1)
        pygame.draw.ellipse(surface, COL_WHIPPED, (cx - int(5*s), cy - int(12*s), int(10*s), int(8*s)))

    elif item == "Caramel":
        cube = pygame.Rect(cx - int(10*s), cy - int(6*s), int(20*s), int(16*s))
        draw_rounded_rect(surface, COL_CARAMEL, cube, radius=5, border_width=2, border_color=TEXT_DARK)
        pygame.draw.lines(surface, (255, 212, 118), False, [
            (cx - int(12*s), cy - int(8*s)), (cx - int(4*s), cy - int(13*s)),
            (cx + int(4*s), cy - int(7*s)), (cx + int(12*s), cy - int(12*s))
        ], 3)

# ==============================================================================
# CLEANLY ORGANIZED CAFE ARCHITECTURE (3 CLEAR ZONES: WINDOW | ORDER | BREW BAR)
# ==============================================================================

def draw_cafe_back_wall(surface, anim_time):
    """Draws an uncluttered, well-organized cozy cafe interior with 3 clear visual zones."""
    surface.fill(MORTAR_COL)

    # 1. Brick Texture Pattern
    for row_idx, by in enumerate(range(54, 410, 22)):
        offset = 24 if row_idx % 2 == 1 else 0
        for col_idx, bx in enumerate(range(-24 + offset, SCREEN_WIDTH, 48)):
            seed = (row_idx * 17 + col_idx * 31) % 5
            col = BRICK_DARK if seed == 0 else (BRICK_LIGHT if seed == 1 else BRICK_WALL)
            pygame.draw.rect(surface, col, (bx, by, 44, 18), border_radius=2)

    # 2. ZONE 1 (LEFT): Grand Arched Cafe Window
    win_x, win_y, win_w, win_h = 28, 82, 230, 320
    pygame.draw.ellipse(surface, SKY_MORNING, (win_x, win_y, win_w, win_w))
    pygame.draw.rect(surface, SKY_MORNING, (win_x, win_y + win_w // 2, win_w, win_h - win_w // 2))
    pygame.draw.circle(surface, SUN_SOFT, (win_x + 140, win_y + 102), 38)

    pygame.draw.rect(surface, EXT_BUILDING, (win_x + 10, win_y + 138, 84, 182))
    pygame.draw.rect(surface, (198, 168, 138), (win_x + 148, win_y + 155, 72, 165))
    for tx, ty, tr in [(win_x + 110, win_y + 175, 36), (win_x + 145, win_y + 185, 32), (win_x + 78, win_y + 195, 28)]:
        pygame.draw.circle(surface, EXT_TREE_DARK, (tx, ty + 4), tr)
        pygame.draw.circle(surface, EXT_TREE, (tx, ty), int(tr * 0.92))

    pygame.draw.line(surface, ARCH_FRAME, (win_x + win_w // 2, win_y), (win_x + win_w // 2, win_y + win_h), 6)
    pygame.draw.line(surface, ARCH_FRAME, (win_x, win_y + 125), (win_x + win_w, win_y + 125), 6)
    pygame.draw.line(surface, ARCH_FRAME, (win_x, win_y + 220), (win_x + win_w, win_y + 220), 6)
    pygame.draw.arc(surface, ARCH_FRAME, (win_x + 24, win_y + 24, win_w - 48, win_w - 48), 0, math.pi, 5)
    pygame.draw.ellipse(surface, ARCH_TRIM, (win_x - 6, win_y - 6, win_w + 12, win_w + 12), 9)
    pygame.draw.rect(surface, ARCH_TRIM, (win_x - 6, win_y + win_w // 2, win_w + 12, win_h - win_w // 2), 9)

    # 3. ZONE 3 (RIGHT): Tidy Menu Chalkboard, Shelves & Espresso Station
    # Clean single chalkboard on the upper-right wall
    board = pygame.Rect(735, 96, 185, 160)
    draw_rounded_rect(surface, CHALKBOARD_BG, board, radius=8, border_width=5, border_color=WOOD_DARK)
    surface.blit(FONT_SMALL.render("CAFE MENU", True, (242, 212, 148)), (782, 108))
    pygame.draw.line(surface, (160, 140, 110), (750, 130), (905, 130), 1)
    surface.blit(FONT_TINY.render("* Americano / Latte", True, TEXT_CREAM), (748, 142))
    surface.blit(FONT_TINY.render("* Caramel Macchiato", True, TEXT_CREAM), (748, 166))
    surface.blit(FONT_TINY.render("* Matcha & Oat Milk", True, TEXT_CREAM), (748, 190))
    surface.blit(FONT_TINY.render("* Hot Choco Whip", True, TEXT_CREAM), (748, 214))

    # Tidy Coffee Bean Shelves (Far Right)
    for sy in [150, 226]:
        draw_soft_shadow(surface, (945, sy + 7, 245, 7), is_ellipse=False, alpha=65)
        pygame.draw.rect(surface, WOOD_COUNTER_FRONT, (945, sy, 245, 9), border_radius=3)

    for i, col in enumerate([(136, 78, 42), (176, 112, 56), (118, 68, 36)]):
        jx = 960 + i * 64
        draw_rounded_rect(surface, col, pygame.Rect(jx, 102, 42, 48), radius=8, border_width=2, border_color=TEXT_DARK)
        pygame.draw.rect(surface, ARCH_FRAME, (jx + 6, 95, 30, 8), border_radius=3)

    for i in range(3):
        bx = 962 + i * 64
        draw_rounded_rect(surface, (206, 168, 118), pygame.Rect(bx, 176, 40, 50), radius=4, border_width=2, border_color=WOOD_DARK)
        pygame.draw.rect(surface, (118, 72, 42), (bx + 7, 192, 26, 15), border_radius=2)

    # Potted Ivy Plants placed neatly at corners
    for px, py in [(272, 114), (1162, 114)]:
        pygame.draw.polygon(surface, (176, 92, 56), [(px - 16, py - 15), (px + 16, py - 15), (px + 11, py + 5), (px - 11, py + 5)])
        for dx, dy, r in [(-13, -18, 13), (0, -22, 15), (13, -17, 13), (-16, -3, 10), (16, 2, 10)]:
            pygame.draw.circle(surface, (76, 126, 64), (px + dx, py + dy), r)

    # Copper & Brass Espresso Machine Station (Right Counter)
    for ux in [745, 1130]:
        draw_rounded_rect(surface, COPPER_DARK, pygame.Rect(ux, 272, 42, 110), radius=14, border_width=2, border_color=TEXT_DARK)
        pygame.draw.rect(surface, COPPER_LIGHT, (ux + 8, 280, 10, 92), border_radius=5)

    mach = pygame.Rect(798, 282, 320, 100)
    draw_rounded_rect(surface, (218, 202, 176), mach, radius=12, border_width=3, border_color=TEXT_DARK)
    pygame.draw.rect(surface, BRASS_GOLD, (804, 288, 308, 26), border_radius=6)
    # Dual Pressure Gauges
    for px_g in [865, 1050]:
        pygame.draw.circle(surface, TEXT_WHITE, (px_g, 301), 10)
        pygame.draw.circle(surface, TEXT_DARK, (px_g, 301), 10, 2)
        pygame.draw.line(surface, BTN_TRASH, (px_g, 301), (px_g + 5, 296), 2)
    # Triple Group Heads & Portafilters
    for gx in [885, 958, 1030]:
        pygame.draw.rect(surface, WOOD_DARK, (gx - 13, 316, 26, 15), border_radius=3)
        pygame.draw.line(surface, WOOD_DARK, (gx, 324), (gx + 18, 332), 5)
    pygame.draw.rect(surface, COPPER_DARK, (806, 370, 304, 12), border_radius=3)

    # Warm String Fairy Lights & Brass Pendant Lamps
    light_overlay = pygame.Surface((SCREEN_WIDTH, 410), pygame.SRCALPHA)
    pygame.draw.polygon(light_overlay, (255, 244, 198, 30), [(50, 115), (235, 115), (380, 405), (130, 405)])

    for idx, lx in enumerate([355, 575]):
        sway = int(math.sin(anim_time * 1.4 + idx) * 2)
        lamp_x = lx + sway
        pygame.draw.polygon(light_overlay, (255, 224, 138, 36), [(lamp_x - 26, 132), (lamp_x + 26, 132), (lamp_x + 125, 405), (lamp_x - 125, 405)])
        surface.blit(light_overlay, (0, 0))
        pygame.draw.line(surface, WOOD_DARK, (lx, 56), (lamp_x, 104), 3)
        pygame.draw.circle(surface, BRASS_LIGHT, (lamp_x, 132), 11)
        pygame.draw.polygon(surface, BRASS_GOLD, [(lamp_x - 14, 102), (lamp_x + 14, 102), (lamp_x + 32, 132), (lamp_x - 32, 132)])
        pygame.draw.polygon(surface, TEXT_DARK, [(lamp_x - 14, 102), (lamp_x + 14, 102), (lamp_x + 32, 132), (lamp_x - 32, 132)], 2)

    bulb_pts = []
    for bx in range(20, SCREEN_WIDTH, 38):
        by = 66 + int(abs(math.sin(bx * 0.008)) * 18)
        bulb_pts.append((bx, by))
    if len(bulb_pts) > 1:
        pygame.draw.lines(surface, WOOD_DARK, False, bulb_pts, 2)
    for bx, by in bulb_pts:
        glow = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 236, 150, 75), (11, 11), 10)
        surface.blit(glow, (bx - 11, by - 7))
        pygame.draw.circle(surface, (255, 242, 175), (bx, by + 4), 4)

def draw_cafe_foreground_counter(surface):
    """Draws the clean curved wooden bar counter in front of the customer."""
    pygame.draw.rect(surface, WOOD_COUNTER_TOP, (175, 380, SCREEN_WIDTH - 175, 190))
    pygame.draw.ellipse(surface, WOOD_COUNTER_TOP, (125, 380, 170, 200))

    for gy in [404, 432, 460, 518, 548]:
        pygame.draw.line(surface, WOOD_GRAIN, (185, gy), (SCREEN_WIDTH - 12, gy), 2)
    pygame.draw.line(surface, WOOD_COUNTER_HIGHLIGHT, (210, 385), (SCREEN_WIDTH - 10, 385), 3)

    pygame.draw.arc(surface, WOOD_DARK, (125, 380, 170, 200), math.pi * 0.5, math.pi * 1.42, 3)
    pygame.draw.line(surface, WOOD_DARK, (205, 380), (SCREEN_WIDTH, 380), 3)

    pygame.draw.rect(surface, WOOD_COUNTER_FRONT, (175, 565, SCREEN_WIDTH - 175, SCREEN_HEIGHT - 565))
    pygame.draw.line(surface, WOOD_COUNTER_EDGE, (175, 565), (SCREEN_WIDTH, 565), 8)
    pygame.draw.line(surface, WOOD_DARK, (175, 561), (SCREEN_WIDTH, 561), 3)

    # Central Raised Wooden Serving Tray
    tray_pts = [(445, 466), (775, 466), (802, 544), (418, 544)]
    shadow_pts = [(p[0], p[1] + 9) for p in tray_pts]
    pygame.draw.polygon(surface, (88, 52, 28), shadow_pts)
    pygame.draw.polygon(surface, WOOD_COUNTER_EDGE, [(p[0], p[1] + 5) for p in tray_pts])
    pygame.draw.polygon(surface, BOARD_TRAY, tray_pts)
    pygame.draw.line(surface, WOOD_COUNTER_HIGHLIGHT, (450, 469), (770, 469), 2)
    pygame.draw.polygon(surface, WOOD_DARK, tray_pts, 2)

    # Decorative plate & cookie on the right counter
    draw_soft_shadow(surface, (852, 496, 78, 28), is_ellipse=True, alpha=60)
    pygame.draw.ellipse(surface, (245, 238, 228), (855, 492, 74, 24))
    pygame.draw.ellipse(surface, TEXT_DARK, (855, 492, 74, 24), 2)

    draw_soft_shadow(surface, (865, 524, 50, 22), is_ellipse=True, alpha=60)
    pygame.draw.ellipse(surface, (196, 134, 72), (868, 520, 46, 20))
    pygame.draw.ellipse(surface, TEXT_DARK, (868, 520, 46, 20), 2)

# ==============================================================================
# CUSTOM ILLUSTRATED CHARACTERS (ELARA, LEO, KAEL, IRIS) & NAME TAGS
# ==============================================================================

def generate_customer():
    """Selects one of the 4 distinct characters and assigns a random cafe order."""
    char = random.choice(CHARACTER_ROSTER).copy()
    char["recipe"] = random.choice(MENU_RECIPES)
    char["bob_phase"] = random.uniform(0, 6.28)
    return char

def draw_customer(surface, cust, x, base_y, anim_time):
    """Draws Elara (25), Leo (8), Kael (35), or Iris (70) with unique outfits and props."""
    bob = int(math.sin(anim_time * 2.6 + cust["bob_phase"]) * 3)
    cy = base_y + cust["height_offset"] + bob
    cid = cust["id"]

    # 1. Character-Specific Back Props (Sword / Staff / Cloak / Backpack)
    if cid == "kael":
        # Greatsword hilt over right shoulder
        pygame.draw.line(surface, (165, 172, 180), (x - 42, cy - 48), (x - 16, cy + 10), 7)
        pygame.draw.line(surface, TEXT_DARK, (x - 42, cy - 48), (x - 16, cy + 10), 2)
        pygame.draw.line(surface, (92, 64, 44), (x - 52, cy - 32), (x - 28, cy - 44), 6)
        pygame.draw.circle(surface, (186, 152, 82), (x - 44, cy - 50), 5)

    elif cid == "leo":
        # Green backpack & wooden sword over shoulder
        draw_rounded_rect(surface, (82, 126, 72), pygame.Rect(x + 22, cy + 14, 24, 46), radius=8, border_width=2, border_color=TEXT_DARK)
        pygame.draw.line(surface, (192, 144, 92), (x - 44, cy - 18), (x - 14, cy + 22), 8)
        pygame.draw.line(surface, TEXT_DARK, (x - 44, cy - 18), (x - 14, cy + 22), 2)
        pygame.draw.line(surface, (142, 96, 54), (x - 48, cy - 4), (x - 32, cy - 16), 5)

    elif cid == "iris":
        # Wooden staff with glowing cyan orb on left
        staff_x = x - 52
        pygame.draw.line(surface, (118, 76, 46), (staff_x, cy - 48), (staff_x, cy + 85), 5)
        pygame.draw.arc(surface, (118, 76, 46), (staff_x - 12, cy - 66, 24, 26), 0.3, math.pi * 1.6, 5)
        glow = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.circle(glow, (110, 235, 255, 110), (18, 18), 16)
        surface.blit(glow, (staff_x - 18, cy - 72))
        pygame.draw.circle(surface, (185, 248, 255), (staff_x, cy - 54), 7)

    # 2. Back Hair Volume
    if cid == "elara":
        pygame.draw.ellipse(surface, cust["hair"], (x - 40, cy - 38, 80, 68))
        # Braided side lock over shoulder
        for by_off in range(0, 42, 10):
            pygame.draw.circle(surface, cust["hair"], (x + 24, cy + 4 + by_off), 7)
            pygame.draw.circle(surface, TEXT_DARK, (x + 24, cy + 4 + by_off), 7, 1)
    elif cid == "leo":
        # Spiky dark hair silhouette
        for dx, dy, r in [(-28, -28, 16), (-14, -42, 18), (4, -44, 18), (22, -36, 17), (32, -20, 15), (-34, -14, 14)]:
            pygame.draw.circle(surface, cust["hair"], (x + dx, cy + dy), r)

    # 3. Torso / Outfit / Cloak
    w_half = 54 if cid == "kael" else (42 if cid == "leo" else 46)
    shoulder_pts = [
        (x - w_half, cy + 85),
        (x - w_half + 6, cy + 40),
        (x - 22, cy + 28),
        (x + 22, cy + 28),
        (x + w_half - 6, cy + 40),
        (x + w_half, cy + 85),
    ]
    pygame.draw.polygon(surface, cust["outfit"], shoulder_pts)
    pygame.draw.polygon(surface, TEXT_DARK, shoulder_pts, 2)

    if cid == "elara":
        # Dark grey traveler capelet over shoulders
        cape_pts = [(x - 48, cy + 56), (x - 42, cy + 34), (x, cy + 28), (x + 42, cy + 34), (x + 48, cy + 56)]
        pygame.draw.polygon(surface, cust["cloak"], cape_pts)
        pygame.draw.polygon(surface, TEXT_DARK, cape_pts, 2)
        # Crossbody leather strap
        pygame.draw.line(surface, (112, 68, 42), (x - 26, cy + 32), (x + 24, cy + 78), 6)

    elif cid == "leo":
        # Hoodie drawstrings
        pygame.draw.line(surface, TEXT_WHITE, (x - 8, cy + 34), (x - 8, cy + 54), 2)
        pygame.draw.line(surface, TEXT_WHITE, (x + 8, cy + 34), (x + 8, cy + 54), 2)

    elif cid == "kael":
        # Steel pauldron armor on left shoulder + dark scarf
        pygame.draw.ellipse(surface, (148, 154, 162), (x - 56, cy + 24, 38, 28))
        pygame.draw.ellipse(surface, TEXT_DARK, (x - 56, cy + 24, 38, 28), 2)
        scarf = pygame.Rect(x - 28, cy + 22, 56, 18)
        draw_rounded_rect(surface, cust["cloak"], scarf, radius=8, border_width=2, border_color=TEXT_DARK)

    elif cid == "iris":
        # Warm woven shawl & gold-trimmed blue robe
        shawl_pts = [(x - 48, cy + 54), (x - 40, cy + 30), (x + 40, cy + 30), (x + 48, cy + 54)]
        pygame.draw.polygon(surface, cust["cloak"], shawl_pts)
        pygame.draw.polygon(surface, TEXT_DARK, shawl_pts, 2)
        pygame.draw.line(surface, BRASS_GOLD, (x - 14, cy + 54), (x - 14, cy + 84), 3)
        pygame.draw.line(surface, BRASS_GOLD, (x + 14, cy + 54), (x + 14, cy + 84), 3)

    # 4. Neck & Head
    pygame.draw.rect(surface, cust["skin_shadow"], (x - 10, cy + 14, 20, 18))
    head_r = 34 if cid == "leo" else 35
    pygame.draw.circle(surface, cust["skin"], (x, cy - 12), head_r)
    pygame.draw.arc(surface, cust["skin_shadow"], (x - head_r + 2, cy - 12 - head_r + 2, (head_r - 2) * 2, (head_r - 2) * 2), math.pi * 0.7, math.pi * 1.4, 4)
    pygame.draw.circle(surface, TEXT_DARK, (x, cy - 12), head_r, 2)

    # 5. Character-Specific Hair & Facial Features
    if cid == "elara":
        pygame.draw.arc(surface, cust["hair"], (x - 36, cy - 48, 72, 48), 0.15, math.pi - 0.15, 12)
        pygame.draw.ellipse(surface, (238, 146, 138), (x - 24, cy - 6, 11, 6))
        pygame.draw.ellipse(surface, (238, 146, 138), (x + 13, cy - 6, 11, 6))

    elif cid == "leo":
        pygame.draw.arc(surface, cust["hair"], (x - 35, cy - 46, 70, 44), 0.1, math.pi - 0.1, 13)
        pygame.draw.ellipse(surface, (242, 152, 144), (x - 23, cy - 5, 11, 6))
        pygame.draw.ellipse(surface, (242, 152, 144), (x + 12, cy - 5, 11, 6))

    elif cid == "kael":
        # Short textured hair + full beard & mustache
        pygame.draw.arc(surface, cust["hair"], (x - 36, cy - 48, 72, 44), 0.1, math.pi - 0.1, 12)
        beard_pts = [(x - 31, cy - 10), (x - 24, cy + 16), (x, cy + 24), (x + 24, cy + 16), (x + 31, cy - 10),
                     (x + 20, cy + 4), (x - 20, cy + 4)]
        pygame.draw.polygon(surface, cust["hair"], beard_pts)
        pygame.draw.polygon(surface, TEXT_DARK, beard_pts, 1)

    elif cid == "iris":
        # White hair bun on top + parted white hair + gentle age lines
        pygame.draw.circle(surface, cust["hair"], (x, cy - 52), 16)
        pygame.draw.circle(surface, TEXT_DARK, (x, cy - 52), 16, 2)
        pygame.draw.arc(surface, cust["hair"], (x - 36, cy - 48, 72, 48), 0.1, math.pi - 0.1, 12)
        pygame.draw.arc(surface, cust["skin_shadow"], (x - 24, cy - 4, 10, 12), math.pi * 0.5, math.pi * 1.4, 2)
        pygame.draw.arc(surface, cust["skin_shadow"], (x + 14, cy - 4, 10, 12), -math.pi * 0.4, math.pi * 0.5, 2)

    # Eyebrows & Blinking Eyes
    brow_w = 3 if cid == "kael" else 2
    pygame.draw.arc(surface, TEXT_DARK, (x - 19, cy - 23, 13, 6), 0.2, math.pi - 0.2, brow_w)
    pygame.draw.arc(surface, TEXT_DARK, (x + 6, cy - 23, 13, 6), 0.2, math.pi - 0.2, brow_w)

    is_blinking = ((anim_time + cust["bob_phase"]) % 3.8) > 3.62
    if is_blinking:
        pygame.draw.arc(surface, TEXT_DARK, (x - 18, cy - 15, 12, 7), math.pi, 2 * math.pi, 2)
        pygame.draw.arc(surface, TEXT_DARK, (x + 6, cy - 15, 12, 7), math.pi, 2 * math.pi, 2)
    else:
        pygame.draw.circle(surface, TEXT_DARK, (x - 12, cy - 13), 4)
        pygame.draw.circle(surface, TEXT_DARK, (x + 12, cy - 13), 4)
        pygame.draw.circle(surface, TEXT_WHITE, (x - 13, cy - 14), 1)
        pygame.draw.circle(surface, TEXT_WHITE, (x + 11, cy - 14), 1)

    # Smile
    if cid == "leo":
        # Big cheerful open grin
        pygame.draw.chord(surface, TEXT_WHITE, (x - 10, cy - 6, 20, 14), math.pi, 2 * math.pi, 0)
        pygame.draw.arc(surface, TEXT_DARK, (x - 10, cy - 6, 20, 14), math.pi, 2 * math.pi, 2)
    else:
        pygame.draw.arc(surface, TEXT_DARK, (x - 9, cy - 5, 18, 10), math.pi + 0.2, 2 * math.pi - 0.2, 2)

def draw_customer_name_badge(surface, cust, x, y):
    """Draws the clean '(Name, Age)' nameplate badge on the front edge of the counter."""
    tag_text = f"({cust['name']}, {cust['age']})"
    badge = pygame.Rect(x - 62, y, 124, 28)
    draw_soft_shadow(surface, (badge.x + 2, badge.y + 3, badge.width, badge.height), is_ellipse=False, alpha=60)
    draw_rounded_rect(surface, PARCHMENT_BG, badge, radius=10, border_width=2, border_color=GOLD_BORDER)
    txt = FONT_SMALL.render(tag_text, True, TEXT_DARK)
    surface.blit(txt, txt.get_rect(center=badge.center))

def draw_single_order_card(surface, rect, cust):
    """Draws a single, spacious, ultra-clear parchment order card in the center-top zone."""
    rec = cust["recipe"]
    steps = [rec["cup"], rec["base"], rec["liquid"]]
    if rec["topping"] != "None":
        steps.append(rec["topping"])

    draw_soft_shadow(surface, (rect.x + 4, rect.y + 6, rect.width, rect.height), is_ellipse=False, alpha=75)
    draw_rounded_rect(surface, PARCHMENT_BG, rect, radius=16, border_width=3, border_color=GOLD_BORDER)
    pygame.draw.rect(surface, PARCHMENT_DARK, rect.inflate(-10, -10), width=2, border_radius=12)

    # Header: Customer Name (Age) + Drink Name
    header_txt = f"{cust['name']} ({cust['age']})  •  {rec['name']}"
    t_surf = FONT_HEADER.render(header_txt, True, TEXT_DARK)
    surface.blit(t_surf, t_surf.get_rect(center=(rect.centerx, rect.y + 26)))
    pygame.draw.line(surface, GOLD_BORDER, (rect.x + 24, rect.y + 46), (rect.right - 24, rect.y + 46), 2)

    # Step-by-Step Illustrated Recipe Boxes
    cols = len(steps)
    box_w = 78
    gap = 12
    total_w = cols * box_w + (cols - 1) * gap
    start_x = rect.centerx - total_w // 2

    for idx, label in enumerate(steps):
        bx = start_x + idx * (box_w + gap)
        by = rect.y + 58
        step_box = pygame.Rect(bx, by, box_w, 76)
        draw_rounded_rect(surface, (242, 230, 208), step_box, radius=10, border_width=1, border_color=GOLD_BORDER)

        # Step number badge
        num_s = FONT_TINY.render(f"Step {idx + 1}", True, TEXT_BROWN)
        surface.blit(num_s, num_s.get_rect(center=(step_box.centerx, by + 11)))

        draw_illustrated_icon(surface, label, step_box.centerx, by + 38, scale=0.95)

        display_lbl = "Whip Cream" if label == "Whipped Cream" else label
        lbl_s = FONT_TINY.render(display_lbl, True, TEXT_DARK)
        surface.blit(lbl_s, lbl_s.get_rect(center=(step_box.centerx, by + 64)))

    # Footer Reward Bar
    pygame.draw.line(surface, GOLD_BORDER, (rect.x + 24, rect.bottom - 32), (rect.right - 24, rect.bottom - 32), 1)
    p_txt = FONT_SMALL.render(f"Order Reward: ${rec['price']}  (+15 pts)", True, TEXT_BROWN)
    surface.blit(p_txt, p_txt.get_rect(center=(rect.centerx, rect.bottom - 17)))

# ==============================================================================
# CENTER DRINK ASSEMBLY & SPARKLES
# ==============================================================================

def draw_drink_assembly(surface, cx, cy, cup_state, anim_time):
    cup_type = cup_state["cup"]
    if not cup_type:
        hint = FONT_SMALL.render("Select Hot Cup or Iced Cup below", True, TEXT_DARK)
        surface.blit(hint, hint.get_rect(center=(cx, cy + 28)))
        return

    draw_soft_shadow(surface, (cx - 58, cy + 44, 116, 24), is_ellipse=True, alpha=70)
    pygame.draw.ellipse(surface, WOOD_COUNTER_EDGE, (cx - 54, cy + 42, 108, 20))
    pygame.draw.ellipse(surface, ARCH_FRAME, (cx - 50, cy + 40, 100, 16), 2)

    top_w, bot_w, cup_h = 92, 66, 118
    top_y = cy - 64
    bot_y = top_y + cup_h

    cup_pts = [
        (cx - top_w // 2, top_y),
        (cx + top_w // 2, top_y),
        (cx + bot_w // 2, bot_y),
        (cx - bot_w // 2, bot_y),
    ]

    if cup_state["pour_timer"] > 0 and cup_state["pour_color"]:
        w = int(8 * min(1.0, cup_state["pour_timer"] * 3))
        pygame.draw.line(surface, cup_state["pour_color"], (cx, top_y - 70), (cx, bot_y - 12), max(2, w))

    bg_col = (250, 245, 236) if cup_type == "Hot Cup" else (228, 244, 252)
    pygame.draw.polygon(surface, bg_col, cup_pts)

    fill_ratio = cup_state["visual_fill"]
    base = cup_state["base"]
    liquid = cup_state["liquid"]

    if base and fill_ratio > 0.01:
        c_base = get_ingredient_color(base)
        cur_top_y = bot_y - int((cup_h - 10) * fill_ratio)
        cur_top_w = int(bot_w + (top_w - bot_w) * ((bot_y - cur_top_y) / cup_h))

        if not liquid:
            liq_pts = [
                (cx - cur_top_w // 2 + 3, cur_top_y),
                (cx + cur_top_w // 2 - 3, cur_top_y),
                (cx + bot_w // 2 - 3, bot_y - 3),
                (cx - bot_w // 2 + 3, bot_y - 3),
            ]
            pygame.draw.polygon(surface, c_base, liq_pts)
        else:
            c_liq = get_ingredient_color(liquid)
            mix_col = blend_colors(c_base, c_liq, 0.35 if liquid == "Water" else 0.65)
            liq_pts = [
                (cx - cur_top_w // 2 + 3, cur_top_y),
                (cx + cur_top_w // 2 - 3, cur_top_y),
                (cx + bot_w // 2 - 3, bot_y - 3),
                (cx - bot_w // 2 + 3, bot_y - 3),
            ]
            pygame.draw.polygon(surface, mix_col, liq_pts)

            mid_y = (cur_top_y + bot_y) // 2 + 6
            mid_w = int(bot_w + (top_w - bot_w) * ((bot_y - mid_y) / cup_h))
            bot_pts = [
                (cx - mid_w // 2 + 3, mid_y),
                (cx + mid_w // 2 - 3, mid_y),
                (cx + bot_w // 2 - 3, bot_y - 3),
                (cx - bot_w // 2 + 3, bot_y - 3),
            ]
            pygame.draw.polygon(surface, blend_colors(c_base, mix_col, 0.38), bot_pts)

    if cup_type == "Iced Cup":
        ice_surf = pygame.Surface((110, 120), pygame.SRCALPHA)
        for ix, iy in [(32, 32), (58, 38), (38, 62), (62, 66)]:
            pygame.draw.rect(ice_surf, (238, 250, 255, 175), (ix, iy, 20, 20), border_radius=5)
            pygame.draw.rect(ice_surf, (255, 255, 255, 230), (ix, iy, 20, 20), width=2, border_radius=5)
        surface.blit(ice_surf, (cx - 55, top_y + 4))

    if cup_type == "Hot Cup":
        sleeve_pts = [(cx - 42, top_y + 34), (cx + 42, top_y + 34), (cx + 37, top_y + 78), (cx - 37, top_y + 78)]
        pygame.draw.polygon(surface, (196, 148, 98), sleeve_pts)
        pygame.draw.polygon(surface, WOOD_DARK, sleeve_pts, 2)

    glare = pygame.Surface((14, cup_h - 14), pygame.SRCALPHA)
    glare.fill((255, 255, 255, 65))
    surface.blit(glare, (cx - 28, top_y + 7))

    pygame.draw.polygon(surface, TEXT_DARK, cup_pts, 3)
    rim = pygame.Rect(cx - top_w // 2 - 3, top_y - 5, top_w + 6, 10)
    draw_rounded_rect(surface, (248, 244, 236), rim, radius=5, border_width=2, border_color=TEXT_DARK)

    topping = cup_state["topping"]
    if topping == "Whipped Cream":
        pygame.draw.ellipse(surface, COL_WHIPPED, (cx - 42, top_y - 16, 84, 22))
        pygame.draw.ellipse(surface, (206, 198, 186), (cx - 42, top_y - 16, 84, 22), 2)
        pygame.draw.ellipse(surface, COL_WHIPPED, (cx - 30, top_y - 28, 60, 19))
        pygame.draw.ellipse(surface, (206, 198, 186), (cx - 30, top_y - 28, 60, 19), 2)
        pygame.draw.ellipse(surface, COL_WHIPPED, (cx - 15, top_y - 38, 30, 15))
        pygame.draw.lines(surface, COL_CARAMEL, False, [(cx - 22, top_y - 14), (cx, top_y - 24), (cx + 22, top_y - 14)], 3)
    elif topping == "Caramel":
        pts = [(cx - 32, top_y - 3), (cx - 16, top_y - 11), (cx, top_y - 2), (cx + 16, top_y - 11), (cx + 32, top_y - 3)]
        pygame.draw.lines(surface, COL_CARAMEL, False, pts, 5)
        pygame.draw.lines(surface, (255, 202, 98), False, [(p[0], p[1] - 1) for p in pts], 2)

    if base:
        steam = pygame.Surface((110, 75), pygame.SRCALPHA)
        for i in range(-1, 2):
            sx = 55 + i * 20 + int(math.sin(anim_time * 3.2 + i) * 6)
            sy = 64 - int(((anim_time * 24 + i * 16) % 48))
            alpha = max(0, int(170 * (sy / 64)))
            pygame.draw.circle(steam, (255, 255, 255, alpha), (sx, sy), 5)
        surface.blit(steam, (cx - 55, top_y - 72))

def spawn_sparkles(particles, cx, cy, count=18):
    colors = [(255, 232, 118), (255, 255, 255), (255, 206, 110)]
    for _ in range(count):
        ang = random.uniform(0, 2 * math.pi)
        spd = random.uniform(28, 105)
        particles.append({
            "x": cx + random.uniform(-35, 35),
            "y": cy + random.uniform(-35, 25),
            "vx": math.cos(ang) * spd,
            "vy": math.sin(ang) * spd - 18,
            "size": random.uniform(4, 9),
            "life": random.uniform(0.6, 1.1),
            "max_life": 1.1,
            "color": random.choice(colors),
        })

def draw_sparkles(surface, particles):
    for p in particles:
        ratio = max(0.0, p["life"] / p["max_life"])
        s = int(p["size"] * ratio)
        if s < 2:
            continue
        x, y = int(p["x"]), int(p["y"])
        pts = [(x, y - s), (x + s // 3, y - s // 3), (x + s, y), (x + s // 3, y + s // 3),
               (x, y + s), (x - s // 3, y + s // 3), (x - s, y), (x - s // 3, y - s // 3)]
        pygame.draw.polygon(surface, p["color"], pts)

# ==============================================================================
# BOTTOM ORNATE ROUND INGREDIENT BUTTONS & ACTION PILLS
# ==============================================================================

def draw_round_ingredient_button(surface, cx, cy, radius, label, mouse_pos, enabled=True, selected=False):
    dist = math.hypot(mouse_pos[0] - cx, mouse_pos[1] - cy)
    is_hovered = (dist <= radius) and enabled

    pygame.draw.circle(surface, (46, 26, 14), (cx, cy + 5), radius)

    ring_col = (255, 224, 102) if selected else ((236, 194, 118) if is_hovered else GOLD_BORDER)
    pygame.draw.circle(surface, ring_col, (cx, cy), radius)

    disc_col = PARCHMENT_BG if enabled else (188, 178, 166)
    if is_hovered:
        disc_col = (255, 252, 244)
    pygame.draw.circle(surface, disc_col, (cx, cy), radius - 5)
    pygame.draw.circle(surface, WOOD_DARK, (cx, cy), radius, 2)

    draw_illustrated_icon(surface, label, cx, cy - 3, scale=1.12)

    display_lbl = "Whip Cream" if label == "Whipped Cream" else label
    lbl_surf = FONT_TINY.render(display_lbl, True, TEXT_WHITE if enabled else (200, 195, 188))
    lbl_shadow = FONT_TINY.render(display_lbl, True, WOOD_DARK)
    surface.blit(lbl_shadow, lbl_shadow.get_rect(center=(cx + 1, cy + radius + 14)))
    surface.blit(lbl_surf, lbl_surf.get_rect(center=(cx, cy + radius + 13)))
    return is_hovered

def draw_pill_button(surface, rect, text, base_col, hover_col, mouse_pos, enabled=True):
    is_hovered = rect.collidepoint(mouse_pos) and enabled
    col = (hover_col if is_hovered else base_col) if enabled else (132, 124, 114)

    sh = rect.copy()
    sh.y += 4
    draw_rounded_rect(surface, (46, 26, 14), sh, radius=rect.height // 2)

    draw_rounded_rect(surface, col, rect, radius=rect.height // 2, border_width=3, border_color=GOLD_BORDER)
    inner = rect.inflate(-8, -8)
    pygame.draw.rect(surface, (255, 255, 255), inner, width=1, border_radius=inner.height // 2)

    txt = FONT_HEADER.render(text, True, TEXT_WHITE if enabled else (215, 210, 204))
    surface.blit(txt, txt.get_rect(center=rect.center))
    return is_hovered

# ==============================================================================
# GAME LOGIC & MAIN LOOP
# ==============================================================================

def create_empty_cup():
    return {
        "cup": None,
        "base": None,
        "liquid": None,
        "topping": "None",
        "target_fill": 0.0,
        "visual_fill": 0.0,
        "pour_timer": 0.0,
        "pour_color": None,
    }

def evaluate_drink(cup_state, recipe):
    if not cup_state["cup"]:
        return False, "Select a cup first!"
    if not cup_state["base"] or not cup_state["liquid"]:
        return False, "Incomplete drink! -5 pts"

    is_match = (
        cup_state["cup"] == recipe["cup"]
        and cup_state["base"] == recipe["base"]
        and cup_state["liquid"] == recipe["liquid"]
        and cup_state["topping"] == recipe["topping"]
    )
    if is_match:
        return True, f"Delicious {recipe['name']}! +15 pts"
    else:
        return False, "Wrong recipe! -5 pts"

def main():
    game_state = "MENU"  # MENU, PLAYING, GAME_OVER
    score = 0
    money = 0
    drinks_served = 0
    streak = 0
    time_remaining = 90.0
    anim_time = 0.0

    current_customer = generate_customer()
    current_cup = create_empty_cup()
    floating_popups = []
    sparkles = []

    CUSTOMER_X = 330
    DRINK_CENTER = (610, 462)

    # Bottom Circular Ingredient Buttons (evenly spaced along bottom bar)
    ingredient_items = [
        ("Hot Cup", "cup"),
        ("Iced Cup", "cup"),
        ("Espresso", "base"),
        ("Matcha", "base"),
        ("Chocolate", "base"),
        ("Water", "liquid"),
        ("Milk", "liquid"),
        ("Oat Milk", "liquid"),
        ("Whipped Cream", "topping"),
        ("Caramel", "topping"),
    ]
    round_buttons = []
    start_x = 225
    spacing_x = 70
    btn_y = 646
    btn_r = 27
    for idx, (label, category) in enumerate(ingredient_items):
        round_buttons.append({
            "label": label,
            "category": category,
            "cx": start_x + idx * spacing_x,
            "cy": btn_y,
            "r": btn_r,
        })

    serve_btn = pygame.Rect(928, 622, 130, 52)
    trash_btn = pygame.Rect(1068, 622, 130, 52)

    menu_start_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 470, 280, 60)
    gameover_restart_btn = pygame.Rect(SCREEN_WIDTH // 2 - 140, 495, 280, 60)

    def reset_shift():
        nonlocal score, money, drinks_served, streak, time_remaining, current_customer, current_cup, floating_popups, sparkles
        score = 0
        money = 0
        drinks_served = 0
        streak = 0
        time_remaining = 90.0
        current_customer = generate_customer()
        current_cup = create_empty_cup()
        floating_popups = []
        sparkles = []

    def add_popup(text, x, y, color):
        floating_popups.append([text, x, y, color, 1.5])

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        anim_time += dt
        mouse_pos = pygame.mouse.get_pos()

        # ----------------------------------------------------------------------
        # EVENT HANDLING
        # ----------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "MENU":
                    if menu_start_btn.collidepoint(mouse_pos):
                        reset_shift()
                        game_state = "PLAYING"

                elif game_state == "GAME_OVER":
                    if gameover_restart_btn.collidepoint(mouse_pos):
                        reset_shift()
                        game_state = "PLAYING"

                elif game_state == "PLAYING":
                    for btn in round_buttons:
                        if math.hypot(mouse_pos[0] - btn["cx"], mouse_pos[1] - btn["cy"]) <= btn["r"]:
                            cat = btn["category"]
                            lbl = btn["label"]

                            if cat == "cup" and not current_cup["cup"]:
                                current_cup["cup"] = lbl
                                spawn_sparkles(sparkles, DRINK_CENTER[0], DRINK_CENTER[1], 10)
                                add_popup(f"{lbl} Ready", DRINK_CENTER[0], DRINK_CENTER[1] - 85, TEXT_WHITE)

                            elif cat == "base":
                                if not current_cup["cup"]:
                                    add_popup("Pick Hot or Iced Cup first!", DRINK_CENTER[0], 575, BTN_TRASH_HOVER)
                                elif not current_cup["base"]:
                                    current_cup["base"] = lbl
                                    current_cup["target_fill"] = 0.36
                                    current_cup["pour_timer"] = 0.45
                                    current_cup["pour_color"] = get_ingredient_color(lbl)
                                    spawn_sparkles(sparkles, DRINK_CENTER[0], DRINK_CENTER[1] - 20, 12)
                                    add_popup(f"+ {lbl}", DRINK_CENTER[0], DRINK_CENTER[1] - 85, BRASS_LIGHT)

                            elif cat == "liquid":
                                if not current_cup["base"]:
                                    add_popup("Add Base first!", DRINK_CENTER[0], 575, BTN_TRASH_HOVER)
                                elif not current_cup["liquid"]:
                                    current_cup["liquid"] = lbl
                                    current_cup["target_fill"] = 0.92
                                    current_cup["pour_timer"] = 0.55
                                    current_cup["pour_color"] = get_ingredient_color(lbl)
                                    spawn_sparkles(sparkles, DRINK_CENTER[0], DRINK_CENTER[1] - 20, 14)
                                    add_popup(f"+ {lbl}", DRINK_CENTER[0], DRINK_CENTER[1] - 85, TEXT_WHITE)

                            elif cat == "topping":
                                if not current_cup["liquid"]:
                                    add_popup("Add Liquid first!", DRINK_CENTER[0], 575, BTN_TRASH_HOVER)
                                elif current_cup["topping"] == "None":
                                    current_cup["topping"] = lbl
                                    spawn_sparkles(sparkles, DRINK_CENTER[0], DRINK_CENTER[1] - 60, 16)
                                    add_popup(f"+ {lbl}", DRINK_CENTER[0], DRINK_CENTER[1] - 95, BRASS_LIGHT)

                    if serve_btn.collidepoint(mouse_pos) and current_cup["cup"]:
                        ok, msg = evaluate_drink(current_cup, current_customer["recipe"])
                        if ok:
                            streak += 1
                            bonus = min(5, streak - 1)
                            score += 15 + bonus * 2
                            earned = current_customer["recipe"]["price"] + bonus
                            money += earned
                            drinks_served += 1
                            spawn_sparkles(sparkles, DRINK_CENTER[0], DRINK_CENTER[1] - 30, 26)
                            add_popup(f"{msg} (+${earned})", 580, 285, (130, 245, 145))
                        else:
                            streak = 0
                            score = max(0, score - 5)
                            add_popup(msg, 580, 285, (255, 130, 120))

                        current_customer = generate_customer()
                        current_cup = create_empty_cup()

                    if trash_btn.collidepoint(mouse_pos) and current_cup["cup"]:
                        current_cup = create_empty_cup()
                        add_popup("Discarded", DRINK_CENTER[0], DRINK_CENTER[1] - 60, (255, 140, 130))

        # ----------------------------------------------------------------------
        # UPDATES
        # ----------------------------------------------------------------------
        if game_state == "PLAYING":
            time_remaining -= dt
            if time_remaining <= 0:
                time_remaining = 0
                game_state = "GAME_OVER"

            if current_cup["pour_timer"] > 0:
                current_cup["pour_timer"] = max(0.0, current_cup["pour_timer"] - dt)

            if current_cup["visual_fill"] < current_cup["target_fill"]:
                current_cup["visual_fill"] = min(
                    current_cup["target_fill"],
                    current_cup["visual_fill"] + dt * 1.9
                )

            for p in floating_popups[:]:
                p[2] -= 34 * dt
                p[4] -= dt
                if p[4] <= 0:
                    floating_popups.remove(p)

        for sp in sparkles[:]:
            sp["x"] += sp["vx"] * dt
            sp["y"] += sp["vy"] * dt
            sp["vy"] += 55 * dt
            sp["life"] -= dt
            if sp["life"] <= 0:
                sparkles.remove(sp)

        # ----------------------------------------------------------------------
        # RENDERING (CLEAN 3-ZONE LAYERED COMPOSITION)
        # ----------------------------------------------------------------------
        draw_cafe_back_wall(screen, anim_time)

        if game_state == "PLAYING":
            draw_customer(screen, current_customer, CUSTOMER_X, 316, anim_time)

        draw_cafe_foreground_counter(screen)

        # Top Ornate Parchment HUD Bar
        pygame.draw.rect(screen, HUD_BAR_BG, (0, 0, SCREEN_WIDTH, 56))
        pygame.draw.line(screen, GOLD_BORDER, (0, 56), (SCREEN_WIDTH, 56), 4)

        hud_items = [
            ("Score:", f"{score}", 260),
            ("Money:", f"${money}", 435),
            ("Drinks Served:", f"{drinks_served}", 635),
            ("Streak:", f"{streak}x", 815),
            ("Time:", f"{int(math.ceil(time_remaining))}s", 965),
        ]
        for lbl, val, hx in hud_items:
            l_s = FONT_SMALL.render(lbl, True, TEXT_DARK)
            screen.blit(l_s, l_s.get_rect(center=(hx, 15)))
            pill = pygame.Rect(hx - 48, 26, 96, 24)
            draw_rounded_rect(screen, HUD_PILL_BG, pill, radius=10, border_width=2, border_color=GOLD_BORDER)
            v_col = (255, 130, 120) if (lbl == "Time:" and time_remaining <= 15) else TEXT_WHITE
            v_s = FONT_SMALL.render(val, True, v_col)
            screen.blit(v_s, v_s.get_rect(center=pill.center))

        if game_state == "MENU":
            card = pygame.Rect(SCREEN_WIDTH // 2 - 330, 135, 660, 310)
            draw_rounded_rect(screen, PARCHMENT_BG, card, radius=22, border_width=4, border_color=GOLD_BORDER)
            pygame.draw.rect(screen, PARCHMENT_DARK, card.inflate(-14, -14), width=2, border_radius=16)

            t1 = FONT_TITLE.render("Barista Cafe", True, TEXT_DARK)
            t2 = FONT_MED.render("Cozy Illustrated Coffee Shop Simulation", True, TEXT_BROWN)
            screen.blit(t1, t1.get_rect(center=(SCREEN_WIDTH // 2, 195)))
            screen.blit(t2, t2.get_rect(center=(SCREEN_WIDTH // 2, 245)))

            preview_cup = {
                "cup": "Iced Cup", "base": "Matcha", "liquid": "Oat Milk",
                "topping": "Whipped Cream", "visual_fill": 0.92,
                "pour_timer": 0.0, "pour_color": None
            }
            draw_drink_assembly(screen, SCREEN_WIDTH // 2, 365, preview_cup, anim_time)
            draw_pill_button(screen, menu_start_btn, "Open Cafe (90s)", BTN_SERVE_READY, BTN_SERVE_HOVER, mouse_pos, True)

        elif game_state == "PLAYING":
            # Customer Name & Age Badge on Counter in front of Character
            draw_customer_name_badge(screen, current_customer, CUSTOMER_X, 392)

            # Single Clean Order Card in Center-Top Zone (Zero overlap with character or menu)
            order_card = pygame.Rect(420, 92, 300, 184)
            draw_single_order_card(screen, order_card, current_customer)

            # Central Drink Assembly on Wooden Tray
            draw_drink_assembly(screen, DRINK_CENTER[0], DRINK_CENTER[1], current_cup, anim_time)

            # Bottom Round Ingredient Buttons
            for btn in round_buttons:
                cat = btn["category"]
                lbl = btn["label"]
                if cat == "cup":
                    enabled = current_cup["cup"] is None
                    selected = current_cup["cup"] == lbl
                elif cat == "base":
                    enabled = (current_cup["cup"] is not None) and (current_cup["base"] is None)
                    selected = current_cup["base"] == lbl
                elif cat == "liquid":
                    enabled = (current_cup["base"] is not None) and (current_cup["liquid"] is None)
                    selected = current_cup["liquid"] == lbl
                else:
                    enabled = (current_cup["liquid"] is not None) and (current_cup["topping"] == "None")
                    selected = current_cup["topping"] == lbl

                draw_round_ingredient_button(screen, btn["cx"], btn["cy"], btn["r"], lbl, mouse_pos, enabled, selected)

            # Serve & Trash Pill Buttons
            can_serve = current_cup["liquid"] is not None
            draw_pill_button(screen, serve_btn, "Serve", BTN_SERVE_READY if can_serve else BTN_SERVE, BTN_SERVE_HOVER, mouse_pos, can_serve)
            draw_pill_button(screen, trash_btn, "Trash", BTN_TRASH, BTN_TRASH_HOVER, mouse_pos, current_cup["cup"] is not None)

            draw_sparkles(screen, sparkles)
            for text, fx, fy, col, _ in floating_popups:
                sh = FONT_MED.render(text, True, WOOD_DARK)
                fg = FONT_MED.render(text, True, col)
                screen.blit(sh, sh.get_rect(center=(fx + 2, fy + 2)))
                screen.blit(fg, fg.get_rect(center=(fx, fy)))

        elif game_state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((28, 16, 10, 155))
            screen.blit(overlay, (0, 0))

            panel = pygame.Rect(SCREEN_WIDTH // 2 - 270, 155, 540, 420)
            draw_rounded_rect(screen, PARCHMENT_BG, panel, radius=22, border_width=4, border_color=GOLD_BORDER)
            pygame.draw.rect(screen, PARCHMENT_DARK, panel.inflate(-14, -14), width=2, border_radius=16)

            over_t = FONT_TITLE.render("Cafe Closed!", True, TEXT_DARK)
            screen.blit(over_t, over_t.get_rect(center=(SCREEN_WIDTH // 2, 215)))

            r1 = FONT_HEADER.render(f"Final Score: {score} pts", True, TEXT_DARK)
            r2 = FONT_HEADER.render(f"Drinks Served: {drinks_served}", True, TEXT_DARK)
            r3 = FONT_HEADER.render(f"Total Revenue & Tips: ${money}", True, (56, 138, 72))

            screen.blit(r1, r1.get_rect(center=(SCREEN_WIDTH // 2, 290)))
            screen.blit(r2, r2.get_rect(center=(SCREEN_WIDTH // 2, 342)))
            screen.blit(r3, r3.get_rect(center=(SCREEN_WIDTH // 2, 394)))

            draw_pill_button(screen, gameover_restart_btn, "Play Again", BTN_SERVE_READY, BTN_SERVE_HOVER, mouse_pos, True)

        pygame.draw.rect(screen, WOOD_DARK, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 6)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
