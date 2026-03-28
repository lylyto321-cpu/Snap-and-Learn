#!/usr/bin/env python3
"""Generate Google Play Store graphics for Snap & Learn."""

import os
import math
from PIL import Image, ImageDraw, ImageFont

# === Config ===
OUT = "/Users/lyanneliang/Snap-and-Learn/store-listing"
os.makedirs(OUT, exist_ok=True)

GREEN = (58, 125, 68)
DARK_GREEN = (40, 95, 48)
LIGHT_GREEN = (78, 155, 88)
WHITE = (255, 255, 255)
NEAR_WHITE = (248, 250, 248)
LIGHT_GRAY = (230, 235, 230)
DARK_TEXT = (30, 40, 30)
MID_TEXT = (80, 100, 80)

# --- Font helpers ---
def find_font(size, bold=False):
    """Try to find a good font, fall back to default."""
    candidates = []
    if bold:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    # Fall back to default bitmap font
    return ImageFont.load_default()


def find_cjk_font(size):
    """Find a font that can render Chinese characters."""
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return find_font(size, bold=True)


def text_size(draw, text, font):
    """Get text bounding box width and height."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_rounded_rect(draw, xy, radius, fill):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    r = radius
    # Four corners
    draw.ellipse([x0, y0, x0 + 2*r, y0 + 2*r], fill=fill)
    draw.ellipse([x1 - 2*r, y0, x1, y0 + 2*r], fill=fill)
    draw.ellipse([x0, y1 - 2*r, x0 + 2*r, y1], fill=fill)
    draw.ellipse([x1 - 2*r, y1 - 2*r, x1, y1], fill=fill)
    # Rectangles to fill gaps
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)


def draw_camera_icon(draw, cx, cy, size, color):
    """Draw a simple camera icon."""
    w = size
    h = size * 0.7
    # Body
    draw_rounded_rect(draw, (cx - w/2, cy - h/2 + size*0.1, cx + w/2, cy + h/2 + size*0.1), size*0.08, color)
    # Lens (circle)
    lr = size * 0.2
    draw.ellipse([cx - lr, cy - lr + size*0.1, cx + lr, cy + lr + size*0.1], outline=WHITE, width=max(3, int(size*0.04)))
    # Top bump
    bw = size * 0.25
    bh = size * 0.12
    draw.rectangle([cx - bw/2, cy - h/2 - bh + size*0.1, cx + bw/2, cy - h/2 + size*0.1 + 2], fill=color)


def draw_book_icon(draw, cx, cy, size, color):
    """Draw a simple dictionary/book icon."""
    w = size * 0.7
    h = size * 0.85
    x0, y0 = cx - w/2, cy - h/2
    # Book cover
    draw_rounded_rect(draw, (x0, y0, x0 + w, y0 + h), size*0.06, color)
    # Spine
    draw.rectangle([x0, y0, x0 + w*0.15, y0 + h], fill=DARK_GREEN)
    # Pages (white rectangle)
    margin = size * 0.08
    draw.rectangle([x0 + w*0.2, y0 + margin, x0 + w - margin, y0 + h - margin], fill=WHITE)
    # Lines on page
    lw = max(2, int(size * 0.025))
    for i in range(3):
        ly = y0 + margin + (h - 2*margin) * (0.25 + i * 0.25)
        draw.line([x0 + w*0.28, ly, x0 + w - margin - size*0.06, ly], fill=LIGHT_GRAY, width=lw)


def draw_flashcard_icon(draw, cx, cy, size, color):
    """Draw flashcard icon - two overlapping cards."""
    w = size * 0.65
    h = size * 0.45
    off = size * 0.08
    # Back card (slightly offset)
    draw_rounded_rect(draw, (cx - w/2 + off, cy - h/2 - off, cx + w/2 + off, cy + h/2 - off), size*0.05, LIGHT_GREEN)
    # Front card
    draw_rounded_rect(draw, (cx - w/2 - off, cy - h/2 + off, cx + w/2 - off, cy + h/2 + off), size*0.05, color)
    # Chinese character on front card
    cjk = find_cjk_font(int(size * 0.22))
    tw, th = text_size(draw, "字", cjk)
    draw.text((cx - off - tw/2, cy + off - th/2 - size*0.02), "字", fill=WHITE, font=cjk)


def draw_chart_icon(draw, cx, cy, size, color):
    """Draw a simple bar chart icon."""
    bars = [0.4, 0.65, 0.5, 0.85, 0.7]
    total_w = size * 0.7
    bar_w = total_w / (len(bars) * 2 - 1)
    base_y = cy + size * 0.35
    top_y = cy - size * 0.35
    range_h = base_y - top_y
    sx = cx - total_w / 2
    for i, pct in enumerate(bars):
        bx = sx + i * bar_w * 2
        by = base_y - range_h * pct
        bar_color = LIGHT_GREEN if i % 2 == 0 else color
        draw_rounded_rect(draw, (bx, by, bx + bar_w, base_y), bar_w*0.2, bar_color)


# ===================================================
# 1. FEATURE GRAPHIC (1024 x 500)
# ===================================================
def create_feature_graphic():
    img = Image.new("RGB", (1024, 500), GREEN)
    draw = ImageDraw.Draw(img)

    # Subtle decorative circles in background
    for (dx, dy, r, alpha) in [(-100, 400, 200, 20), (900, -50, 180, 15), (500, 450, 150, 18), (200, -80, 120, 12)]:
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([dx - r, dy - r, dx + r, dy + r], fill=(255, 255, 255, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    # Try to place the app icon
    icon_placed = False
    try:
        icon = Image.open("/tmp/icon_final.png").convert("RGBA")
        icon = icon.resize((140, 140), Image.LANCZOS)
        # Place icon on left side
        icon_x, icon_y = 180, 180
        # Create a temp RGBA version to paste
        img_rgba = img.convert("RGBA")
        img_rgba.paste(icon, (icon_x, icon_y), icon)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)
        icon_placed = True
    except Exception:
        pass

    # App name
    title_font = find_font(72, bold=True)
    subtitle_font = find_font(28, bold=False)

    title = "Snap & Learn"
    tw, th = text_size(draw, title, title_font)

    if icon_placed:
        text_x = 350
    else:
        text_x = (1024 - tw) // 2

    text_y = 170
    # Shadow
    draw.text((text_x + 2, text_y + 2), title, fill=(30, 80, 40), font=title_font)
    draw.text((text_x, text_y), title, fill=WHITE, font=title_font)

    # Subtitle
    sub = "Learn Chinese from the world around you"
    sw, sh = text_size(draw, sub, subtitle_font)
    sub_x = text_x + (tw - sw) // 2 if not icon_placed else text_x
    draw.text((sub_x, text_y + th + 20), sub, fill=(220, 240, 220), font=subtitle_font)

    # Decorative line below subtitle
    line_y = text_y + th + 20 + sh + 15
    line_w = 80
    draw.rectangle([text_x, line_y, text_x + line_w, line_y + 3], fill=(255, 255, 255, 180))

    img.save(os.path.join(OUT, "feature_graphic.png"), "PNG")
    print("Created feature_graphic.png")


# ===================================================
# 2. PHONE SCREENSHOTS (1080 x 2400)
# ===================================================
SCREEN_W, SCREEN_H = 1080, 2400

def create_screenshot(filename, headline, description, draw_icon_func, accent_detail_func=None):
    img = Image.new("RGB", (SCREEN_W, SCREEN_H), NEAR_WHITE)
    draw = ImageDraw.Draw(img)

    # Top colored band
    band_h = 220
    draw.rectangle([0, 0, SCREEN_W, band_h], fill=GREEN)

    # Subtle pattern dots on band
    for i in range(20):
        dx = (i * 137) % SCREEN_W
        dy = (i * 83) % band_h
        r = 3 + (i % 4)
        draw.ellipse([dx-r, dy-r, dx+r, dy+r], fill=(255, 255, 255, 15))

    # Status bar area (time, battery etc placeholder)
    status_font = find_font(24, bold=False)
    draw.text((40, 20), "9:41", fill=WHITE, font=status_font)

    # Icon area - large circle with icon
    circle_cy = band_h + 350
    circle_r = 200
    # Green circle background
    draw.ellipse([SCREEN_W//2 - circle_r, circle_cy - circle_r,
                  SCREEN_W//2 + circle_r, circle_cy + circle_r], fill=GREEN)
    # Lighter inner circle
    inner_r = circle_r - 12
    draw.ellipse([SCREEN_W//2 - inner_r, circle_cy - inner_r,
                  SCREEN_W//2 + inner_r, circle_cy + inner_r], fill=LIGHT_GREEN)
    # Even lighter center
    center_r = inner_r - 15
    draw.ellipse([SCREEN_W//2 - center_r, circle_cy - center_r,
                  SCREEN_W//2 + center_r, circle_cy + center_r], fill=GREEN)

    # Draw the icon inside the circle
    draw_icon_func(draw, SCREEN_W // 2, circle_cy, circle_r * 1.5, WHITE)

    # Headline text
    h_font = find_font(64, bold=True)
    hw, hh = text_size(draw, headline, h_font)
    h_y = circle_cy + circle_r + 100
    draw.text(((SCREEN_W - hw) // 2, h_y), headline, fill=DARK_TEXT, font=h_font)

    # Description text
    d_font = find_font(34, bold=False)
    dw, dh = text_size(draw, description, d_font)
    d_y = h_y + hh + 30
    draw.text(((SCREEN_W - dw) // 2, d_y), description, fill=MID_TEXT, font=d_font)

    # Decorative accent line
    line_y = d_y + dh + 50
    line_w = 60
    draw.rectangle([(SCREEN_W - line_w)//2, line_y, (SCREEN_W + line_w)//2, line_y + 4], fill=GREEN)

    # Additional detail area below
    if accent_detail_func:
        accent_detail_func(draw, img, SCREEN_W, line_y + 60)

    # Bottom branding
    brand_font = find_font(28, bold=True)
    brand = "Snap & Learn"
    bw, bh = text_size(draw, brand, brand_font)
    draw.text(((SCREEN_W - bw) // 2, SCREEN_H - 120), brand, fill=GREEN, font=brand_font)

    # Bottom dots (page indicator)
    dot_y = SCREEN_H - 60
    dot_r = 8
    dot_spacing = 30
    num_dots = 4
    dot_start = SCREEN_W // 2 - (num_dots - 1) * dot_spacing // 2
    screenshot_index = ["screenshot_1.png", "screenshot_2.png", "screenshot_3.png", "screenshot_4.png"].index(filename)
    for i in range(num_dots):
        dx = dot_start + i * dot_spacing
        c = GREEN if i == screenshot_index else LIGHT_GRAY
        draw.ellipse([dx - dot_r, dot_y - dot_r, dx + dot_r, dot_y + dot_r], fill=c)

    img.save(os.path.join(OUT, filename), "PNG")
    print(f"Created {filename}")


def detail_camera(draw, img, w, start_y):
    """Show a mock camera viewfinder area."""
    margin = 120
    box_h = 500
    y0 = start_y + 40
    # Rounded rect frame
    draw_rounded_rect(draw, (margin, y0, w - margin, y0 + box_h), 20, (240, 245, 240))
    # Inner "viewfinder" area
    inner_m = 20
    draw_rounded_rect(draw, (margin + inner_m, y0 + inner_m, w - margin - inner_m, y0 + box_h - inner_m), 14, WHITE)
    # Corner brackets (camera viewfinder style)
    bracket_len = 40
    bracket_w = 4
    corners = [
        (margin + inner_m + 30, y0 + inner_m + 30),  # top-left
        (w - margin - inner_m - 30, y0 + inner_m + 30),  # top-right
        (margin + inner_m + 30, y0 + box_h - inner_m - 30),  # bottom-left
        (w - margin - inner_m - 30, y0 + box_h - inner_m - 30),  # bottom-right
    ]
    for i, (cx, cy) in enumerate(corners):
        sx = 1 if i % 2 == 0 else -1
        sy = 1 if i < 2 else -1
        draw.rectangle([cx, cy, cx + sx * bracket_len, cy + bracket_w * sy], fill=GREEN)
        draw.rectangle([cx, cy, cx + bracket_w * sx, cy + sy * bracket_len], fill=GREEN)

    # Chinese text sample in viewfinder
    cjk = find_cjk_font(48)
    sample = "你好世界"
    tw2, th2 = text_size(draw, sample, cjk)
    draw.text(((w - tw2)//2, y0 + box_h//2 - th2//2), sample, fill=DARK_TEXT, font=cjk)

    # Highlighted word box
    hw = tw2 // 4
    hx = (w - tw2) // 2
    hy = y0 + box_h // 2 - th2 // 2 - 6
    draw.rectangle([hx - 4, hy, hx + hw + 4, hy + th2 + 12], outline=GREEN, width=3)


def detail_dictionary(draw, img, w, start_y):
    """Show mock dictionary entries."""
    margin = 100
    y = start_y + 40
    cjk = find_cjk_font(42)
    regular = find_font(28, bold=False)
    bold = find_font(30, bold=True)

    entries = [
        ("你好", "nǐ hǎo", "hello"),
        ("学习", "xué xí", "to study, to learn"),
        ("世界", "shì jiè", "world"),
    ]
    for char, pinyin, meaning in entries:
        # Card background
        card_h = 130
        draw_rounded_rect(draw, (margin, y, w - margin, y + card_h), 16, WHITE)
        # Left accent bar
        draw.rectangle([margin, y + 20, margin + 6, y + card_h - 20], fill=GREEN)
        # Chinese character
        draw.text((margin + 30, y + 20), char, fill=DARK_TEXT, font=cjk)
        # Pinyin
        draw.text((margin + 160, y + 22), pinyin, fill=GREEN, font=regular)
        # English
        draw.text((margin + 160, y + 65), meaning, fill=MID_TEXT, font=regular)
        y += card_h + 20


def detail_flashcard(draw, img, w, start_y):
    """Show a mock flashcard."""
    y = start_y + 50
    card_w, card_h = 600, 350
    cx = w // 2
    # Card shadow
    draw_rounded_rect(draw, (cx - card_w//2 + 6, y + 6, cx + card_w//2 + 6, y + card_h + 6), 24, (200, 210, 200))
    # Card
    draw_rounded_rect(draw, (cx - card_w//2, y, cx + card_w//2, y + card_h), 24, WHITE)
    # Top colored strip
    draw.rectangle([cx - card_w//2 + 24, y, cx + card_w//2 - 24, y + 6], fill=GREEN)

    # Big character
    cjk_big = find_cjk_font(96)
    char = "学"
    tw3, th3 = text_size(draw, char, cjk_big)
    draw.text(((w - tw3)//2, y + 60), char, fill=DARK_TEXT, font=cjk_big)

    # Tap to flip hint
    hint_font = find_font(26, bold=False)
    hint = "Tap to flip"
    hw2, hh2 = text_size(draw, hint, hint_font)
    draw.text(((w - hw2)//2, y + card_h - 60), hint, fill=MID_TEXT, font=hint_font)

    # Progress dots below card
    dot_y2 = y + card_h + 50
    for i in range(5):
        dx = cx - 80 + i * 40
        c = GREEN if i < 3 else LIGHT_GRAY
        draw.ellipse([dx - 6, dot_y2 - 6, dx + 6, dot_y2 + 6], fill=c)

    # "3 of 5" label
    prog_font = find_font(24, bold=False)
    draw.text((cx - 25, dot_y2 + 20), "3 of 5", fill=MID_TEXT, font=prog_font)


def detail_progress(draw, img, w, start_y):
    """Show mock progress stats."""
    y = start_y + 40
    margin = 100
    bold = find_font(32, bold=True)
    regular = find_font(24, bold=False)
    big_num = find_font(56, bold=True)

    stats = [
        ("156", "Words Learned"),
        ("12", "Day Streak"),
        ("85%", "Accuracy"),
    ]
    card_w_each = (w - 2 * margin - 40) // 3
    for i, (num, label) in enumerate(stats):
        cx = margin + i * (card_w_each + 20) + card_w_each // 2
        card_x0 = margin + i * (card_w_each + 20)
        # Card
        draw_rounded_rect(draw, (card_x0, y, card_x0 + card_w_each, y + 160), 16, WHITE)
        # Number
        nw, nh = text_size(draw, num, big_num)
        draw.text((cx - nw//2, y + 20), num, fill=GREEN, font=big_num)
        # Label
        lw, lh = text_size(draw, label, regular)
        draw.text((cx - lw//2, y + 95), label, fill=MID_TEXT, font=regular)

    # Weekly chart area below
    chart_y = y + 220
    draw_rounded_rect(draw, (margin, chart_y, w - margin, chart_y + 300), 16, WHITE)
    # Title
    draw.text((margin + 30, chart_y + 20), "This Week", fill=DARK_TEXT, font=bold)

    # Bar chart
    days = ["M", "T", "W", "T", "F", "S", "S"]
    values = [0.5, 0.7, 0.4, 0.9, 0.6, 0.3, 0.8]
    chart_margin = 60
    chart_w = (w - 2 * margin - 2 * chart_margin)
    bar_w_unit = chart_w // len(days)
    chart_base = chart_y + 260
    chart_top = chart_y + 70
    chart_range = chart_base - chart_top

    day_font = find_font(22, bold=False)
    for i, (day, val) in enumerate(zip(days, values)):
        bx = margin + chart_margin + i * bar_w_unit + bar_w_unit // 4
        bw2 = bar_w_unit // 2
        bh = int(chart_range * val)
        bar_col = GREEN if i < 5 else LIGHT_GREEN
        draw_rounded_rect(draw, (bx, chart_base - bh, bx + bw2, chart_base), bw2 // 4, bar_col)
        # Day label
        dw2, dh2 = text_size(draw, day, day_font)
        draw.text((bx + bw2//2 - dw2//2, chart_base + 8), day, fill=MID_TEXT, font=day_font)


# ===================================================
# Generate all images
# ===================================================
print("Generating Google Play Store graphics...")
print(f"Output directory: {OUT}")
print()

create_feature_graphic()

screenshots = [
    ("screenshot_1.png", "Snap any Chinese text", "Point your camera at any Chinese text\nand instantly recognize characters", draw_camera_icon, detail_camera),
    ("screenshot_2.png", "Instant vocabulary lookup", "Get definitions, pinyin, and examples\nfor every word you discover", draw_book_icon, detail_dictionary),
    ("screenshot_3.png", "Smart flashcards", "Review words with spaced repetition\nto build lasting memory", draw_flashcard_icon, detail_flashcard),
    ("screenshot_4.png", "Track your progress", "See your learning stats and\nstay motivated every day", draw_chart_icon, detail_progress),
]

for fname, headline, desc, icon_fn, detail_fn in screenshots:
    create_screenshot(fname, headline, desc, icon_fn, detail_fn)

print()
print("All graphics generated successfully!")
print(f"Files saved to: {OUT}")
for f in sorted(os.listdir(OUT)):
    if f.endswith(".png"):
        size = os.path.getsize(os.path.join(OUT, f))
        img = Image.open(os.path.join(OUT, f))
        print(f"  {f}: {img.size[0]}x{img.size[1]} ({size // 1024} KB)")
