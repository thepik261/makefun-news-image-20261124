#!/usr/bin/env python3
"""News-image entry for make.fun bounty news-image-20261124.

Draws a 1024x1024 newspaper front page summing up Tuesday 24 November 2026:
the Gulf tanker standoff, the Indonesia factory fire, the Trump hush-money
appeal, the Women's World Cup hosts, Denmark's "ghetto law" ruling, and the
World Chess Championship opener. Python standard library only (zlib, struct,
os), no network, deterministic: two runs write identical bytes.

Run:  python3 main.py        (writes /output/entry.png)
      MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W, H = 1024, 1024

# Palette
PAPER = (246, 241, 231)
INK = (26, 26, 26)
NAVY = (22, 50, 79)
NAVY_LT = (31, 78, 121)
RED = (176, 46, 46)
GOLD = (200, 162, 75)
SKY = (217, 230, 242)
SEA = (31, 78, 121)
GREY = (110, 110, 105)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 5x7 bitmap font, uppercase + digits + punctuation. Each glyph is 7 rows
# of 5 characters; '#' is a set pixel.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}

CHAR_W = 6  # 5 pixels + 1 pixel gap, before scaling


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


def draw_text(px, x, y, text, scale, color):
    """Draw text at (x, y) top-left; returns width in pixels."""
    text = text.upper()  # the bitmap font carries capitals only
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    for dy in range(scale):
                        base = ((y + row * scale + dy) * W + cx + col * scale) * 3
                        for dx in range(scale):
                            o = base + dx * 3
                            px[o], px[o + 1], px[o + 2] = color
        cx += CHAR_W * scale
    return cx - x - scale


def draw_text_centered(px, cx, y, text, scale, color):
    draw_text(px, cx - text_width(text, scale) // 2, y, text, scale, color)


def fill_rect(px, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            o = base + (xx - x0) * 3
            px[o], px[o + 1], px[o + 2] = color


def rect_outline(px, x, y, w, h, color, t=2):
    fill_rect(px, x, y, w, t, color)
    fill_rect(px, x, y + h - t, w, t, color)
    fill_rect(px, x, y, t, h, color)
    fill_rect(px, x + w - t, y, t, h, color)


def hline(px, x, y, w, color, t=1):
    fill_rect(px, x, y, w, t, color)


def fill_circle(px, cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                if 0 <= xx < W and 0 <= yy < H:
                    o = (yy * W + xx) * 3
                    px[o], px[o + 1], px[o + 2] = color


def wrap(text, max_width_px, scale):
    """Greedy word wrap; returns list of lines fitting max_width_px."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width_px or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_sea_scene(px, x, y, w, h):
    """Simple tanker-at-sea illustration inside box (x, y, w, h).
    Every element stays inside the box (ship parts rise at most to the top)."""
    fill_rect(px, x, y, w, h, SKY)
    fill_circle(px, x + w - 70, y + 24, 16, GOLD)          # sun
    fill_rect(px, x, y + h - 30, w, 30, SEA)               # sea
    # waves
    for wx in range(x + 8, x + w - 8, 46):
        fill_rect(px, wx, y + h - 22, 30, 3, WHITE)
    for wx in range(x + 30, x + w - 8, 46):
        fill_rect(px, wx, y + h - 10, 30, 3, (160, 200, 225))
    # tanker hull (low silhouette: bridge and containers stay in-box)
    hx, hy = x + 60, y + h - 50
    fill_rect(px, hx, hy, 300, 20, (30, 30, 34))
    fill_rect(px, hx + 300, hy + 6, 34, 14, (30, 30, 34))  # bow
    fill_rect(px, hx + 18, hy - 12, 56, 12, WHITE)          # bridge
    for cx in range(hx + 110, hx + 280, 36):                # containers
        fill_rect(px, cx, hy - 14, 28, 14, GOLD)
    # distant second ship
    fill_rect(px, x + w - 190, y + h - 40, 90, 10, (60, 60, 66))


