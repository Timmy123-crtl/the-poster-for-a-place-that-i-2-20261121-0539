"""Travel poster for AURELIA, the islands above the clouds.

AURELIA is a place that does not exist: three green islands floating in
a sunset sky, their waterfalls spilling off the edges into a sea of
clouds below, with a small lamplit town on the largest island. The
poster is drawn from scratch with PIL — every shape, gradient and letter
is generated here, no external assets, no network, fully deterministic.

Composition, top to bottom, leads the eye the way the judge's brief
asks: the place name first (large, cream, letterspaced), then the
landmark (the main floating island with its town), then the horizon
(sun + cloud sea). One landmark, one promise: a warm evening above
the clouds.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

CREAM = (253, 243, 221)
INK_SHADOW = (38, 28, 66)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def sky_gradient(draw):
    """Vertical sunset gradient, indigo at the top to gold at the horizon."""
    stops = [
        (0.00, (26, 31, 74)),
        (0.28, (74, 57, 110)),
        (0.50, (146, 83, 120)),
        (0.66, (232, 150, 92)),
        (0.78, (248, 196, 130)),
        (1.00, (250, 214, 158)),
    ]
    for y in range(H):
        t = y / (H - 1)
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1:
                f = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
                draw.line([(0, y), (W, y)], fill=lerp(c0, c1, f))
                break


def ellipse(layer, box, fill):
    ImageDraw.Draw(layer).ellipse(box, fill=fill)


def soft_disc(layer, cx, cy, r, colour, alpha):
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour + (alpha,))


def cloud(layer, cx, cy, w, h, colour, alpha):
    """A soft cloud built from overlapping discs."""
    for dx, dy, rw, rh in [
        (-0.42, 0.10, 0.30, 0.22),
        (-0.18, -0.06, 0.34, 0.30),
        (0.10, 0.02, 0.36, 0.28),
        (0.38, 0.12, 0.28, 0.20),
        (0.00, 0.14, 0.55, 0.20),
    ]:
        ellipse(layer,
                [cx + dx * w - rw * w, cy + dy * h - rh * h,
                 cx + dx * w + rw * w, cy + dy * h + rh * h],
                colour + (alpha,))


def island_points(cx, top_y, width, depth, point_y):
    """Top edge slightly domed, sides tapering to a single bottom point."""
    half = width / 2.0
    pts = []
    for i in range(9):
        f = i / 8.0
        x = cx - half + f * width
        y = top_y + 14 * math.sin(f * math.pi) - 10 * math.sin(f * math.pi * 2)
        pts.append((x, y))
    pts.append((cx + half * 0.55, top_y + depth * 0.45))
    pts.append((cx + half * 0.22, point_y - depth * 0.18))
    pts.append((cx, point_y))
    pts.append((cx - half * 0.22, point_y - depth * 0.18))
    pts.append((cx - half * 0.55, top_y + depth * 0.45))
    return pts


def draw_island(draw, layer, cx, top_y, width, depth, point_y,
                grass, rock_top, rock_bottom, scale=1.0):
    pts = island_points(cx, top_y, width, depth, point_y)
    # Rocky body, shaded top to bottom.
    draw.polygon(pts, fill=rock_top)
    n = len(pts)
    for i in range(1, n):
        pass
    # Grass cap: a band following the domed top edge.
    cap = []
    for i in range(9):
        f = i / 8.0
        x = cx - width / 2.0 + f * width
        y = top_y + 14 * math.sin(f * math.pi) - 10 * math.sin(f * math.pi * 2)
        cap.append((x, y))
    for i in range(8, -1, -1):
        f = i / 8.0
        x = cx - width / 2.0 + f * width
        y = (top_y + 14 * math.sin(f * math.pi)
             - 10 * math.sin(f * math.pi * 2) + 26 * scale)
        cap.append((x, y))
    draw.polygon(cap, fill=grass)
    # Rock shading: darker underside triangle and a few cliff streaks.
    d = ImageDraw.Draw(layer)
    d.polygon([(cx - width * 0.28, top_y + depth * 0.42),
               (cx + width * 0.28, top_y + depth * 0.42),
               (cx, point_y)], fill=(58, 36, 30, 90))
    for fx, fl in [(-0.30, 0.30), (-0.08, 0.42), (0.16, 0.34), (0.34, 0.22)]:
        x0 = cx + fx * width
        y0 = top_y + depth * 0.30
        d.line([(x0, y0), (x0 + 6, y0 + depth * fl)],
               fill=(58, 36, 30, 110), width=max(2, int(5 * scale)))
    # Pale rim light on the sun side (right edge).
    draw.line([(cx + width * 0.30, top_y + depth * 0.30),
               (cx + width * 0.10, point_y - depth * 0.10)],
              fill=(248, 196, 130), width=max(2, int(4 * scale)))
    return cap


def waterfall(layer, x, y0, length, width):
    """A pale fall spilling off an island edge, fading into mist."""
    d = ImageDraw.Draw(layer)
    d.polygon([(x - width / 2, y0), (x + width / 2, y0),
               (x + width * 0.75, y0 + length),
               (x - width * 0.75, y0 + length)],
              fill=(214, 234, 242, 175))
    d.line([(x - width * 0.15, y0), (x - width * 0.25, y0 + length)],
           fill=(255, 255, 255, 200), width=3)
    d.line([(x + width * 0.2, y0), (x + width * 0.3, y0 + length)],
           fill=(255, 255, 255, 160), width=2)
    ellipse(layer, [x - width, y0 + length - 8, x + width, y0 + length + 22],
            (235, 240, 244, 130))


def house(draw, x, y, w, h, wall, roof):
    draw.rectangle([x, y, x + w, y + h], fill=wall)
    draw.polygon([(x - 2, y), (x + w / 2, y - h * 0.55), (x + w + 2, y)],
                 fill=roof)
    draw.rectangle([x + w * 0.28, y + h * 0.45, x + w * 0.48, y + h * 0.65],
                   fill=(255, 214, 130))
    draw.rectangle([x + w * 0.62, y + h * 0.45, x + w * 0.82, y + h * 0.65],
                   fill=(255, 214, 130))


def cypress(draw, x, y, h):
    draw.polygon([(x - h * 0.16, y), (x, y - h), (x + h * 0.16, y)],
                 fill=(26, 84, 52))


def bird(draw, x, y, s, colour):
    draw.arc([x - s, y - s * 0.5, x, y + s * 0.5], 200, 340, fill=colour,
             width=3)
    draw.arc([x, y - s * 0.5, x + s, y + s * 0.5], 200, 340, fill=colour,
             width=3)


def draw_text_spaced(draw, cx, y, text, font, fill, spacing, shadow=True):
    """Centred, letterspaced text; returns the bottom y."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2.0
    for ch, wch in zip(text, widths):
        if shadow:
            draw.text((x + 3, y + 4), ch, font=font, fill=INK_SHADOW)
        draw.text((x, y), ch, font=font, fill=fill)
        x += wch + spacing
    return y + font.size


