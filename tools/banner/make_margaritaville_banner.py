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
HERO = os.path.join(NWFL, r"Properties\Bay County\Panama City Beach\West Bay & HWY 79 Corridor\Latitude Margaritaville Watersound\Models\Escape\Images\Pool.png")
KAREN = os.path.join(NWFL, r"Images\Portraits\Karen Full Length Portrait.png")
SUBSCRIBE = os.path.join(NWFL, r"Images\General Images\Subscribe-Button.png")
BANNERS = os.path.join(NWFL, r"Images\Banners")
OUT_YOUTUBE = os.path.join(BANNERS, "Margaritaville Channel Banner - YouTube.png")
OUT_FACEBOOK = os.path.join(BANNERS, "Margaritaville Channel Banner - Facebook.png")

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


def text_center(draw, cx, y, text, f, fill, shadow=True, track=0.0):
    """Draw text horizontally centered on cx (supports letter tracking)."""
    if track:
        w = sum(draw.textlength(ch, font=f) + track for ch in text) - track
        x = cx - w / 2
        for ch in text:
            if shadow:
                draw.text((x + 3, y + 3), ch, font=f, fill=(0, 0, 0, 170))
            draw.text((x, y), ch, font=f, fill=fill)
            x += draw.textlength(ch, font=f) + track
        return
    w = draw.textlength(text, font=f)
    text_left(draw, cx - w / 2, y, text, f, fill, shadow=shadow)


def build_youtube(out_path: str, with_subscribe: bool = True) -> None:
    """Realtor-branded banner: Karen's photo, sales CTA, contact, Subscribe."""
    base = cover(Image.open(HERO).convert("RGB"), W, H).convert("RGBA")

    # Overall darken + right-weighted gradient (text now sits on the right).
    base = Image.alpha_composite(base, Image.new("RGBA", (W, H), (8, 22, 30, 95)))
    grad = Image.new("L", (W, 1))
    for x in range(W):
        t = max(0.0, min(1.0, (x - 760) / (W - 760)))
        grad.putpixel((x, 0), int(175 * t))
    grad = grad.resize((W, H))
    shade = Image.new("RGBA", (W, H), (4, 16, 24, 0))
    shade.putalpha(grad)
    base = Image.alpha_composite(base, shade)

    # --- Karen, full-length cut-out, on the LEFT (original orientation) ---
    karen = scale_h(Image.open(KAREN).convert("RGBA"), 1400)
    kx, ky = 300, SAFE_T - 120
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sil = Image.new("RGBA", karen.size, (0, 0, 0, 0))
    sil.paste((0, 0, 0, 130), (0, 0), karen)
    shadow.paste(sil, (kx + 18, ky + 20), sil)
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    base = Image.alpha_composite(base, shadow)
    base.paste(karen, (kx, ky), karen)

    draw = ImageDraw.Draw(base)
    # Wording sits to the RIGHT of Karen.
    tx = kx + karen.width + 70
    text_w = max(820, SAFE_R - tx - 10)

    # "RETIRE IN"  (PCB y ~539..616)
    text_left(draw, tx, 543, "RETIRE IN", font("arialbd.ttf", 60), TEAL, track=14)

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

    # Subscribe + bell graphic, lower-right (YouTube only).
    if with_subscribe:
        sub = scale_h(Image.open(SUBSCRIBE).convert("RGBA"), 170)
        base.paste(sub, (tx + 760, 1090), sub)

    base.convert("RGB").save(out_path, "PNG")
    print("Saved:", out_path, base.size)


def build_facebook(out_path: str) -> None:
    """Community / info banner at proper Facebook cover dimensions.

    Facebook Page cover photos display at 851x315 (desktop) and 640x360
    (mobile). We render at 1702x630 -- 2x the desktop display, ratio 2.70:1 --
    so the upload is crisp and undistorted. All text is centered and kept
    within the mobile-safe width, since Facebook trims the left/right edges
    of the cover on phones.
    """
    FB_W, FB_H = 1702, 630
    # Mobile shows roughly the center 75% of the width -> keep text inside this.
    safe_w = int(FB_W * 0.72)

    base = cover(Image.open(HERO).convert("RGB"), FB_W, FB_H).convert("RGBA")

    # Even darken, then a centered horizontal vignette so the centered text
    # block stays legible over the pool imagery.
    base = Image.alpha_composite(base, Image.new("RGBA", (FB_W, FB_H), (8, 22, 30, 110)))
    grad = Image.new("L", (FB_W, 1))
    for x in range(FB_W):
        d = abs(x - FB_W / 2) / (FB_W / 2)     # 0 at center -> 1 at edges
        grad.putpixel((x, 0), int(150 * (1 - d)))
    grad = grad.resize((FB_W, FB_H))
    shade = Image.new("RGBA", (FB_W, FB_H), (4, 16, 24, 0))
    shade.putalpha(grad)
    base = Image.alpha_composite(base, shade)

    draw = ImageDraw.Draw(base)
    cx = FB_W // 2

    # Eyebrow (teal, tracked)
    text_center(draw, cx, 66, "YOUR 55+ RETIREMENT GUIDE TO",
                font("arialbd.ttf", 34), TEAL, track=8)

    # Headline (white) -> two centered lines
    f_h = fit_font(draw, "Latitude Margaritaville", "ariblk.ttf", 88, safe_w)
    h1_y = 128
    h2_y = h1_y + int(f_h.size * 1.02)
    text_center(draw, cx, h1_y, "Latitude Margaritaville", f_h, WHITE)
    text_center(draw, cx, h2_y, "Watersound", f_h, WHITE)

    # Subhead (teal): placed below the headline so it never overlaps "Watersound"
    sub_y = h2_y + f_h.size + 14
    text_center(draw, cx, sub_y,
                "55+ Active Adult Living  \u2022  Photos  \u2022  Q&A  \u2022  Resident Insights",
                font("arialbd.ttf", 28), TEAL)

    # Expectation-setting line
    text_center(draw, cx, 512,
                "An unofficial community for current & future residents",
                font("arialbd.ttf", 24), WHITE)

    # Required legal disclaimer (non-affiliation) -> smaller, bottom line.
    text_center(draw, cx, 560,
                "Neither I nor my brokerage is affiliated with or endorsed by "
                "Latitude Margaritaville, LMWS or Minto Communities.",
                font("arial.ttf", 20), WHITE)

    base.convert("RGB").save(out_path, "PNG")
    print("Saved:", out_path, base.size)


def main() -> None:
    build_youtube(OUT_YOUTUBE, with_subscribe=True)
    build_facebook(OUT_FACEBOOK)


if __name__ == "__main__":
    main()