def draw_chessboard(px, x, y, sq):
    """8x8 board, square size sq, with a few piece dots."""
    for r in range(8):
        for c in range(8):
            col = WHITE if (r + c) % 2 == 0 else INK
            fill_rect(px, x + c * sq, y + r * sq, sq, sq, col)
    rect_outline(px, x, y, 8 * sq, 8 * sq, INK, 3)
    # a few pieces: white king, black queen, pawns
    fill_circle(px, x + 4 * sq + sq // 2, y + 7 * sq + sq // 2, sq // 3, RED)
    fill_circle(px, x + 3 * sq + sq // 2, y + 0 * sq + sq // 2, sq // 3, RED)
    fill_circle(px, x + 1 * sq + sq // 2, y + 6 * sq + sq // 2, sq // 4, GOLD)
    fill_circle(px, x + 6 * sq + sq // 2, y + 1 * sq + sq // 2, sq // 4, GOLD)


def draw_panel(px, x, y, w, h, accent, kicker, headline, body):
    fill_rect(px, x, y, w, h, WHITE)
    rect_outline(px, x, y, w, h, INK, 2)
    fill_rect(px, x, y, 6, h, accent)
    ix = x + 20
    iw = w - 40
    draw_text(px, ix, y + 14, kicker, 2, RED)
    lines = wrap(headline, iw, 4)
    ly = y + 36
    for ln in lines[:2]:
        draw_text(px, ix, ly, ln, 4, INK)
        ly += 34
    by = y + h - 44
    for ln in wrap(body, iw, 2)[:2]:
        draw_text(px, ix, by, ln, 2, (70, 70, 70))
        by += 18


def build_image():
    px = bytearray(PAPER * (W * H))

    # ---- Masthead ----
    fill_rect(px, 0, 0, W, 148, NAVY)
    draw_text_centered(px, W // 2, 18, "THE WORLD IN ONE DAY", 2, GOLD)
    draw_text_centered(px, W // 2, 48, "TUESDAY 24 NOVEMBER 2026", 6, WHITE)
    draw_text_centered(px, W // 2, 112, "SIX STORIES THAT DEFINED THE DAY", 2, WHITE)
    fill_rect(px, 0, 148, W, 4, RED)

    # ---- Sub-masthead ----
    draw_text_centered(px, W // 2, 164, "FRONT PAGE  -  ONE DAY, ONE PICTURE", 2, GREY)

    # ---- Lead story: Gulf tanker standoff ----
    lx, ly, lw, lh = 24, 192, 976, 252
    fill_rect(px, lx, ly, lw, lh, WHITE)
    rect_outline(px, lx, ly, lw, lh, INK, 2)
    draw_text(px, lx + 20, ly + 14, "LEAD STORY  -  THE GULF", 2, RED)
    draw_text(px, lx + 20, ly + 38, "IRAN READIES 14 TANKERS", 5, INK)
    draw_text(px, lx + 20, ly + 76, "TO TEST U.S. BLOCKADE", 5, INK)
    draw_text(px, lx + 20, ly + 118, "Trump vows to sink any ship that runs the blockade", 3, (70, 70, 70))
    draw_text(px, lx + 20, ly + 142, "as Tehran's convoy gathers at Kharg Island.", 3, (70, 70, 70))
    draw_sea_scene(px, lx + 20, ly + 170, lw - 40, 74)

    # ---- Grid: four stories ----
    gx, gy, gw, gh, gap = 24, 460, 480, 156, 16
    draw_panel(px, gx, gy, gw, gh, RED, "INDONESIA",
               "FACTORY FIRE TOLL RISES TO 26",
               "34 still missing after the blaze at a candy plant near Jakarta.")
    draw_panel(px, gx + gw + gap, gy, gw, gh, NAVY_LT, "UNITED STATES",
               "TRUMP GETS NEW PATH TO ERASE CONVICTION",
               "Appeals court moves the hush-money case to federal court.")
    draw_panel(px, gx, gy + gh + gap, gw, gh, GOLD, "FOOTBALL",
               "WOMEN'S WORLD CUP HOSTS NAMED",
               "2031: USA, Mexico, Costa Rica, Jamaica. 2035: United Kingdom.")
    draw_panel(px, gx + gw + gap, gy + gh + gap, gw, gh, (90, 60, 120), "DENMARK",
               "COURT UPHOLDS 'GHETTO' EVICTIONS",
               "Judges rule 91 lease endings were not discrimination.")

    # ---- Bottom story: chess ----
    bx, by, bw, bh = 24, 800, 976, 148
    fill_rect(px, bx, by, bw, bh, WHITE)
    rect_outline(px, bx, by, bw, bh, INK, 2)
    draw_text(px, bx + 20, by + 14, "SPORT  -  GENEVA", 2, RED)
    draw_text(px, bx + 20, by + 38, "CHESS CROWN ON THE LINE", 5, INK)
    draw_text(px, bx + 20, by + 84, "Gukesh defends title against Sindarov, 20,", 3, (70, 70, 70))
    draw_text(px, bx + 20, by + 108, "in the youngest-ever match. Game 1 today.", 3, (70, 70, 70))
    draw_chessboard(px, bx + bw - 148, by + 12, 16)

    # ---- Footer ----
    hline(px, 24, 968, 976, INK, 2)
    draw_text_centered(px, W // 2, 982,
                       "REPORTS PUBLISHED TUESDAY 24 NOVEMBER 2026", 2, GREY)

    return bytes(px)


def png_bytes(px):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += px[yy * W * 3:(yy + 1) * W * 3]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build_image())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
