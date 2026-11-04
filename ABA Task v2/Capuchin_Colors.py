#  ______     ______     ______   __  __     ______     __  __     __     __   __        ______     ______     __         ______     ______     ______
# /\  ___\   /\  __ \   /\  == \ /\ \/\ \   /\  ___\   /\ \_\ \   /\ \   /\ "-.\ \      /\  ___\   /\  __ \   /\ \       /\  __ \   /\  == \   /\  ___\
# \ \ \____  \ \  __ \  \ \  _-/ \ \ \_\ \  \ \ \____  \ \  __ \  \ \ \  \ \ \-.  \     \ \ \____  \ \ \/\ \  \ \ \____  \ \ \/\ \  \ \  __<   \ \___  \
#  \ \_____\  \ \_\ \_\  \ \_\    \ \_____\  \ \_____\  \ \_\ \_\  \ \_\  \ \_\\"\_\     \ \_____\  \ \_____\  \ \_____\  \ \_____\  \ \_\ \_\  \/\_____\
#   \/_____/   \/_/\/_/   \/_/     \/_____/   \/_____/   \/_/\/_/   \/_/   \/_/ \/_/      \/_____/   \/_____/   \/_____/   \/_____/   \/_/ /_/   \/_____/
# CODE BY MATTHEW H. BABB ALL RIGHTS RESERVED !!!!!!!!!!!!
# Do NOT use this code without the permission of original author !!!!!!!!!!!!

# Capuchin-safe random color pairs
# ---------------------------------------------------------------------------------------------------------------------
# The macaque (MATLAB) version picked 2 random RGB colors and re-rolled them if they were "too close" (distance < 0.8).
# Rhesus are all trichromats. Capuchins are NOT: every male and some females are red-green colorblind (dichromats),
# and we do not know which of our monkeys are which. So this file only keeps a color pair if it passes ALL of these:
#
#   1. BEN'S RULE (same as the published macaque task): the 3D distance between the two colors in RGB space must be
#      at least 0.8, using RGB values from 0 - 1:
#          sqrt( (R1 - R2)^2 + (G1 - G2)^2 + (B1 - B2)^2 ) >= 0.8      (that is 204 on the 0 - 255 scale)
#   2. The two colors look different to a PROTAN dichromat  (red-green colorblind, missing the long "red" cone)
#   3. The two colors look different to a DEUTAN dichromat  (red-green colorblind, missing the medium "green" cone)
#   4. Both colors are bright enough to stand out from the dark grey background (for all 3 types of vision)
#
# Capuchin dichromats have one of three red/green cone types (535, 550, or 562 nm). The protan and deutan
# simulations cover the two ends of that range, so a pair that passes both should be safe for every monkey.
#
# Checks 2 - 4 are EXTRA checks for capuchins, on top of Ben's rule.
# For checks 2 and 3, "look different" is measured with Delta E (the standard color-difference number in CIELAB color space):
#   Delta E ~2  = barely noticeable to people
#   Delta E ~10 = clearly different
#   Delta E 30+ = obviously different colors
# Colorblind vision is simulated with the Machado, Oliveira & Fernandes (2009) matrices (full severity).
#
# NOTE: No pygame in here on purpose, so this file can be tested on any computer.

import random
import math

"""SETTINGS -----------------------------------------------------------------------------------------------------------"""
# These are for Matt / Ben, NOT for research assistants (that is why they are not in parameters.txt)
MIN_RGB_DISTANCE = 0.8          # Ben's rule: minimum RGB distance between A and B (RGB scaled 0 - 1). Lower this if it ever struggles
MIN_DELTA_E_COLORBLIND = 30     # Minimum difference between A and B for BOTH protan and deutan dichromats
MIN_LIGHTNESS = 35              # Minimum brightness (L*, 0 = black, 100 = white) of each color. Dark grey bg is ~L* 16

"""COLORBLIND SIMULATION MATRICES ------------------------------------------------------------------------------------"""
# These work on LINEAR rgb values (0 - 1), not on the normal 0 - 255 screen values
protan_matrix = [[0.152286, 1.052583, -0.204868],
                 [0.114503, 0.786281, 0.099216],
                 [-0.003882, -0.048116, 1.051998]]

deutan_matrix = [[0.367322, 0.860646, -0.227968],
                 [0.280085, 0.672501, 0.047413],
                 [-0.011820, 0.042940, 0.968881]]

