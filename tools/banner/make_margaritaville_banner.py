"""Generate the Latitude Margaritaville Watersound YouTube channel banner.

Matches the look of Karen's PCB channel banner (see
docs/library/channel-junkies/playbook/margaritaville-banner-brief.md):
- Karen's full-length cut-out on the right
- Headline / tagline / contact text block on the left
- Subscribe + bell graphic
- Tropical Latitude Margaritaville Watersound community background

All critical content is kept inside YouTube's all-device safe area
(center 1235 x 338 of the 2048 x 1152 canvas).

Run:
    .venv/Scripts/python.exe tools/banner/make_margaritaville_banner.py
"""

from __future__ import annotations

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 2048, 1152
SAFE_W, SAFE_H = 1235, 338
SAFE_L = (W - SAFE_W) // 2          # 406
SAFE_T = (H - SAFE_H) // 2          # 407
SAFE_R = SAFE_L + SAFE_W            # 1641
SAFE_B = SAFE_T + SAFE_H            # 745

NWFL = r"C:\Users\mikel\NWFL Beach Homes\NWFL Beach Homes - Documents"
HERO = os.path.join(
    NWFL,
    r"Properties\Margaritaville\Escape\Images"
    r"\pool-and-bar-drone-1-by-rhp-12309-1687548916.jpg",
)
KAREN = os.path.join(NWFL, r"Images\Portraits\Karen Full Length Portrait.png")
SUBSCRIBE = os.path.join(NWFL, r"Images\General Images\Subscribe-Button.png")
OUT = (
    r"R:\YouTube-Channel\docs\library\channel-junkies\resources"
    r"\Margaritaville Channel Banner.png"
)

TEAL = (32, 208, 196)
PINK = (255, 120, 170)
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


def fit_font(draw, text, name, start, max_w, min_size=20):
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
                draw.text((cx + 2, y + 2), ch, font=f, fill=(0, 0, 0, 160))
            draw.text((cx, y), ch, font=f, fill=fill)
            cx += draw.textlength(ch, font=f) + track
        return
    if shadow:
        draw.text((x + 2, y + 2), text, font=f, fill=(0, 0, 0, 160))
    draw.text((x, y), text, font=f, fill=fill)


def main() -> None:
    base = cover(Image.open(HERO).convert("RGB"), W, H).convert("RGBA")

    # Overall darken for legibility.
    base = Image.alpha_composite(base, Image.new("RGBA", (W, H), (8, 22, 30, 95)))

    # Left-to-right dark gradient so the text side is darker than the photo side.
    grad = Image.new("L", (W, 1))
    for x in range(W):
        t = max(0.0, min(1.0, 1.0 - (x - SAFE_L) / (SAFE_W * 0.95)))
        grad.putpixel((x, 0), int(165 * t))
    grad = grad.resize((W, H))
    shade = Image.new("RGBA", (W, H), (4, 16, 24, 0))
    shade.putalpha(grad)
    base = Image.alpha_composite(base, shade)

    # --- Karen, full-length cut-out, on the right ---
    karen = Image.open(KAREN).convert("RGBA")
    kh = 1230
    karen = scale_h(karen, kh)
    # Face sits ~12% from the top of the cut-out; place so it lands in safe band.
    ky = SAFE_T - 60
    kx = min(SAFE_R - karen.width + 250, W - karen.width + 140)
    # soft shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sil = Image.new("RGBA", karen.size, (0, 0, 0, 0))
    sil.paste((0, 0, 0, 130), (0, 0), karen)
    shadow.paste(sil, (kx + 14, ky + 16), sil)
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    base = Image.alpha_composite(base, shadow)
    base.paste(karen, (kx, ky), karen)

    draw = ImageDraw.Draw(base)

    # --- Text block on the left, within the safe area ---
    tx = SAFE_L + 24
    text_w = max(620, min(kx - tx - 30, 880))
    y = SAFE_T + 4

    f_pre = font("arialbd.ttf", 30)
    text_left(draw, tx, y, "LIVING IN", f_pre, TEAL, track=8)
    y += 46

    f_h = fit_font(draw, "Latitude Margaritaville", "ariblk.ttf", 70, text_w)
    text_left(draw, tx, y, "Latitude Margaritaville", f_h, WHITE)
    y += int(f_h.size * 1.02)
    text_left(draw, tx, y, "Watersound", f_h, WHITE)
    y += int(f_h.size * 1.18)

    f_sub = fit_font(
        draw, "THINKING ABOUT 55+ LIVING? I'M HERE TO HELP!",
        "arialbd.ttf", 30, text_w,
    )
    text_left(draw, tx, y, "THINKING ABOUT 55+ LIVING? I'M HERE TO HELP!",
              f_sub, TEAL)
    y += int(f_sub.size * 1.7)

    f_c = fit_font(draw, "TEXT / CALL: (850) 517-8528", "arialbd.ttf", 28, text_w)
    text_left(draw, tx, y, "TEXT / CALL: (850) 517-8528", f_c, WHITE)
    y += int(f_c.size * 1.25)
    text_left(draw, tx, y, "Karen@nwflbeachhomes.com", f_c, WHITE)

    # --- Subscribe + bell graphic, just under the text block ---
    sub = Image.open(SUBSCRIBE).convert("RGBA")
    sub = sub.resize((round(sub.width * 118 / sub.height), 118), Image.LANCZOS)
    base.paste(sub, (tx, y + 20), sub)

    base.convert("RGB").save(OUT, "PNG")
    print("Saved:", OUT, base.size)


if __name__ == "__main__":
    main()