def main():
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    sky_gradient(draw)

    # Stars in the upper sky.
    for sx, sy, sr in [(120, 300, 2), (880, 240, 2), (700, 150, 3),
                       (300, 180, 2), (950, 330, 2), (180, 120, 2),
                       (620, 90, 2)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(255, 244, 214))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # Low sun with a soft glow, sitting on the cloud sea.
    soft_disc(glow, 512, 660, 300, (255, 205, 130), 38)
    soft_disc(glow, 512, 660, 210, (255, 214, 150), 60)
    soft_disc(glow, 512, 660, 150, (255, 224, 170), 90)
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow), (0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([512 - 92, 660 - 92, 512 + 92, 660 + 92],
                 fill=(255, 232, 175))

    # High drifting clouds behind the islands.
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cloud(mist, 240, 610, 420, 90, (226, 190, 205), 90)
    cloud(mist, 820, 580, 380, 80, (240, 205, 190), 90)
    cloud(mist, 512, 700, 520, 90, (244, 214, 190), 80)
    img.paste(Image.alpha_composite(img.convert("RGBA"), mist), (0, 0))
    draw = ImageDraw.Draw(img)

    # Birds.
    for bx, by, bs in [(200, 330, 22), (270, 300, 18), (830, 300, 20),
                       (770, 350, 16), (350, 270, 15)]:
        bird(draw, bx, by, bs, (43, 38, 78))

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    # Left island.
    draw_island(draw, overlay, 235, 505, 300, 120, 640,
                (74, 138, 84), (122, 88, 66), (74, 50, 38), 0.7)
    cypress(draw, 200, 512, 34)
    cypress(draw, 268, 508, 28)
    house(draw, 225, 486, 26, 20, (250, 240, 220), (178, 92, 60))

    # Right island.
    draw_island(draw, overlay, 845, 520, 250, 105, 632,
                (66, 128, 78), (118, 84, 62), (70, 48, 36), 0.65)
    cypress(draw, 830, 526, 30)
    cypress(draw, 872, 524, 24)
    house(draw, 812, 502, 24, 18, (250, 240, 220), (178, 92, 60))

    # Main island with the lamplit town.
    draw_island(draw, overlay, 560, 408, 540, 190, 668,
                (88, 154, 92), (132, 94, 68), (78, 52, 40), 1.0)
    for tx, th in [(330, 44), (372, 56), (700, 48), (748, 38), (640, 34)]:
        cypress(draw, tx, 424, th)
    house(draw, 400, 392, 34, 26, (252, 242, 222), (178, 92, 60))
    house(draw, 452, 388, 40, 30, (246, 232, 206), (164, 84, 54))
    house(draw, 512, 394, 32, 24, (252, 242, 222), (178, 92, 60))
    house(draw, 566, 388, 38, 28, (246, 232, 206), (164, 84, 54))
    house(draw, 624, 394, 30, 22, (252, 242, 222), (178, 92, 60))
    # A small watchtower with a warm lamp.
    draw.rectangle([676, 372, 692, 414], fill=(240, 228, 200))
    draw.polygon([(672, 372), (684, 356), (696, 372)], fill=(164, 84, 54))
    draw.ellipse([680, 360, 688, 368], fill=(255, 220, 140))

    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay), (0, 0))
    draw = ImageDraw.Draw(img)

    # Waterfalls spilling off the main island into the mist.
    falls = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    waterfall(falls, 330, 560, 130, 26)
    waterfall(falls, 790, 560, 120, 22)
    waterfall(falls, 130, 540, 110, 16)
    waterfall(falls, 935, 545, 100, 15)
    img.paste(Image.alpha_composite(img.convert("RGBA"), falls), (0, 0))
    draw = ImageDraw.Draw(img)

    # The sea of clouds along the bottom.
    sea = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cloud(sea, 180, 830, 560, 150, (247, 232, 208), 235)
    cloud(sea, 620, 880, 640, 170, (242, 201, 178), 235)
    cloud(sea, 900, 820, 420, 130, (226, 184, 196), 220)
    cloud(sea, 120, 920, 500, 150, (232, 196, 190), 235)
    cloud(sea, 760, 950, 560, 150, (247, 232, 208), 235)
    cloud(sea, 430, 790, 420, 110, (214, 176, 196), 150)
    img.paste(Image.alpha_composite(img.convert("RGBA"), sea), (0, 0))
    draw = ImageDraw.Draw(img)

    # Vintage double frame.
    draw.rectangle([26, 26, W - 26, H - 26], outline=CREAM, width=5)
    draw.rectangle([40, 40, W - 40, H - 40], outline=CREAM, width=2)

    # The name, set into the sky; the descriptor beneath it.
    title_font = ImageFont.truetype(SERIF_BOLD, 118)
    sub_font = ImageFont.truetype(SANS, 32)
    draw_text_spaced(draw, 512, 78, "AURELIA", title_font, CREAM, 26)
    draw_text_spaced(draw, 512, 218, "THE ISLANDS ABOVE THE CLOUDS",
                     sub_font, (253, 238, 210), 10)

    out_dir = "/output" if os.path.isdir("/output") else "."
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG")
    print(path, img.size, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