"""COLOR MATH FUNCTIONS ----------------------------------------------------------------------------------------------"""

def rgb_to_linear(rgb):
    """Screen RGB (0 - 255) --> linear rgb (0 - 1). Screens are not linear, so this undoes the screen's gamma."""
    linear = []
    for c in rgb:
        c = c / 255.0
        if c <= 0.04045:
            linear.append(c / 12.92)
        else:
            linear.append(((c + 0.055) / 1.055) ** 2.4)
    return linear

def simulate(linear, matrix):
    """Apply a colorblind matrix to a linear rgb color. Returns what a dichromat would see (linear rgb)."""
    new = []
    for row in matrix:
        value = row[0] * linear[0] + row[1] * linear[1] + row[2] * linear[2]
        new.append(min(max(value, 0.0), 1.0))           # Keep it between 0 and 1
    return new

def linear_to_lab(linear):
    """Linear rgb (0 - 1) --> CIELAB (L*, a*, b*). L* is brightness, a* is red-green, b* is blue-yellow."""
    r, g, b = linear
    X = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    Y = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 1.00000
    Z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        if t > 0.008856:
            return t ** (1.0 / 3.0)
        else:
            return 7.787 * t + 16.0 / 116.0

    fx, fy, fz = f(X), f(Y), f(Z)
    L = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return (L, a, b)

def delta_e(lab1, lab2):
    """Distance between two CIELAB colors (Delta E 1976)"""
    return math.sqrt((lab1[0] - lab2[0]) ** 2 + (lab1[1] - lab2[1]) ** 2 + (lab1[2] - lab2[2]) ** 2)

def rgb_distance(rgb1, rgb2):
    """Ben's distance: straight-line 3D distance between 2 colors in RGB space, with RGB scaled 0 - 1 (max = 1.73)"""
    return math.sqrt(((rgb1[0] - rgb2[0]) / 255.0) ** 2 + ((rgb1[1] - rgb2[1]) / 255.0) ** 2 + ((rgb1[2] - rgb2[2]) / 255.0) ** 2)

def color_views(rgb):
    """Returns the CIELAB color as seen by a trichromat, a protan, and a deutan"""
    linear = rgb_to_linear(rgb)
    normal = linear_to_lab(linear)
    protan = linear_to_lab(simulate(linear, protan_matrix))
    deutan = linear_to_lab(simulate(linear, deutan_matrix))
    return normal, protan, deutan

"""MAIN FUNCTION: USE THIS ONE IN YOUR TASKS -------------------------------------------------------------------------"""

def capuchin_color_pair():
    """Generate 2 random colors (A and B) that pass Ben's RGB distance rule AND are easy to tell apart for
       dichromat (red-green colorblind) capuchins.
       Returns: color_A (R, G, B), color_B (R, G, B), and the smallest Delta E of the 3 types of vision"""
    while True:
        color_A = (random.randint(0, 254), random.randint(0, 254), random.randint(0, 254))   # 254 max: pure white (255, 255, 255)
        color_B = (random.randint(0, 254), random.randint(0, 254), random.randint(0, 254))   # is invisible in Matt's Toolbox

        # Check 1: Ben's rule. 3D distance in RGB space (RGB scaled 0 - 1) must be at least 0.8
        rgb_dist = rgb_distance(color_A, color_B)
        if rgb_dist < MIN_RGB_DISTANCE:
            continue                                                    # Re-roll the colors

        A_normal, A_protan, A_deutan = color_views(color_A)
        B_normal, B_protan, B_deutan = color_views(color_B)

        # Check 4: Both colors bright enough against the dark grey background (in all 3 views)
        too_dark = False
        for lab in [A_normal, A_protan, A_deutan, B_normal, B_protan, B_deutan]:
            if lab[0] < MIN_LIGHTNESS:
                too_dark = True
        if too_dark:
            continue                                                    # Re-roll the colors

        # Checks 2 - 3: A and B still look different to red-green colorblind (protan AND deutan) monkeys
        dE_normal = delta_e(A_normal, B_normal)
        dE_protan = delta_e(A_protan, B_protan)
        dE_deutan = delta_e(A_deutan, B_deutan)

        if dE_protan >= MIN_DELTA_E_COLORBLIND and dE_deutan >= MIN_DELTA_E_COLORBLIND:
            min_dE = round(min(dE_normal, dE_protan, dE_deutan), 1)     # Smallest Delta E of the 3 views (saved in the data)
            return color_A, color_B, min_dE
