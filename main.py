#!/usr/bin/env python3
"""Draw a one-page infographic summing up the world news of
Thursday 19 November 2026 and write it as entry.png.

Standard library only.  Contains its own PNG encoder and its own
5x7 bitmap font; no external assets, fonts or network access.
Output is deterministic: the same bytes on every run.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- colors
BG       = (246, 244, 238)   # off-white page
NAVY     = (16, 30, 52)      # masthead / footer
NAVY_TX  = (238, 242, 248)   # text on navy
NAVY_SUB = (168, 182, 204)   # muted text on navy
GOLD     = (212, 164, 44)    # accent rule
PANEL    = (255, 255, 255)   # panel background
BORDER   = (196, 200, 206)   # panel border
INK      = (24, 28, 36)      # headline text
BODY     = (84, 92, 106)     # sub-line text
RED      = (178, 44, 40)
BLUE     = (36, 84, 158)
ORANGE   = (226, 116, 28)
YELLOW   = (246, 196, 66)
GREEN    = (38, 138, 74)
TEAL     = (24, 128, 138)
PURPLE   = (104, 62, 158)

# ---------------------------------------------------------------- canvas
PX = bytearray(W * H * 3)


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PX[i] = color[0]
        PX[i + 1] = color[1]
        PX[i + 2] = color[2]


def rect(x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, color)


def circle(cx, cy, r, color):
    r2 = r * r
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r2:
                set_px(xx, yy, color)


def ellipse(cx, cy, a, b, color):
    for yy in range(cy - b, cy + b + 1):
        for xx in range(cx - a, cx + a + 1):
            dx = (xx - cx) / a
            dy = (yy - cy) / b
            if dx * dx + dy * dy <= 1.0:
                set_px(xx, yy, color)


def triangle(p1, p2, p3, color):
    (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
    minx = max(0, min(x1, x2, x3))
    maxx = min(W - 1, max(x1, x2, x3))
    miny = max(0, min(y1, y2, y3))
    maxy = min(H - 1, max(y1, y2, y3))
    d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    if d == 0:
        return
    for yy in range(miny, maxy + 1):
        for xx in range(minx, maxx + 1):
            w1 = ((y2 - y3) * (xx - x3) + (x3 - x2) * (yy - y3)) / d
            w2 = ((y3 - y1) * (xx - x3) + (x1 - x3) * (yy - y3)) / d
            w3 = 1.0 - w1 - w2
            if w1 >= 0 and w2 >= 0 and w3 >= 0:
                set_px(xx, yy, color)


def thick_line(x1, y1, x2, y2, color, t=3):
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    r = t // 2
    for i in range(steps + 1):
        x = x1 + (x2 - x1) * i // steps
        y = y1 + (y2 - y1) * i // steps
        rect(x - r, y - r, t, t, color)


# ---------------------------------------------------------------- font
# 5x7 glyphs, each row a 5-bit pattern, MSB = leftmost pixel.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    'X': (0x11, 0x0A, 0x04, 0x04, 0x04, 0x0A, 0x11),
    'Y': (0x11, 0x0A, 0x04, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ',': (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    ':': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x00, 0x08),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '%': (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x0B),
    '-': (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '+': (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
}


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, color, bold=False):
    """Draw text with top-left corner at (x, y). Returns the x end."""
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[' '])
        passes = (0, max(1, scale // 2)) if bold else (0,)
        for off in passes:
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (0x10 >> col):
                        rect(x + off + col * scale, y + row * scale,
                             scale, scale, color)
        x += 6 * scale
    return x


def draw_text_centered(y, text, scale, color, bold=False):
    x = (W - text_width(text, scale)) // 2
    draw_text(x, y, text, scale, color, bold)


def wrap_text(text, scale, max_width):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, text, scale, color, max_width, line_gap, bold=False):
    lines = wrap_text(text, scale, max_width)
    for line in lines:
        draw_text(x, y, line, scale, color, bold)
        y += 7 * scale + line_gap
    return y


# ---------------------------------------------------------------- icons
def icon_circles(cx, cy):
    """Three overlapping circles: the three leaders at one table."""
    circle(cx - 26, cy + 8, 30, RED)
    circle(cx + 26, cy + 8, 30, BLUE)
    circle(cx, cy - 18, 30, GOLD)


def icon_scales(cx, cy, color):
    rect(cx - 2, cy - 30, 5, 56, color)                    # post
    rect(cx - 30, cy - 30, 65, 5, color)                   # beam
    circle(cx, cy - 33, 5, color)                          # finial
    for sx in (cx - 26, cx + 30):                          # pans
        thick_line(sx, cy - 25, sx - 9, cy + 2, color, 2)
        thick_line(sx, cy - 25, sx + 9, cy + 2, color, 2)
        ellipse(sx, cy + 4, 11, 5, color)
    rect(cx - 14, cy + 26, 33, 5, color)                   # base


def icon_bridge(cx, cy, color):
    rect(cx - 36, cy + 14, 76, 5, color)                   # deck
    rect(cx - 30, cy - 22, 6, 38, color)                   # towers
    rect(cx + 28, cy - 22, 6, 38, color)
    for i in range(37):                                    # main cable arc
        t = i / 36.0
        x = cx - 33 + int(72 * t)
        y = cy - 20 + int(30 * (2 * t - 1) ** 2)
        rect(x, y, 3, 3, color)
    for dx in (-18, 0, 18):                                # hangers
        thick_line(cx + dx, cy - 4, cx + dx, cy + 14, color, 2)
    for i in range(8):                                     # water
        rect(cx - 32 + i * 9, cy + 28, 6, 3, TEAL)


def icon_flame(cx, cy):
    triangle((cx, cy - 36), (cx - 20, cy + 12), (cx + 20, cy + 12), ORANGE)
    circle(cx, cy + 10, 20, ORANGE)
    triangle((cx, cy - 14), (cx - 11, cy + 14), (cx + 11, cy + 14), YELLOW)
    circle(cx, cy + 13, 11, YELLOW)
    circle(cx, cy + 16, 6, RED)


def icon_leaf(cx, cy, color):
    ellipse(cx, cy, 26, 15, color)
    triangle((cx + 14, cy - 20), (cx + 30, cy - 30), (cx + 26, cy - 8), color)
    thick_line(cx - 22, cy + 12, cx + 20, cy - 14, BG, 2)  # vein
    thick_line(cx + 18, cy + 14, cx + 30, cy + 24, color, 4)  # stem


def icon_chart(cx, cy, color):
    rect(cx - 34, cy - 30, 4, 62, INK)                     # axis y
    rect(cx - 34, cy + 28, 70, 4, INK)                     # axis x
    pts = [(cx - 26, cy + 18), (cx - 8, cy + 4), (cx + 8, cy + 10),
           (cx + 26, cy - 16)]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        thick_line(x1, y1, x2, y2, color, 5)
    triangle((pts[-1][0] + 12, pts[-1][1] - 2),
             (pts[-1][0] - 4, pts[-1][1] - 8),
             (pts[-1][0] + 2, pts[-1][1] + 8), color)  # arrowhead


# ---------------------------------------------------------------- layout
def panel(x, y, w, h, accent):
    rect(x, y, w, h, PANEL)
    rect(x, y, w, 3, BORDER)
    rect(x, y + h - 3, w, 3, BORDER)
    rect(x, y, 3, h, BORDER)
    rect(x + w - 3, y, 3, h, BORDER)
    rect(x, y, 8, h, accent)


def small_story(x, y, w, h, accent, icon, headline, sub):
    panel(x, y, w, h, accent)
    icon(x + 52, y + h // 2)
    tx = x + 100
    tw = w - 100 - 18
    hy = draw_wrapped(tx, y + 22, headline, 2, INK, tw, 7, bold=True)
    draw_wrapped(tx, hy + 9, sub, 2, BODY, tw, 6)


def build():
    rect(0, 0, W, H, BG)

    # ---- masthead
    rect(0, 0, W, 168, NAVY)
    draw_text_centered(24, "THE WORLD IN ONE DAY", 3, NAVY_SUB)
    draw_text_centered(58, "THURSDAY 19 NOVEMBER 2026", 6, NAVY_TX, bold=True)
    rect(312, 122, 400, 3, GOLD)
    draw_text_centered(136, "GLOBAL HEADLINES ON ONE PAGE", 2, NAVY_SUB)
    rect(0, 168, W, 6, GOLD)

    # ---- lead story
    lx, ly, lw, lh = 28, 198, 968, 238
    panel(lx, ly, lw, lh, RED)
    draw_text(lx + 30, ly + 24, "LEAD STORY", 2, RED, bold=True)
    icon_circles(lx + 108, ly + 146)
    tx = lx + 216
    tw = lw - 216 - 26
    hy = draw_wrapped(tx, ly + 64,
                      "SHENZHEN SUMMIT: TRUMP, XI AND PUTIN MEET FACE TO FACE",
                      4, INK, tw, 12, bold=True)
    rect(tx, hy + 6, tw, 3, BORDER)
    draw_wrapped(tx, hy + 26,
                 "APEC TALKS END WITH A JOINT PEACE DECLARATION",
                 2, BODY, tw, 8)
    draw_text(tx, hy + 58,
              "NUCLEAR RISKS, UKRAINE AND IRAN TOP THE AGENDA",
              2, BODY)

    # ---- grid of four small stories
    gy = 456
    gh = 148
    gw = 474
    small_story(28, gy, gw, gh, BLUE, lambda cx, cy: icon_scales(cx, cy, BLUE),
                "WORLD COURT RULES MYANMAR COMMITTED GENOCIDE",
                "ICJ VERDICT IN THE ROHINGYA CASE, A FIRST OF ITS KIND")
    small_story(522, gy, gw, gh, TEAL, lambda cx, cy: icon_bridge(cx, cy, TEAL),
                "UKRAINE STRIKES THE CRIMEAN BRIDGE AGAIN",
                "THIRD ATTACK THIS WEEK ON THE KERCH LINK")
    gy2 = gy + gh + 18
    small_story(28, gy2, gw, gh, ORANGE, icon_flame,
                "IRAN TENSIONS FLARE ACROSS THE GULF",
                "TRUMP WARNS TEHRAN AS DRONES AND MISSILES FLY")
    small_story(522, gy2, gw, gh, GREEN, lambda cx, cy: icon_leaf(cx, cy, GREEN),
                "COP31 CLIMATE TALKS GO TO THE WIRE",
                "FOSSIL FUEL PHASE-OUT WORDING STILL UNRESOLVED")

    # ---- wide fifth story
    wy = gy2 + gh + 18
    panel(28, wy, 968, 158, PURPLE)
    icon_chart(118, wy + 82, GREEN)
    draw_text(216, wy + 44, "ANTHROPIC SETS AN IPO RECORD", 3, INK, bold=True)
    draw_text(216, wy + 96, "$81 BILLION RAISED AT A $1.5 TRILLION VALUE",
              2, BODY)
    for i, bh in enumerate((18, 30, 24, 44, 58)):
        rect(820 + i * 32, wy + 124 - bh, 20, bh, PURPLE)

    # ---- footer
    fy = 950
    rect(0, fy, W, H - fy, NAVY)
    rect(0, fy, W, 5, GOLD)
    draw_text_centered(fy + 18,
                       "DENMARK SEALS GREENLAND ARCTIC PACT - FIJI DECLARES EL NINO",
                       2, NAVY_TX)
    draw_text_centered(fy + 46,
                       "DROUGHT DISASTER - 589M CHILDREN NOW LIVE IN CONFLICT ZONES",
                       2, NAVY_TX)


# ---------------------------------------------------------------- PNG out
def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def encode_png():
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += PX[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


def main():
    build()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(encode_png())
    print("wrote", path)


if __name__ == "__main__":
    main()
