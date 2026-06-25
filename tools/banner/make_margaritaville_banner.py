"""Generate the Latitude Margaritaville Watersound YouTube channel banner.

Built at the SAME 2560x1440 canvas as Karen's PCB banner so YouTube's
all-device "safe area" (the red rectangle in the banner crop tool) crops
identically on desktop, tablet, and mobile. Layout mirrors the PCB banner:

    PCB measured bands (2560x1440):
      safe area      x 507..2053   y 508..931
      "LIVING IN"    y ~539..616
      headline       y ~634..842   (big)
      subhead        y ~862..900
      contact        y ~1110..1158 (below safe -> desktop only)
      Karen          enters ~x1689, runs to the right edge

Only the background (Pool.png) and the location words
("Latitude Margaritaville Watersound") differ from the PCB banner.

Run:
    .venv/Scripts/python.exe tools/banner/make_margaritaville_banner.py
"""

from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Match the PCB banner exactly.
W, H = 2560, 1440
SAFE_W, SAFE_H = 1546, 423
SAFE_L = (W - SAFE_W) // 2          # 507
SAFE_T = (H - SAFE_H) // 2          # 508
SAFE_R = SAFE_L + SAFE_W            # 2053
SAFE_B = SAFE_T + SAFE_H            # 931

NWFL = r"C:\Users\mikel\NWFL Beach Homes\NWFL Beach Homes - Documents"
HERO = os.path.join(NWFL, r"Properties\Margaritaville\Escape\Images\Pool.png")
KAREN = os.path.join(NWFL, r"Images\Portraits\Karen Full Length Portrait.png")
SUBSCRIBE = os.path.join(NWFL, r"Images\General Images\Subscribe-Button.png")
OUT = (
    r"R:\YouTube-Channel\docs\library\channel-junkies\resources"
    r"\Margaritaville Channel Banner.png"
)

TEAL = (32, 208, 196)
WHITE = (255, 255, 255)
FONT_DIR = r"C:\Windows\Fonts"


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def cover(img: Image.Image, w: int, h: int) -> Image.Image:
    sr, dr = img.width / img.height, w / h
    if sr > dr:
        nw, nh = round(h * sr), h
    else:
        nw, nh = w, round(w / sr)
    img = img.resize((nw, nh), Image.LANCZOS)
    left, top = (nw - w) // 2, (nh - h) // 2
    return img.crop((left, top, left + w, top + h))


def scale_h(img: Image.Image, h: int) -> Image.Image:
    return img.resize((round(img.width * h / img.height), h), Image.LANCZOS)


def fit_font(draw, text, name, start, max_w, min_size=24):
    size = start
    while size > min_size:
        f = font(name, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(name, min_size)


def text_left(draw, x, y, text, f, fill, shadow=True, track=0.0):
    if track:
        cx = x
        for ch in text:
            if shadow:
                draw.text((cx + 3, y + 3), ch, font=f, fill=(0, 0, 0, 170))
            draw.text((cx, y), ch, font=f, fill=fill)
            cx += draw.textlength(ch, font=f) + track
        return
    if shadow:
        draw.text((x + 3, y + 3), text, font=f, fill=(0, 0, 0, 170))
    draw.text((x, y), text, font=f, fill=fill)


def main() -> None:
    base = cover(Image.open(HERO).convert("RGB"), W, H).convert("RGBA")

    # Overall darken + left-weighted gradient for text legibility.
    base = Image.alpha_composite(base, Image.new("RGBA", (W, H), (8, 22, 30, 95)))
    grad = Image.new("L", (W, 1))
    for x in range(W):
        t = max(0.0, min(1.0, 1.0 - (x - SAFE_L) / (SAFE_W * 0.95)))
        grad.putpixel((x, 0), int(175 * t))
    grad = grad.resize((W, H))
    shade = Image.new("RGBA", (W, H), (4, 16, 24, 0))
    shade.putalpha(grad)
    base = Image.alpha_composite(base, shade)

    # --- Karen, full-length cut-out, on the right (matches PCB framing) ---
    karen = scale_h(Image.open(KAREN).convert("RGBA"), 1400)
    kx, ky = 1620, SAFE_T - 120
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sil = Image.new("RGBA", karen.size, (0, 0, 0, 0))
    sil.paste((0, 0, 0, 130), (0, 0), karen)
    shadow.paste(sil, (kx + 18, ky + 20), sil)
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    base = Image.alpha_composite(base, shadow)
    base.paste(karen, (kx, ky), karen)

    draw = ImageDraw.Draw(base)
    tx = SAFE_L + 18
    text_w = max(820, kx - tx - 40)

    # "LIVING IN"  (PCB y ~539..616)
    text_left(draw, tx, 543, "LIVING IN", font("arialbd.ttf", 60), TEAL, track=14)

    # Headline (PCB y ~634..842) -> two lines
    f_h = fit_font(draw, "Latitude Margaritaville", "ariblk.ttf", 132, text_w)
    text_left(draw, tx, 636, "Latitude Margaritaville", f_h, WHITE)
    text_left(draw, tx, 636 + int(f_h.size * 1.05), "Watersound", f_h, WHITE)

    # Subhead (PCB y ~862..900)
    f_sub = fit_font(
        draw, "THINKING ABOUT 55+ LIVING? I'M HERE TO HELP!",
        "arialbd.ttf", 44, text_w,
    )
    text_left(draw, tx, 866, "THINKING ABOUT 55+ LIVING? I'M HERE TO HELP!",
              f_sub, TEAL)

    # Contact (PCB y ~1110..1158, below safe area -> desktop)
    f_c = font("arialbd.ttf", 40)
    text_left(draw, tx, 1098, "TEXT / CALL: (850) 517-8528", f_c, WHITE)
    text_left(draw, tx, 1150, "Karen@nwflbeachhomes.com", f_c, WHITE)

    # Subscribe + bell graphic, lower-left.
    sub = scale_h(Image.open(SUBSCRIBE).convert("RGBA"), 170)
    base.paste(sub, (tx + 760, 1090), sub)

    base.convert("RGB").save(OUT, "PNG")
    print("Saved:", OUT, base.size)


if __name__ == "__main__":
    main()
