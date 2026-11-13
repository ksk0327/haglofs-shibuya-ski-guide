# -*- coding: utf-8 -*-
"""Generates every product page, every category page, and the category-grid
block of index.html from one data source (PRODUCTS, below).

Architecture (2026-11-12 multi-category rework):
  - CATEGORIES: the top-level product types shown as tiles on index.html
    (Jackets, Pants, Base Layers, Mid Layers, Backpacks & Bags). A category
    with zero products in it renders as a disabled "Coming soon" tile.
  - AXIS_SETS: the 5 fit-chart axis labels used for each category's radar
    chart. Jackets keep the original Resort/Powder/Off-piste/Touring/Cold
    axes; other categories get axes suited to that product type. These are
    first-draft proposals — easy to rename later in one place.
  - PRODUCTS: one dict per product. Each has `category` (must match a
    CATEGORIES slug), `gender` ("mens" or "womens"), and `activity_tags`
    (e.g. ["Ski"]) in addition to all the copy/spec/size/color/image fields
    used before. Adding a new product is just appending one dict here.

What gets (re)generated every run:
  - products/<slug>.html for every product in PRODUCTS
  - assets/img/radar-<slug>.svg for every product (axes from its category)
  - category/<slug>.html for every category in CATEGORIES (a Men's/Women's
    tab view of that category's products — pure CSS tabs, no JS — plus a
    quick-compare table when the category defines one)
  - the block between <!-- CATEGORY_GRID:START/END --> markers in
    index.html (the category tile grid). The rest of index.html — intro,
    tax-free notice, payment methods, footer — is still hand-maintained.

Run with: python3 tools/build_products.py
"""
import math
import os
import re

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT_DIR = os.path.join(BASE_DIR, "products")
CATEGORY_DIR = os.path.join(BASE_DIR, "category")
IMG_DIR = os.path.join(BASE_DIR, "assets", "img")
INDEX_PATH = os.path.join(BASE_DIR, "index.html")

# ---------------------------------------------------------------
# Categories (top-level product types) and their fit-chart axes.
# A category with no products yet still appears on index.html as a
# disabled "Coming soon" tile, so the intended final site shape is visible
# right away — add products to PRODUCTS below and it activates on its own.
# ---------------------------------------------------------------
CATEGORIES = [
    {
        "slug": "jackets",
        "label": "Jackets",
        "blurb": "Shell & insulated jackets for resort, backcountry and touring.",
    },
    {
        "slug": "pants",
        "label": "Pants",
        "blurb": "Ski and outdoor pants.",
    },
    {
        "slug": "base-layers",
        "label": "Base Layers",
        "blurb": "Next-to-skin thermal layers.",
    },
    {
        "slug": "mid-layers",
        "label": "Mid Layers",
        "blurb": "Fleece and insulated layers for extra warmth.",
    },
    {
        "slug": "backpacks",
        "label": "Backpacks & Bags",
        "blurb": "Day packs and touring packs.",
    },
]
CATEGORY_BY_SLUG = {c["slug"]: c for c in CATEGORIES}

# First-draft axis proposals for categories that don't have products yet —
# easy to rename in one place once real items are being added.
AXIS_SETS = {
    "jackets": ["Resort", "Powder", "Off-piste", "Touring", "Cold"],
    "pants": ["Resort", "Powder", "Off-piste", "Touring", "Cold"],
    "base-layers": ["Warmth", "Breathability", "Moisture-wicking", "Stretch", "Odor control"],
    "mid-layers": ["Warmth", "Breathability", "Packability", "Durability", "Versatility"],
    "backpacks": ["Capacity", "Load comfort", "Durability", "Weight", "Organization"],
}

# Quick-compare table column headers per category. Only categories listed
# here get a compare table on their category page; a category with no
# entry here (or with no products) simply skips that section.
COMPARE_HEADERS = {
    "jackets": ["Jacket", "Shell / Insulation", "Waterproof", "Breathability (RET)", "Weight (L)", "Best for"],
    "pants": ["Pant / Bib", "Shell / Insulation", "Waterproof", "Breathability (RET)", "Weight (L)", "Best for"],
}

# ---------------------------------------------------------------
# Fit-chart radar SVG generator. Axes are passed in per call so the same
# drawing code works for every category's axis set.
# ---------------------------------------------------------------
RADAR_ACCENT = "#b0251f"
RADAR_MUTED = "#6b6b6b"
RADAR_LINE = "#e4e1dc"
RADAR_SIZE = 280
RADAR_CX = RADAR_CY = RADAR_SIZE / 2
RADAR_R = 58
RADAR_LABEL_R = RADAR_R + 32

def _radar_point(i, value, num_axes, max_value=5):
    angle = -math.pi / 2 + i * (2 * math.pi / num_axes)
    r = (value / max_value) * RADAR_R
    return RADAR_CX + r * math.cos(angle), RADAR_CY + r * math.sin(angle)

def _radar_label_point(i, num_axes):
    angle = -math.pi / 2 + i * (2 * math.pi / num_axes)
    return RADAR_CX + RADAR_LABEL_R * math.cos(angle), RADAR_CY + RADAR_LABEL_R * math.sin(angle)

def radar_svg(slug, values, axes):
    n = len(axes)
    rings = []
    for ring_v in [1, 2, 3, 4, 5]:
        pts = [_radar_point(i, ring_v, n) for i in range(n)]
        pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        rings.append(f'<polygon points="{pts_str}" fill="none" stroke="{RADAR_LINE}" stroke-width="1"/>')
    spokes = []
    for i in range(n):
        x, y = _radar_point(i, 5, n)
        spokes.append(f'<line x1="{RADAR_CX}" y1="{RADAR_CY}" x2="{x:.1f}" y2="{y:.1f}" stroke="{RADAR_LINE}" stroke-width="1"/>')
    data_pts = [_radar_point(i, v, n) for i, v in enumerate(values)]
    data_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in data_pts)
    dots = []
    for (x, y) in data_pts:
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{RADAR_ACCENT}"/>')
    labels = []
    for i, name in enumerate(axes):
        x, y = _radar_label_point(i, n)
        anchor = "middle"
        if x < RADAR_CX - 12: anchor = "end"
        elif x > RADAR_CX + 12: anchor = "start"
        dy = 0
        if y < RADAR_CY - 12: dy = -2
        elif y > RADAR_CY + 12: dy = 9
        labels.append(f'<text x="{x:.1f}" y="{y+dy:.1f}" text-anchor="{anchor}" font-size="10.5" fill="{RADAR_MUTED}" font-family="Helvetica Neue, Arial, sans-serif">{name}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {RADAR_SIZE} {RADAR_SIZE}" role="img" aria-label="{slug} fit chart">
  {''.join(rings)}
  {''.join(spokes)}
  <polygon points="{data_str}" fill="{RADAR_ACCENT}" fill-opacity="0.10" stroke="{RADAR_ACCENT}" stroke-width="2.2"/>
  {''.join(dots)}
  {''.join(labels)}
</svg>'''

def write_radar_svg(slug, values, axes):
    out_path = os.path.join(IMG_DIR, f"radar-{slug}.svg")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(radar_svg(slug, values, axes))

PLACEHOLDER_ICON = '''<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><path d="M4 20V9l8-5 8 5v11M4 20h16M9 20v-6h6v6"/></svg>'''

def gallery_html(labels):
    slides = []
    for label in labels:
        slides.append(f'''      <div class="slide"><div class="slide-inner">{PLACEHOLDER_ICON}<div class="ph-label">Photo placeholder<br>{label}</div></div></div>''')
    return '\n'.join(slides)

def gallery_images_html(images):
    """images: list of dicts with keys src, alt, caption."""
    slides = []
    for img in images:
        slides.append(
            '      <div class="slide slide-photo">'
            f'<img src="{img["src"]}" alt="{img["alt"]}">'
            f'<div class="slide-caption">{img["caption"]}</div>'
            '</div>'
        )
    return '\n'.join(slides)

def kf_html(items):
    out = []
    for label, value in items:
        out.append(f'''      <div class="kf"><div class="kf-label">{label}</div><div class="kf-value">{value}</div></div>''')
    return '\n'.join(out)

def feature_list_html(items):
    return '\n'.join(f'      <li>{i}</li>' for i in items)

def specs_table_html(rows):
    out = []
    for label, value in rows:
        out.append(f'      <tr><th>{label}</th><td>{value}</td></tr>')
    return '\n'.join(out)

def size_table_html(headers, rows):
    head = ''.join(f'<th>{h}</th>' for h in headers)
    body = []
    for row in rows:
        cells = ''.join(f'<td>{c}</td>' for c in row)
        body.append(f'          <tr>{cells}</tr>')
    return head, '\n'.join(body)

def chips_html(items):
    return '\n'.join(f'      <span class="chip">{i}</span>' for i in items)

def activity_pills_html(tags):
    if not tags:
        return ''
    return '<div class="activity-tags">' + ''.join(f'<span class="activity-pill">{t}</span>' for t in tags) + '</div>'

# Approximate swatch colors for named colorways (for the small color dot next
# to each chip — not exact pantone matches, just enough to tell them apart
# at a glance without scrolling back up to the photos).
COLOR_HEX = {
    "true black": "#1a1a1a",
    "black": "#1a1a1a",
    "purple night": "#3a2c4d",
    "evening": "#2b3a55",
    "chlorophyll green": "#4c7a3f",
    "seaweed green": "#33502f",
    "dew green": "#8aa98a",
    "teak brown": "#6b4a35",
    "woodland": "#4a4a33",
    "chalk beige": "#cdc3b0",
    "tarn blue": "#466a86",
    "turn blue": "#466a86",
    "northern blue": "#1f3a63",
}

def _swatch_color(token):
    return COLOR_HEX.get(token.strip().lower(), "#bbbbbb")

def color_chip_html(name):
    parts = [p.strip() for p in name.split("/")]
    if len(parts) == 2:
        c1, c2 = _swatch_color(parts[0]), _swatch_color(parts[1])
        swatch = f'<span class="chip-swatch" style="background: linear-gradient(135deg, {c1} 50%, {c2} 50%);"></span>'
    else:
        swatch = f'<span class="chip-swatch" style="background: {_swatch_color(parts[0])};"></span>'
    return f'      <span class="chip chip-color">{swatch}{name}</span>'

def color_chips_html(items):
    return '\n'.join(color_chip_html(i) for i in items)

def related_html(items, current_slug):
    out = []
    for p in items:
        if p["slug"] == current_slug:
            continue
        out.append(f'''    <a href="{p['slug']}.html"><span class="rel-name">{p['card_name']}</span><span class="rel-spec">{p['mini_specs'][-1] if p['mini_specs'] else ''}</span></a>''')
    return '\n'.join(out)

# ---------------------------------------------------------------
# Product data. One dict per product — this is the single source of truth
# for its product page, its fit-chart SVG, its card on its category page,
# and its row in that category's quick-compare table (if any).
# ---------------------------------------------------------------
PRODUCTS = [
    dict(
        slug="vassi-gtx-pro-ii",
        category="jackets", subcategory="shell", gender="mens",
        activity_tags=["Ski"],
        name_en="Vassi GTX Pro II Jacket Men",
        name_jp="ヴァッシ ゴアテックス プロ II ジャケット〔メンズ〕",
        model_number="608577",
        price="¥126,500",
        price_note=" (tax included) — final total confirmed at checkout",
        meta_desc="Haglöfs Vassi GTX Pro II freeride ski jacket — specs, features and size chart for international customers.",
        gallery_labels=["Front", "Back / hood detail", "Worn, on mountain"],
        kf_items=[
            ("Waterproof", "28,000mm"),
            ("Breathability", "RET 13.5"),
            ("Weight (L)", "665g"),
            ("Hood", "Helmet-compatible"),
        ],
        about=("The top-of-line jacket in Haglöfs' Vassi freeride series, built for skiers who split their time between "
               "resort laps and backcountry lines. A 3-layer GORE-TEX Pro shell — Haglöfs' most protective, most "
               "breathable waterproof fabric — handles deep snow, high wind and long days without overheating."),
        features=[
            "Helmet-compatible hood, adjustable from two points",
            "Chin guard with laser-cut ventilation flap and soft fleece lining",
            "Angled 2-way pit-zip ventilation that stays clear of a backpack's hip belt",
            "2 hand pockets with gusseted zips, large enough for gloved hands",
            "2 zippered chest pockets",
            "Goggle wipe built into a chest pocket",
            "Ski-pass pocket on the left sleeve",
            "Open mesh inner pocket for small items",
            "Stretch snow skirt with rubber grip, keeps powder out",
            "Articulated elbows for a freer range of motion",
            "Wide velcro cuff adjusters",
            "Drawcord hem",
            "RECCO® reflector for avalanche rescue search",
        ],
        specs_rows=[
            ("Shell fabric", "3-layer GORE-TEX Pro, 100% recycled polyamide, 70 denier (denier = fabric thickness; higher = tougher, more durable)"),
            ("Waterproofness", "28,000mm"),
            ("Breathability (RET)", "13.5 — lower RET = more breathable"),
            ("Weight", "665g (men's size L)"),
        ],
        size_headers=["Size", "Chest", "Waist width", "Hem width", "Body length", "Sleeve length"],
        size_rows=[
            ["S", "121.5", "110.0", "112.0", "83.0", "84.0"],
            ["M", "127.5", "116.0", "118.0", "84.0", "85.5"],
            ["L", "133.5", "122.0", "124.0", "85.0", "87.5"],
            ["XL", "139.5", "128.0", "130.0", "86.0", "89.0"],
        ],
        size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value.",
        colors=["Purple Night / Evening", "True Black / Chlorophyll Green"],
        sizes=["S", "M", "L", "XL"],
        best_for="Freeride & backcountry skiing — deep snow, long days, technical terrain",
        images=[
            {"src": "../assets/img/vassi-gtx-pro-ii-purple-night-evening-front.webp",
             "alt": "Vassi GTX Pro II Jacket, Purple Night / Evening colorway, front",
             "caption": "Purple Night / Evening — Front"},
            {"src": "../assets/img/vassi-gtx-pro-ii-purple-night-evening-back.webp",
             "alt": "Vassi GTX Pro II Jacket, Purple Night / Evening colorway, back",
             "caption": "Purple Night / Evening — Back"},
            {"src": "../assets/img/vassi-gtx-pro-ii-true-black-chlorophyll-green-front.webp",
             "alt": "Vassi GTX Pro II Jacket, True Black / Chlorophyll Green colorway, front",
             "caption": "True Black / Chlorophyll Green — Front"},
            {"src": "../assets/img/vassi-gtx-pro-ii-true-black-chlorophyll-green-back.webp",
             "alt": "Vassi GTX Pro II Jacket, True Black / Chlorophyll Green colorway, back",
             "caption": "True Black / Chlorophyll Green — Back"},
        ],
        card_tag="Freeride Shell",
        card_name="Vassi GTX Pro II Jacket",
        mini_specs=["GORE-TEX Pro", "28,000mm", "665g"],
        thumb_src="assets/img/vassi-gtx-pro-ii-purple-night-evening-front.webp",
        thumb_alt="Vassi GTX Pro II Jacket",
        radar_scores=[3, 5, 5, 4, 2],
        radar_alt="Vassi GTX Pro II fit chart: strongest for powder and off-piste",
        compare=dict(shell_insulation="GORE-TEX Pro 3L / Shell only", waterproof="28,000mm",
                     breathability="13.5", weight="665g", best_for_short="Freeride & backcountry"),
    ),
    dict(
        slug="vassi-gtx-ii",
        category="jackets", subcategory="shell", gender="mens",
        activity_tags=["Ski"],
        name_en="Vassi GTX II Jacket Men",
        name_jp="ヴァッシ ゴアテックス II ジャケット〔メンズ〕",
        model_number="608574",
        price="¥93,500",
        price_note=" (tax included) — final total confirmed at checkout",
        meta_desc="Haglöfs Vassi GTX II freeride ski jacket — specs, features and size chart for international customers.",
        gallery_labels=["Front", "Back / hood detail", "Worn, on mountain"],
        kf_items=[
            ("Waterproof", "28,000mm"),
            ("Breathability", "RET 20"),
            ("Weight (L)", "720g"),
            ("Hood", "Helmet-compatible"),
        ],
        about=("The everyday version of Haglöfs' Vassi freeride series. A 3-layer GORE-TEX shell gives the same "
               "waterproof, windproof protection as the Pro II at a more accessible price, in a slightly heavier, "
               "more durable 75-denier fabric — a strong all-round choice for resort and backcountry skiing alike."),
        features=[
            "Large helmet-compatible hood, adjustable from two points",
            "Chin guard with laser-cut ventilation flap and soft fleece lining",
            "Angled 2-way pit-zip ventilation that stays clear of a backpack",
            "2 hand pockets with gusseted zips",
            "1 zippered chest pocket",
            "Goggle wipe",
            "Ski-pass pocket on the left upper sleeve",
            "Open mesh inner pocket",
            "Stretch powder skirt with rubber grip",
            "Articulated elbows",
            "Wide velcro cuff adjusters",
            "Drawcord hem",
            "RECCO® reflector — a built-in chip that helps rescuers locate you if buried in an avalanche",
        ],
        specs_rows=[
            ("Shell fabric", "3-layer GORE-TEX, 100% recycled polyester, 75 denier (denier = fabric thickness; higher = tougher, more durable)"),
            ("Membrane", "GORE-TEX ePE laminate (a 2-layer waterproof membrane)"),
            ("Waterproofness", "28,000mm"),
            ("Breathability (RET)", "20 — lower RET = more breathable; 20 is a solid everyday resort/freeride level"),
            ("Weight", "720g (men's size L)"),
        ],
        size_headers=["Size", "Chest", "Waist width", "Hem width", "Body length", "Sleeve length"],
        size_rows=[
            ["S", "118.0", "109.5", "111.5", "80.5", "83.5"],
            ["M", "124.0", "115.5", "117.5", "81.5", "85.0"],
            ["L", "130.0", "121.5", "123.5", "82.5", "87.0"],
            ["XL", "136.0", "127.5", "129.5", "83.5", "88.5"],
        ],
        size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value.",
        colors=["Purple Night", "Teak Brown / Woodland", "Dew Green", "Tarn Blue"],
        sizes=["S", "M", "L", "XL"],
        best_for="Everyday resort & freeride skiing — great all-round value",
        images=[
            {"src": "../assets/img/vassi-gtx-ii-dew-green-front.webp",
             "alt": "Vassi GTX II Jacket, Dew Green colorway, front",
             "caption": "Dew Green — Front"},
            {"src": "../assets/img/vassi-gtx-ii-dew-green-back.webp",
             "alt": "Vassi GTX II Jacket, Dew Green colorway, back",
             "caption": "Dew Green — Back"},
            {"src": "../assets/img/vassi-gtx-ii-purple-night-front.webp",
             "alt": "Vassi GTX II Jacket, Purple Night colorway, front",
             "caption": "Purple Night — Front"},
            {"src": "../assets/img/vassi-gtx-ii-purple-night-back.webp",
             "alt": "Vassi GTX II Jacket, Purple Night colorway, back",
             "caption": "Purple Night — Back"},
            {"src": "../assets/img/vassi-gtx-ii-tarn-blue-front.webp",
             "alt": "Vassi GTX II Jacket, Tarn Blue colorway, front",
             "caption": "Tarn Blue — Front"},
            {"src": "../assets/img/vassi-gtx-ii-tarn-blue-back.webp",
             "alt": "Vassi GTX II Jacket, Tarn Blue colorway, back",
             "caption": "Tarn Blue — Back"},
            {"src": "../assets/img/vassi-gtx-ii-teak-brown-woodland-front.webp",
             "alt": "Vassi GTX II Jacket, Teak Brown / Woodland colorway, front",
             "caption": "Teak Brown / Woodland — Front"},
            {"src": "../assets/img/vassi-gtx-ii-teak-brown-woodland-back.webp",
             "alt": "Vassi GTX II Jacket, Teak Brown / Woodland colorway, back",
             "caption": "Teak Brown / Woodland — Back"},
        ],
        card_tag="Freeride Shell",
        card_name="Vassi GTX II Jacket",
        mini_specs=["GORE-TEX", "28,000mm", "720g"],
        thumb_src="assets/img/vassi-gtx-ii-dew-green-front.webp",
        thumb_alt="Vassi GTX II Jacket",
        radar_scores=[3, 4, 4, 3, 3],
        radar_alt="Vassi GTX II fit chart: balanced, strongest for powder and off-piste",
        compare=dict(shell_insulation="GORE-TEX 3L / Shell only", waterproof="28,000mm",
                     breathability="20", weight="720g", best_for_short="Freeride, everyday value"),
    ),
    dict(
        slug="alper-proof",
        category="jackets", subcategory="shell", gender="mens",
        activity_tags=["Ski"],
        name_en="Alper Proof Jacket Men",
        name_jp="アルパー プルーフ ジャケット〔メンズ〕",
        model_number="607936",
        price="¥59,400",
        price_note=" (tax included) — final total confirmed at checkout",
        meta_desc="Haglöfs Alper Proof all-mountain ski jacket — specs, features and size chart for international customers.",
        gallery_labels=["Front", "Back / hood detail", "Worn, on mountain"],
        kf_items=[
            ("Waterproof", "20,000mm"),
            ("Breathability", "20,000 g/m²/24h"),
            ("Weight (L)", "670g"),
            ("Hood", "Helmet-compatible"),
        ],
        about=("New for Autumn/Winter, the Alper Proof is Haglöfs' value-focused all-mountain jacket — built with the "
               "brand's in-house PROOF™ Pro waterproof fabric so it covers the everyday ski-resort essentials "
               "(helmet-compatible hood, ventilation, powder skirt) without the price tag of a GORE-TEX shell."),
        features=[
            "Adjustable, helmet-compatible hood",
            "Zippered pit-zip ventilation",
            "2 zippered hand pockets, plus one large chest pocket",
            "Ski-pass pocket on the left upper sleeve",
            "Stretch snow skirt with rubber grip",
            "Adjustable drawcord hem",
            "2-way center-front Aquaguard® zip",
            "Wide velcro cuff adjusters",
        ],
        specs_rows=[
            ("Shell fabric", "3-layer PROOF™ Pro, 100% recycled polyester, 75 denier (denier = fabric thickness; higher = tougher, more durable)"),
            ("Waterproofness", "20,000mm"),
            ("Breathability", "20,000 g/m²/24h (higher number = more breathable; a solid everyday resort level)"),
            ("Weight", "670g (men's size L)"),
        ],
        size_headers=["Size", "Chest", "Waist width", "Hem width", "Body length", "Sleeve length"],
        size_rows=[
            ["S", "118.0", "109.0", "111.0", "80.5", "84.5"],
            ["M", "124.0", "115.0", "117.0", "81.5", "86.0"],
            ["L", "130.0", "121.0", "123.0", "82.5", "88.0"],
            ["XL", "136.0", "127.0", "129.0", "83.5", "89.5"],
        ],
        size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value.",
        colors=["Northern Blue / Tarn Blue", "Seaweed Green / Chlorophyll Green", "Teak Brown", "True Black"],
        sizes=["S", "M", "L", "XL"],
        best_for="All-mountain resort skiing — best value shell in this lineup",
        images=[
            {"src": "../assets/img/alper-proof-northern-blue-tarn-blue-front.webp",
             "alt": "Alper Proof Jacket, Northern Blue / Tarn Blue colorway, front",
             "caption": "Northern Blue / Tarn Blue — Front"},
            {"src": "../assets/img/alper-proof-northern-blue-tarn-blue-back.webp",
             "alt": "Alper Proof Jacket, Northern Blue / Tarn Blue colorway, back",
             "caption": "Northern Blue / Tarn Blue — Back"},
            {"src": "../assets/img/alper-proof-seaweed-green-chlorophyll-green-front.webp",
             "alt": "Alper Proof Jacket, Seaweed Green / Chlorophyll Green colorway, front",
             "caption": "Seaweed Green / Chlorophyll Green — Front"},
            {"src": "../assets/img/alper-proof-seaweed-green-chlorophyll-green-back.webp",
             "alt": "Alper Proof Jacket, Seaweed Green / Chlorophyll Green colorway, back",
             "caption": "Seaweed Green / Chlorophyll Green — Back"},
            {"src": "../assets/img/alper-proof-teak-brown-front.webp",
             "alt": "Alper Proof Jacket, Teak Brown colorway, front",
             "caption": "Teak Brown — Front"},
            {"src": "../assets/img/alper-proof-teak-brown-back.webp",
             "alt": "Alper Proof Jacket, Teak Brown colorway, back",
             "caption": "Teak Brown — Back"},
            {"src": "../assets/img/alper-proof-true-black-front.webp",
             "alt": "Alper Proof Jacket, True Black colorway, front",
             "caption": "True Black — Front"},
            {"src": "../assets/img/alper-proof-true-black-back.webp",
             "alt": "Alper Proof Jacket, True Black colorway, back",
             "caption": "True Black — Back"},
        ],
        card_tag="All-Mountain Shell",
        card_name="Alper Proof Jacket",
        mini_specs=["PROOF™ Pro", "20,000mm", "670g"],
        thumb_src="assets/img/alper-proof-northern-blue-tarn-blue-front.webp",
        thumb_alt="Alper Proof Jacket",
        radar_scores=[3, 3, 3, 3, 3],
        radar_alt="Alper Proof fit chart: evenly balanced all-around",
        compare=dict(shell_insulation="PROOF™ Pro 3L / Shell only", waterproof="20,000mm",
                     breathability="— (breathability 20,000g/m²/24h)", weight="670g", best_for_short="All-mountain, best value"),
    ),
    dict(
        slug="latnja-gtx-insulated",
        category="jackets", subcategory="insulated", gender="mens",
        activity_tags=["Ski"],
        name_en="Latnja GTX Insulated Jacket Men",
        name_jp="ラティニャ ゴアテックス インシュレイテッド ジャケット〔メンズ〕",
        model_number="607469",
        price="¥69,300",
        price_note=" (tax included) — final total confirmed at checkout",
        meta_desc="Haglöfs Latnja GTX Insulated ski jacket — specs, features and size chart for international customers.",
        gallery_labels=["Front", "Back / hood detail", "Worn, on mountain"],
        kf_items=[
            ("Waterproof", "28,000mm"),
            ("Breathability", "RET > 13"),
            ("Weight (L)", "860g"),
            ("Hood", "Helmet-compatible, 2-way adjustable"),
        ],
        about=("Inspired by the Vassi freeride series, the Latnja adds built-in insulation for genuinely cold days — "
               "resort skiing, lift-served touring, or anywhere you'd rather not layer a separate midlayer underneath. "
               "A waterproof GORE-TEX ePE 2-layer shell is paired with a lightweight Mimic SILVER fill, mapped across "
               "three zones so warmth is added where you need it most without overheating on the move."),
        features=[
            "2-way adjustable, helmet-compatible hood",
            "Snow skirt with rubber grip to seal out powder",
            "Stand collar with a removable brushed chin guard, plus zippered ventilation",
            "Diagonally placed 2-way zip ventilation",
            "2 zippered hand pockets, 1 large chest pocket, 1 ski-pass sleeve pocket",
            "Stretch wrist gaiters under adjustable velcro cuffs",
            "Adjustable drawcord hem",
            "RECCO® reflector — a built-in chip that helps rescuers locate you if buried in an avalanche",
        ],
        specs_rows=[
            ("Shell fabric", "75 denier, 100% recycled polyester / GORE-TEX® 2L ePE (denier = fabric thickness; ePE = a 2-layer waterproof membrane)"),
            ("Lining", "100% recycled polyester"),
            ("Insulation", "100% recycled polyester / Mimic SILVER, body-mapped across 3 zones"),
            ("Waterproofness", "28,000mm"),
            ("Breathability (RET)", "RET > 13 — lower RET = more breathable; this is a warm, cold-weather level"),
            ("Weight", "860g (men's size L)"),
        ],
        size_headers=["Size", "Chest", "Waist width", "Shoulder width", "Body length", "Sleeve length"],
        size_rows=[
            ["S", "118.0", "109.0", "48.5", "81.0", "84.0"],
            ["M", "124.0", "115.0", "50.5", "82.0", "85.5"],
            ["L", "130.0", "121.0", "52.5", "83.0", "87.5"],
            ["XL", "136.0", "127.0", "54.5", "84.0", "89.0"],
        ],
        size_note="All measurements in cm, garment laid flat (external measurements). Multiply by 0.39 for an approximate inch value.",
        colors=["Chlorophyll Green", "Chalk Beige", "Tarn Blue", "True Black"],
        sizes=["S", "M", "L", "XL"],
        best_for="Cold resort days & lift-served touring — when you don't want to layer a midlayer",
        images=[
            {"src": "../assets/img/latnja-gtx-insulated-chalk-beige-front.webp",
             "alt": "Latnja GTX Insulated Jacket, Chalk Beige colorway, front",
             "caption": "Chalk Beige — Front"},
            {"src": "../assets/img/latnja-gtx-insulated-chalk-beige-back.webp",
             "alt": "Latnja GTX Insulated Jacket, Chalk Beige colorway, back",
             "caption": "Chalk Beige — Back"},
            {"src": "../assets/img/latnja-gtx-insulated-chlorophyll-green-front.webp",
             "alt": "Latnja GTX Insulated Jacket, Chlorophyll Green colorway, front",
             "caption": "Chlorophyll Green — Front"},
            {"src": "../assets/img/latnja-gtx-insulated-chlorophyll-green-back.webp",
             "alt": "Latnja GTX Insulated Jacket, Chlorophyll Green colorway, back",
             "caption": "Chlorophyll Green — Back"},
            {"src": "../assets/img/latnja-gtx-insulated-true-black-front.webp",
             "alt": "Latnja GTX Insulated Jacket, True Black colorway, front",
             "caption": "True Black — Front"},
            {"src": "../assets/img/latnja-gtx-insulated-true-black-back.webp",
             "alt": "Latnja GTX Insulated Jacket, True Black colorway, back",
             "caption": "True Black — Back"},
            {"src": "../assets/img/latnja-gtx-insulated-turn-blue-front.webp",
             "alt": "Latnja GTX Insulated Jacket, Tarn Blue colorway, front",
             "caption": "Tarn Blue — Front"},
            {"src": "../assets/img/latnja-gtx-insulated-turn-blue-back.webp",
             "alt": "Latnja GTX Insulated Jacket, Tarn Blue colorway, back",
             "caption": "Tarn Blue — Back"},
        ],
        card_tag="Insulated",
        card_name="Latnja GTX Insulated Jacket",
        mini_specs=["GORE-TEX 2L", "28,000mm", "860g"],
        thumb_src="assets/img/latnja-gtx-insulated-chalk-beige-front.webp",
        thumb_alt="Latnja GTX Insulated Jacket",
        radar_scores=[5, 2, 1, 2, 5],
        radar_alt="Latnja GTX Insulated fit chart: strongest for resort skiing and cold weather",
        compare=dict(shell_insulation="GORE-TEX ePE 2L / Insulated (3-zone mapped fill)", waterproof="28,000mm",
                     breathability="> 13", weight="860g", best_for_short="Cold-weather resort & touring"),
    ),
    dict(
        slug="nallo-touring-gtx",
        category="jackets", subcategory="shell", gender="mens",
        activity_tags=["Ski", "Touring"],
        name_en="Nallo Touring GTX Jacket Men",
        name_jp="ナロ ツーリング ゴアテックス ジャケット〔メンズ〕",
        model_number="608333",
        price="¥97,900",
        price_note=" (tax included) — final total confirmed at checkout",
        meta_desc="Haglöfs Nallo Touring GTX ski touring jacket — specs, features and size chart for international customers.",
        gallery_labels=["Front", "Back / hood detail", "Worn, touring"],
        kf_items=[
            ("Waterproof", "28,000mm"),
            ("Breathability", "RET 13"),
            ("Weight (L)", "407g — lightest in series"),
            ("Hood", "Helmet-compatible"),
        ],
        about=("Built for ski touring rather than the lift line, the Nallo Touring GTX is the lightest jacket in this "
               "lineup at just 407g. An angled front zip keeps a midlayer pocket reachable even with a pack on, and it's "
               "the first snow jacket from Haglöfs to include Twiceme® safety technology, which shares medical and "
               "location information in an emergency via NFC."),
        features=[
            "Reflective brand logo for visibility",
            "Adjustable, helmet-compatible hood with laminated brim",
            "Angled front ventilation",
            "Large zippered chest pocket with an internal mesh pocket for a ski pass",
            "2-way center-front zip",
            "Internal pocket sized for climbing skins",
            "Articulated sleeves for freedom of movement",
            "Adjustable cuffs and hem",
            "Twiceme® technology — NFC tag shares medical/location info with first responders",
        ],
        specs_rows=[
            ("Face fabric", "100% recycled polyamide, 30 denier, 3-layer GORE-TEX ripstop (denier = fabric thickness; higher = tougher, more durable)"),
            ("Lining", "100% polyamide"),
            ("Pocket mesh", "95% polyamide, 5% polyurethane"),
            ("Waterproofness", "28,000mm"),
            ("Breathability (RET)", "13 — lower RET = more breathable; this is a highly breathable, touring-friendly level"),
            ("Weight", "407g (men's size L)"),
        ],
        size_headers=["Size", "Chest", "Hem width", "Waist", "Body length", "Sleeve length"],
        size_rows=[
            ["S", "118.0", "112.0", "112.0", "77.5", "83.5"],
            ["M", "124.0", "118.0", "118.0", "78.5", "85.0"],
            ["L", "130.0", "124.0", "124.0", "79.5", "86.5"],
            ["XL", "136.0", "130.0", "130.0", "80.5", "88.5"],
        ],
        size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value.",
        colors=["Chlorophyll Green", "Chalk Beige"],
        sizes=["S", "M", "L", "XL"],
        best_for="Ski touring & uphill travel — lightest option in this lineup",
        images=[
            {"src": "../assets/img/nallo-touring-gtx-chalk-beige-front.webp",
             "alt": "Nallo Touring GTX Jacket, Chalk Beige colorway, front",
             "caption": "Chalk Beige — Front"},
            {"src": "../assets/img/nallo-touring-gtx-chalk-beige-back.webp",
             "alt": "Nallo Touring GTX Jacket, Chalk Beige colorway, back",
             "caption": "Chalk Beige — Back"},
            {"src": "../assets/img/nallo-touring-gtx-chlorophyll-green-front.webp",
             "alt": "Nallo Touring GTX Jacket, Chlorophyll Green colorway, front",
             "caption": "Chlorophyll Green — Front"},
            {"src": "../assets/img/nallo-touring-gtx-chlorophyll-green-back.webp",
             "alt": "Nallo Touring GTX Jacket, Chlorophyll Green colorway, back",
             "caption": "Chlorophyll Green — Back"},
        ],
        card_tag="Ski Touring Shell",
        card_name="Nallo Touring GTX Jacket",
        mini_specs=["GORE-TEX", "28,000mm", "407g"],
        thumb_src="assets/img/nallo-touring-gtx-chalk-beige-front.webp",
        thumb_alt="Nallo Touring GTX Jacket",
        radar_scores=[3, 3, 4, 5, 1],
        radar_alt="Nallo Touring GTX fit chart: strongest for touring, also strong off-piste",
        compare=dict(shell_insulation="GORE-TEX 3L ripstop / Shell only", waterproof="28,000mm",
                     breathability="13", weight="407g", best_for_short="Ski touring, lightest option"),
    ),

    # -----------------------------------------------------------
    # Ski pants (men's) — added 2026-11-13. DRAFT: sourced from UPLND
    # reference pages, not yet confirmed against the physical in-store
    # tags. See README.md item 23 before treating any of this 5 as final.
    # -----------------------------------------------------------
    dict(
        slug="vassi-gtx-pro-ii-bib",
        category="pants", subcategory="shell", gender="mens",
        activity_tags=["Ski"],
        name_en="Vassi GTX Pro II Bib Men",
        name_jp="ヴァッシ ゴアテックス プロ II ビブ〔メンズ〕",
        model_number="608576",
        price="¥99,000",
        price_note=" (tax included) — final total confirmed at checkout",
        meta_desc="Haglöfs Vassi GTX Pro II freeride ski bib — specs, features and size chart for international customers.",
        gallery_labels=["Front", "Back", "Worn, on mountain"],
        kf_items=[
            ("Waterproof", "28,000mm"),
            ("Breathability", "RET 13.5"),
            ("Weight (L)", "680g"),
            ("Style", "Bib"),
        ],
        about=("The bib version of Haglöfs' top-of-line Vassi freeride series, for skiers who want maximum snow "
               "protection and no gap at the waist. The same 3-layer GORE-TEX Pro shell as the Pro II jacket, with "
               "stretch cross-back suspenders and stretch side panels so it moves with you on technical terrain."),
        features=[
            "Bib design with stretch cross-back suspenders",
            "Stretch upper side panels",
            "2 zippered chest pockets",
            "2 zippered thigh pockets",
            "2-way zippered thigh vents",
            "Long zippered leg vents with adjustable, rubber-grip gaiters",
            "Articulated (3D-cut) knees",
            "Edge guards",
            "RECCO® reflector for avalanche rescue search",
        ],
        specs_rows=[
            ("Shell fabric", "3-layer GORE-TEX Pro, 100% recycled polyamide, 70 denier (denier = fabric thickness; higher = tougher, more durable)"),
            ("Waterproofness", "28,000mm"),
            ("Breathability (RET)", "13.5 — lower RET = more breathable"),
            ("Weight", "680g (men's size L)"),
        ],
        size_headers=["Size", "Waist", "Hip", "Thigh width", "Hem width", "Inseam"],
        size_rows=[
            ["S", "96.0", "108.0", "74.5", "53.5", "78.5"],
            ["M", "102.0", "114.0", "77.5", "55.0", "79.5"],
            ["L", "108.0", "120.0", "80.5", "56.0", "80.5"],
            ["XL", "114.0", "126.0", "83.5", "57.0", "81.0"],
        ],
        size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value.",
        colors=["Purple Night", "True Black", "Chlorophyll Green"],
        sizes=["S", "M", "L", "XL"],
        best_for="Freeride & backcountry skiing — maximum protection, bib design",
        images=[
            {"src": "../assets/img/vassi-gtx-pro-ii-bib-purple-night-front.webp",
             "alt": "Vassi GTX Pro II Bib, Purple Night colorway, front",
             "caption": "Purple Night — Front"},
            {"src": "../assets/img/vassi-gtx-pro-ii-bib-purple-night-back.webp",
             "alt": "Vassi GTX Pro II Bib, Purple Night colorway, back",
             "caption": "Purple Night — Back"},
            {"src": "../assets/img/vassi-gtx-pro-ii-bib-true-black-front.webp",
             "alt": "Vassi GTX Pro II Bib, True Black colorway, front",
             "caption": "True Black — Front"},
            {"src": "../assets/img/vassi-gtx-pro-ii-bib-true-black-back.webp",
             "alt": "Vassi GTX Pro II Bib, True Black colorway, back",
             "caption": "True Black — Back"},
            {"src": "../assets/img/vassi-gtx-pro-ii-bib-chlorophyll-green-front.webp",
             "alt": "Vassi GTX Pro II Bib, Chlorophyll Green colorway, front",
             "caption": "Chlorophyll Green — Front"},
            {"src": "../assets/img/vassi-gtx-pro-ii-bib-chlorophyll-green-back.webp",
             "alt": "Vassi GTX Pro II Bib, Chlorophyll Green colorway, back",
             "caption": "Chlorophyll Green — Back"},
        ],
        card_tag="Freeride Bib",
        card_name="Vassi GTX Pro II Bib",
        mini_specs=["GORE-TEX Pro", "28,000mm", "680g"],
        thumb_src="assets/img/vassi-gtx-pro-ii-bib-purple-night-front.webp",
        thumb_alt="Vassi GTX Pro II Bib",
        radar_scores=[3, 5, 5, 4, 2],
        radar_alt="Vassi GTX Pro II Bib fit chart: strongest for powder and off-piste",
        compare=dict(shell_insulation="GORE-TEX Pro 3L / Shell only", waterproof="28,000mm",
                     breathability="13.5", weight="680g", best_for_short="Freeride & backcountry"),
    ),
    dict(
        slug="vassi-gtx-ii-pant",
        category="pants", subcategory="shell", gender="mens",
        activity_tags=["Ski"],
        name_en="Vassi GTX II Pant Men",
        name_jp="ヴァッシ ゴアテックス II パンツ〔メンズ〕",
        model_number="608575",
        price="¥82,500",
        price_note=" (tax included) — final total confirmed at checkout",
        meta_desc="Haglöfs Vassi GTX II freeride ski pant — specs, features and size chart for international customers.",
        gallery_labels=["Front", "Back", "Worn, on mountain"],
        kf_items=[
            ("Waterproof", "28,000mm"),
            ("Breathability", "RET 20"),
            ("Weight (L)", "610g"),
            ("Style", "Pant"),
        ],
        about=("The pant counterpart to Haglöfs' everyday Vassi GTX II jacket. A 3-layer GORE-TEX shell gives "
               "waterproof, windproof protection in a durable 75-denier fabric — a strong all-round choice for "
               "resort and backcountry skiing alike."),
        features=[
            "Velcro-adjustable waist with belt loops",
            "2-way zippered thigh ventilation",
            "Zippered thigh pocket",
            "Articulated (shaped) knees",
            "Adjustable, rubber-grip gaiters",
            "Edge guards",
            "RECCO® reflector for avalanche rescue search",
        ],
        specs_rows=[
            ("Shell fabric", "3-layer GORE-TEX, 100% recycled polyester, 75 denier (denier = fabric thickness; higher = tougher, more durable)"),
            ("Membrane", "GORE-TEX ePE laminate (a 2-layer waterproof membrane)"),
            ("Waterproofness", "28,000mm"),
            ("Breathability (RET)", "20 — lower RET = more breathable; 20 is a solid everyday resort/freeride level"),
            ("Weight", "610g (men's size L)"),
        ],
        size_headers=["Size", "Waist", "Hip", "Thigh width", "Hem width", "Inseam"],
        size_rows=[
            ["S", "86.5", "100.0", "67.0", "53.5", "82.0"],
            ["M", "92.5", "106.0", "70.0", "55.0", "83.0"],
            ["L", "98.5", "112.0", "73.0", "56.0", "84.0"],
            ["XL", "104.5", "118.0", "76.0", "57.0", "84.5"],
        ],
        size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value.",
        colors=["True Black", "Tarn Blue", "Chalk Beige"],
        sizes=["S", "M", "L", "XL"],
        best_for="Everyday resort & freeride skiing — great all-round value",
        card_tag="Freeride Shell",
        card_name="Vassi GTX II Pant",
        mini_specs=["GORE-TEX", "28,000mm", "610g"],
        images=[
            {"src": "../assets/img/vassi-gtx-ii-pant-true-black-front.webp", "alt": "Vassi GTX II Pant, True Black colorway, front", "caption": "True Black — Front"},
            {"src": "../assets/img/vassi-gtx-ii-pant-true-black-back.webp", "alt": "Vassi GTX II Pant, True Black colorway, back", "caption": "True Black — Back"},
            {"src": "../assets/img/vassi-gtx-ii-pant-tarn-blue-front.webp", "alt": "Vassi GTX II Pant, Tarn Blue colorway, front", "caption": "Tarn Blue — Front"},
            {"src": "../assets/img/vassi-gtx-ii-pant-tarn-blue-back.webp", "alt": "Vassi GTX II Pant, Tarn Blue colorway, back", "caption": "Tarn Blue — Back"},
            {"src": "../assets/img/vassi-gtx-ii-pant-chalk-beige-front.webp", "alt": "Vassi GTX II Pant, Chalk Beige colorway, front", "caption": "Chalk Beige — Front"},
            {"src": "../assets/img/vassi-gtx-ii-pant-chalk-beige-back.webp", "alt": "Vassi GTX II Pant, Chalk Beige colorway, back", "caption": "Chalk Beige — Back"},
        ],
        thumb_src="assets/img/vassi-gtx-ii-pant-true-black-front.webp",
        thumb_alt="Vassi GTX II Pant",
        radar_scores=[3, 4, 4, 3, 3],
        radar_alt="Vassi GTX II Pant fit chart: balanced, strongest for powder and off-piste",
        compare=dict(shell_insulation="GORE-TEX 3L / Shell only", waterproof="28,000mm",
                     breathability="20", weight="610g", best_for_short="Freeride, everyday value"),
    ),
    dict(
        slug="alper-proof-pant",
        category="pants", subcategory="shell", gender="mens",
        activity_tags=["Ski"],
        name_en="Alper Proof Pant Men",
        name_jp="アルパー プルーフ パンツ〔メンズ〕",
        model_number="607939",
        price="¥50,600",
        price_note=" (tax included) — final total confirmed at checkout",
        meta_desc="Haglöfs Alper Proof all-mountain ski pant — specs, features and size chart for international customers.",
        gallery_labels=["Front", "Back", "Worn, on mountain"],
        kf_items=[
            ("Waterproof", "20,000mm"),
            ("Breathability", "20,000 g/m²/24h"),
            ("Weight (L)", "510g"),
            ("Style", "Pant"),
        ],
        about=("The pant counterpart to Haglöfs' value-focused Alper Proof jacket, built with the brand's in-house "
               "PROOF™ Pro waterproof fabric. Covers the everyday ski-resort essentials — ventilation, a snow "
               "gaiter, Kevlar-reinforced edge guards — without the price tag of a GORE-TEX shell."),
        features=[
            "Zippered thigh ventilation",
            "Snow gaiter with stretch webbing and rubber grip",
            "Velcro waist adjustment with belt loops",
            "3D-formed (articulated) knees for mobility",
            "Kevlar-reinforced edge guards",
        ],
        specs_rows=[
            ("Shell fabric", "3-layer PROOF™ Pro, 100% recycled polyester"),
            ("Waterproofness", "20,000mm"),
            ("Breathability", "20,000 g/m²/24h (higher number = more breathable; a solid everyday resort level)"),
            ("Weight", "510g (men's size L)"),
        ],
        size_headers=["Size", "Waist", "Hip", "Thigh width", "Leg opening", "Inseam"],
        size_rows=[
            ["S", "87.0", "102.0", "68.5", "53.5", "82.5"],
            ["M", "93.0", "108.0", "71.5", "55.0", "83.5"],
            ["L", "99.0", "114.0", "74.5", "56.0", "84.5"],
            ["XL", "105.0", "120.0", "77.5", "57.0", "85.0"],
        ],
        size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value.",
        colors=["True Black", "Tarn Blue", "Seaweed Green"],
        sizes=["S", "M", "L", "XL"],
        best_for="All-mountain resort skiing — best value shell in this lineup",
        card_tag="All-Mountain Shell",
        card_name="Alper Proof Pant",
        mini_specs=["PROOF™ Pro", "20,000mm", "510g"],
        images=[
            {"src": "../assets/img/alper-proof-pant-true-black-front.webp", "alt": "Alper Proof Pant, True Black colorway, front", "caption": "True Black — Front"},
            {"src": "../assets/img/alper-proof-pant-true-black-back.webp", "alt": "Alper Proof Pant, True Black colorway, back", "caption": "True Black — Back"},
            {"src": "../assets/img/alper-proof-pant-tarn-blue-front.webp", "alt": "Alper Proof Pant, Tarn Blue colorway, front", "caption": "Tarn Blue — Front"},
            {"src": "../assets/img/alper-proof-pant-tarn-blue-back.webp", "alt": "Alper Proof Pant, Tarn Blue colorway, back", "caption": "Tarn Blue — Back"},
            {"src": "../assets/img/alper-proof-pant-seaweed-green-front.webp", "alt": "Alper Proof Pant, Seaweed Green colorway, front", "caption": "Seaweed Green — Front"},
            {"src": "../assets/img/alper-proof-pant-seaweed-green-back.webp", "alt": "Alper Proof Pant, Seaweed Green colorway, back", "caption": "Seaweed Green — Back"},
        ],
        thumb_src="assets/img/alper-proof-pant-true-black-front.webp",
        thumb_alt="Alper Proof Pant",
        radar_scores=[3, 3, 3, 3, 3],
        radar_alt="Alper Proof Pant fit chart: evenly balanced all-around",
        compare=dict(shell_insulation="PROOF™ Pro 3L / Shell only", waterproof="20,000mm",
                     breathability="— (breathability 20,000g/m²/24h)", weight="510g", best_for_short="All-mountain, best value"),
    ),
    dict(
        slug="latnja-gtx-insulated-pant",
        category="pants", subcategory="insulated", gender="mens",
        activity_tags=["Ski"],
        name_en="Latnja GTX Insulated Pant Men",
        name_jp="ラティニャ ゴアテックス インシュレイテッド パンツ〔メンズ〕",
        model_number="607470",
        price="¥59,400",
        price_note=" (tax included) — final total confirmed at checkout",
        meta_desc="Haglöfs Latnja GTX Insulated ski pant — specs, features and size chart for international customers.",
        gallery_labels=["Front", "Back", "Worn, on mountain"],
        kf_items=[
            ("Waterproof", "28,000mm"),
            ("Breathability", "RET 13"),
            ("Weight (L)", "632g"),
            ("Style", "Pant"),
        ],
        about=("The pant counterpart to Haglöfs' insulated Latnja jacket, for genuinely cold resort days. A "
               "waterproof GORE-TEX 2-layer shell is paired with a lightweight Mimic SILVER fill, body-mapped so "
               "warmth is added where you need it most."),
        features=[
            "Adjustable waistband",
            "Spacious pockets",
            "Zippered ventilation",
            "Built-in snow gaiter",
            "Body-mapped insulation zones for targeted warmth",
        ],
        specs_rows=[
            ("Shell fabric", "75 denier, 100% recycled polyester / GORE-TEX® 2L ePE (denier = fabric thickness; ePE = a 2-layer waterproof membrane)"),
            ("Insulation", "100% recycled polyester / Mimic SILVER, body-mapped for targeted warmth"),
            ("Waterproofness", "28,000mm"),
            ("Breathability (RET)", "13 — lower RET = more breathable; this is a warm, cold-weather level"),
            ("Weight", "632g (men's size L)"),
        ],
        size_headers=None,
        size_rows=None,
        size_note="A full cm size chart for this item wasn't available from our reference source — ask staff in store for exact measurements.",
        colors=["True Black", "Tarn Blue", "Chalk Beige", "Chlorophyll Green"],
        sizes=["S", "M", "L", "XL"],
        best_for="Cold resort days — built-in insulation, no midlayer needed",
        card_tag="Insulated",
        card_name="Latnja GTX Insulated Pant",
        mini_specs=["GORE-TEX 2L", "28,000mm", "632g"],
        images=[
            {"src": "../assets/img/latnja-gtx-insulated-pant-true-black-front.webp", "alt": "Latnja GTX Insulated Pant, True Black colorway, front", "caption": "True Black — Front"},
            {"src": "../assets/img/latnja-gtx-insulated-pant-true-black-back.webp", "alt": "Latnja GTX Insulated Pant, True Black colorway, back", "caption": "True Black — Back"},
            {"src": "../assets/img/latnja-gtx-insulated-pant-tarn-blue-front.webp", "alt": "Latnja GTX Insulated Pant, Tarn Blue colorway, front", "caption": "Tarn Blue — Front"},
            {"src": "../assets/img/latnja-gtx-insulated-pant-tarn-blue-back.webp", "alt": "Latnja GTX Insulated Pant, Tarn Blue colorway, back", "caption": "Tarn Blue — Back"},
            {"src": "../assets/img/latnja-gtx-insulated-pant-chalk-beige-front.webp", "alt": "Latnja GTX Insulated Pant, Chalk Beige colorway, front", "caption": "Chalk Beige — Front"},
            {"src": "../assets/img/latnja-gtx-insulated-pant-chalk-beige-back.webp", "alt": "Latnja GTX Insulated Pant, Chalk Beige colorway, back", "caption": "Chalk Beige — Back"},
            {"src": "../assets/img/latnja-gtx-insulated-pant-chlorophyll-green-front.webp", "alt": "Latnja GTX Insulated Pant, Chlorophyll Green colorway, front", "caption": "Chlorophyll Green — Front"},
            {"src": "../assets/img/latnja-gtx-insulated-pant-chlorophyll-green-back.webp", "alt": "Latnja GTX Insulated Pant, Chlorophyll Green colorway, back", "caption": "Chlorophyll Green — Back"},
        ],
        thumb_src="assets/img/latnja-gtx-insulated-pant-true-black-front.webp",
        thumb_alt="Latnja GTX Insulated Pant",
        radar_scores=[5, 2, 1, 2, 5],
        radar_alt="Latnja GTX Insulated Pant fit chart: strongest for resort skiing and cold weather",
        compare=dict(shell_insulation="GORE-TEX 2L / Insulated (body-mapped fill)", waterproof="28,000mm",
                     breathability="13", weight="632g", best_for_short="Cold-weather resort"),
    ),
    dict(
        slug="nallo-touring-gtx-pant",
        category="pants", subcategory="shell", gender="mens",
        activity_tags=["Ski", "Touring"],
        name_en="Nallo Touring GTX Pant Men",
        name_jp="ナロ ツーリング ゴアテックス パンツ〔メンズ〕",
        model_number="608335",
        price="¥82,500",
        price_note=" (tax included) — final total confirmed at checkout",
        meta_desc="Haglöfs Nallo Touring GTX ski touring pant — specs, features and size chart for international customers.",
        gallery_labels=["Front", "Back", "Worn, touring"],
        kf_items=[
            ("Waterproof", "28,000mm"),
            ("Breathability", "RET 13"),
            ("Weight (L)", "394g — lightest in series"),
            ("Style", "Pant"),
        ],
        about=("The pant counterpart to Haglöfs' Nallo Touring GTX jacket, built for ski touring rather than the "
               "lift line. A light 30-denier GORE-TEX ripstop shell keeps weight down, with a snow gaiter "
               "compatible with walk-mode ski boots and Twiceme® safety technology built in."),
        features=[
            "Side adjustable waist with velcro tabs and belt loops",
            "Side ventilation zips",
            "2 zippered thigh pockets",
            "Articulated, pre-shaped knees for mobility",
            "Snow gaiter compatible with walk-mode ski boots",
            "Edge guards",
            "Reflective brand logo for visibility",
            "Twiceme® technology — NFC tag shares medical/location info with first responders",
        ],
        specs_rows=[
            ("Shell fabric", "100% recycled polyamide, 30 denier, 3-layer GORE-TEX ripstop (denier = fabric thickness; higher = tougher, more durable)"),
            ("Lining", "100% polyamide"),
            ("Pocket mesh", "95% polyamide, 5% polyurethane"),
            ("Waterproofness", "28,000mm"),
            ("Breathability (RET)", "13 — lower RET = more breathable; this is a highly breathable, touring-friendly level"),
            ("Weight", "394g (men's size L)"),
        ],
        size_headers=["Size", "Waist", "Hip", "Inseam", "Thigh width", "Hem width"],
        size_rows=[
            ["S", "87.5", "103.0", "84.0", "69.0", "53.5"],
            ["M", "93.5", "109.0", "85.0", "72.0", "55.0"],
            ["L", "99.5", "115.0", "86.0", "75.0", "56.0"],
            ["XL", "105.5", "121.0", "86.5", "78.0", "57.0"],
        ],
        size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value.",
        colors=["True Black", "Chalk Beige"],
        sizes=["S", "M", "L", "XL"],
        best_for="Ski touring & uphill travel — lightest option in this lineup",
        card_tag="Ski Touring Shell",
        card_name="Nallo Touring GTX Pant",
        mini_specs=["GORE-TEX", "28,000mm", "394g"],
        images=[
            {"src": "../assets/img/nallo-touring-gtx-pant-true-black-front.webp", "alt": "Nallo Touring GTX Pant, True Black colorway, front", "caption": "True Black — Front"},
            {"src": "../assets/img/nallo-touring-gtx-pant-true-black-back.webp", "alt": "Nallo Touring GTX Pant, True Black colorway, back", "caption": "True Black — Back"},
            {"src": "../assets/img/nallo-touring-gtx-pant-chalk-beige-front.webp", "alt": "Nallo Touring GTX Pant, Chalk Beige colorway, front", "caption": "Chalk Beige — Front"},
            {"src": "../assets/img/nallo-touring-gtx-pant-chalk-beige-back.webp", "alt": "Nallo Touring GTX Pant, Chalk Beige colorway, back", "caption": "Chalk Beige — Back"},
        ],
        thumb_src="assets/img/nallo-touring-gtx-pant-true-black-front.webp",
        thumb_alt="Nallo Touring GTX Pant",
        radar_scores=[3, 3, 4, 5, 1],
        radar_alt="Nallo Touring GTX Pant fit chart: strongest for touring, also strong off-piste",
        compare=dict(shell_insulation="GORE-TEX 3L ripstop / Shell only", waterproof="28,000mm",
                     breathability="13", weight="394g", best_for_short="Ski touring, lightest option"),
    ),
]

def products_in(category_slug, gender=None):
    out = [p for p in PRODUCTS if p["category"] == category_slug]
    if gender:
        out = [p for p in out if p["gender"] == gender]
    return out

# ---------------------------------------------------------------
# Product page template + builder
# ---------------------------------------------------------------
TEMPLATE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name_en} — Haglöfs Shibuya</title>
<meta name="description" content="{meta_desc}">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body class="has-ask-bar">

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="../index.html">Haglöfs Shibuya<small>Shop Guide</small></a>
    <nav><a href="../index.html">All items</a></nav>
  </div>
</header>

<div class="wrap">

  <a class="back-link" href="{back_href}">&larr; {back_label}</a>

  <div class="gallery">
{gallery}
  </div>

  <div class="product-head">
    <div class="model-tag">Haglöfs · Style {model_number}</div>
    <h1>{name_en}</h1>
    <p class="price">{price}<small>{price_note}</small></p>
    <p class="currency-note">Paying in another currency? Rates vary by country and change daily — search &quot;JPY to [your currency]&quot; online for today's rate.</p>
    <div class="best-for">Best for: {best_for}</div>
    {activity_pills}
    <div class="radar-chart-block">
      <p class="radar-chart-caption">Fit chart</p>
      <img src="../assets/img/radar-{slug}.svg" loading="eager" decoding="sync" alt="{name_en} fit chart ({axes_str})">
    </div>
  </div>

  <div class="key-features">
{key_features}
  </div>

  <section class="section-block">
    <h2>About this item</h2>
    <p>{about}</p>
  </section>

  <section class="section-block">
    <h2>Key features</h2>
    <ul class="feature-list">
{features}
    </ul>
  </section>

  <section class="section-block">
    <h2>Materials &amp; specs</h2>
    <table class="specs">
{specs}
    </table>
  </section>

  <section class="section-block">
{size_section}
  </section>

  <section class="section-block">
    <h2>Colors &amp; sizes in this style</h2>
    <p style="font-size:12.5px;color:var(--muted);margin:0 0 6px;">Colors</p>
    <div class="avail-grid">
{colors}
    </div>
    <p style="font-size:12.5px;color:var(--muted);margin:14px 0 6px;">Sizes</p>
    <div class="avail-grid">
{sizes}
    </div>
    <p class="stock-note">Sizes shown above run S–XL. Some items and colors may also be available in other sizes (e.g. XXL) depending on style — please ask staff to confirm what's currently in stock.</p>
  </section>

  <section class="section-block">
    <h2>{related_heading}</h2>
    <div class="related-grid">
{related}
    </div>
  </section>

  <div class="staff-note">
    <strong>Tax-free shopping:</strong> Japan's tax refund system changed in November 2026 — you now pay the tax-included price here in store, then claim a refund of the consumption tax when you leave Japan. Show your passport and receipt at the tax refund counter at the airport (within 90 days of purchase). Ask staff for details.
  </div>

  <div class="staff-note">
    Not sure which one fits your trip? Show this page to any Haglöfs Shibuya staff member — we're happy to help in English.
  </div>

</div>

<footer class="site-footer">
  <div class="wrap">
    <span>Haglöfs Shibuya · RCT Japan</span>
    <span>Ask any staff member if you'd like help in English.</span>
  </div>
</footer>

<div class="ask-staff-bar">Need help deciding? <strong>Ask any staff member</strong> — happy to help in English.</div>

</body>
</html>
'''

def build_product_page(p):
    slug = p["slug"]
    cat = CATEGORY_BY_SLUG[p["category"]]
    axes = AXIS_SETS[p["category"]]

    gallery = gallery_images_html(p["images"]) if p.get("images") else gallery_html(p["gallery_labels"])
    key_features = kf_html(p["kf_items"])
    feat_list = feature_list_html(p["features"])
    specs = specs_table_html(p["specs_rows"])

    if p["size_headers"]:
        head, body = size_table_html(p["size_headers"], p["size_rows"])
        size_section = f'''    <h2>Size chart (cm)</h2>
    <p class="scroll-hint">Swipe left to see all columns &rarr;</p>
    <div class="size-table-wrap">
      <table class="size">
        <thead><tr>{head}</tr></thead>
        <tbody>
{body}
        </tbody>
      </table>
    </div>
    <p class="size-note">{p['size_note']}</p>'''
    else:
        size_section = f'''    <h2>Size chart</h2>
    <p class="size-note">{p['size_note']}</p>'''

    colors_html = color_chips_html(p["colors"])
    sizes_html = chips_html(p["sizes"])
    related = related_html(products_in(p["category"]), slug)

    html = TEMPLATE.format(
        slug=slug, name_en=p["name_en"], model_number=p["model_number"],
        price=p["price"], price_note=p["price_note"], meta_desc=p["meta_desc"],
        gallery=gallery, key_features=key_features, about=p["about"],
        features=feat_list, specs=specs, size_section=size_section,
        colors=colors_html, sizes=sizes_html, related=related,
        best_for=p["best_for"],
        back_href=f"../category/{cat['slug']}.html",
        back_label=f"All {cat['label'].lower()}",
        activity_pills=activity_pills_html(p.get("activity_tags")),
        axes_str=" / ".join(axes),
        related_heading=f"Compare with other {cat['label'].lower()} in this category",
    )
    out_path = os.path.join(OUT_DIR, f"{slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out_path)

    write_radar_svg(slug, p["radar_scores"], axes)
    print("wrote", os.path.join(IMG_DIR, f"radar-{slug}.svg"))

# ---------------------------------------------------------------
# Category-page card row (used on category/<slug>.html) + builder
# ---------------------------------------------------------------
def radar_row_html(p, path_prefix=""):
    tag_pills = activity_pills_html(p.get("activity_tags"))
    if p.get("images"):
        thumb_html = f'<div class="radar-row-thumb"><img src="{path_prefix}{p["thumb_src"]}" alt="{p["thumb_alt"]}"></div>'
    else:
        thumb_html = f'<div class="radar-row-thumb radar-row-thumb-placeholder">{PLACEHOLDER_ICON}</div>'
    return f'''      <a class="radar-row" href="{path_prefix}products/{p['slug']}.html">
        <div class="radar-row-card">
          {thumb_html}
          <div class="radar-row-info">
            <div class="card-tag">{p['card_tag']}</div>
            <h3>{p['card_name']}</h3>
            {tag_pills}
            <div class="mini-specs">
              {''.join(f'<span>{s}</span>' for s in p['mini_specs'])}
            </div>
          </div>
        </div>
        <div class="radar-row-chart">
          <p class="radar-chart-caption radar-chart-caption-sm">Fit chart</p>
          <img src="{path_prefix}assets/img/radar-{p['slug']}.svg" loading="eager" decoding="sync" alt="{p['radar_alt']}">
        </div>
      </a>'''

def compare_table_html(cat_slug, products):
    headers = COMPARE_HEADERS.get(cat_slug)
    if not headers or not products:
        return ""
    head_html = ''.join(f'<th>{h}</th>' if i > 0 else f'<th class="row-label">{h}</th>' for i, h in enumerate(headers))
    rows = []
    for p in products:
        c = p.get("compare")
        if not c:
            continue
        rows.append(
            f'          <tr>\n'
            f'            <th class="row-label"><a href="../products/{p["slug"]}.html">{p["card_name"]}</a></th>\n'
            f'            <td>{c["shell_insulation"]}</td>\n'
            f'            <td>{c["waterproof"]}</td>\n'
            f'            <td>{c["breathability"]}</td>\n'
            f'            <td>{c["weight"]}</td>\n'
            f'            <td>{c["best_for_short"]}</td>\n'
            f'          </tr>'
        )
    if not rows:
        return ""
    return f'''    <h2 style="margin-top:28px;">Quick compare</h2>
    <p class="scroll-hint">Swipe left to see all columns &rarr;</p>
    <div class="compare-wrap">
      <table class="compare">
        <caption>Key specs at a glance — tap a name to open the full page</caption>
        <thead>
          <tr>
            {head_html}
          </tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </div>
    <p class="size-note">Figures above are men's size L unless noted. Reference prices and specs — please confirm final price and stock with a staff member.</p>'''

def gender_panel_html(cat_slug, gender, label):
    products = products_in(cat_slug, gender)
    if not products:
        return f'    <p class="category-empty-note">{label} items are not yet available on this guide — ask staff in store, or check back soon.</p>'
    rows = '\n'.join(radar_row_html(p, path_prefix="../") for p in products)
    compare = compare_table_html(cat_slug, products)
    out = f'    <div class="radar-list">\n{rows}\n    </div>'
    if compare:
        out += "\n" + compare
    return out

CATEGORY_TEMPLATE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{label} — Haglöfs Shibuya</title>
<meta name="description" content="{meta_desc}">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="../index.html">Haglöfs Shibuya<small>Shop Guide</small></a>
    <nav><a href="../index.html">All items</a></nav>
  </div>
</header>

<div class="wrap">

  <a class="back-link" href="../index.html">&larr; All categories</a>

  <section class="section-block" style="border-top:none; padding-top:0;">
    <h1>{label}</h1>
    <p class="radar-note">{blurb}</p>

    <div class="gender-tabs">
      <input type="radio" name="gender-{slug}" id="gender-{slug}-mens" checked>
      <label for="gender-{slug}-mens">Men's</label>
      <input type="radio" name="gender-{slug}" id="gender-{slug}-womens">
      <label for="gender-{slug}-womens">Women's</label>

      <div class="gender-panel">
{mens_panel}
      </div>
      <div class="gender-panel">
{womens_panel}
      </div>
    </div>
  </section>

</div>

<footer class="site-footer">
  <div class="wrap">
    <span>Haglöfs Shibuya · RCT Japan</span>
    <span>Ask any staff member if you'd like help in English.</span>
  </div>
</footer>

</body>
</html>
'''

def build_category_page(cat):
    mens_panel = gender_panel_html(cat["slug"], "mens", "Men's")
    womens_panel = gender_panel_html(cat["slug"], "womens", "Women's")
    html = CATEGORY_TEMPLATE.format(
        slug=cat["slug"], label=cat["label"], blurb=cat["blurb"],
        meta_desc=f"{cat['label']} available at Haglöfs Shibuya — specs, features and sizing for international customers.",
        mens_panel=mens_panel, womens_panel=womens_panel,
    )
    out_path = os.path.join(CATEGORY_DIR, f"{cat['slug']}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out_path)

# ---------------------------------------------------------------
# index.html category-grid block
# ---------------------------------------------------------------
def category_tile_html(cat):
    count = len(products_in(cat["slug"]))
    if count == 0:
        return f'''      <div class="category-tile category-tile-soon">
        <div class="category-tile-label">{cat['label']}</div>
        <div class="category-tile-count">Coming soon</div>
        <p class="category-tile-blurb">{cat['blurb']}</p>
      </div>'''
    style_word = "style" if count == 1 else "styles"
    return f'''      <a class="category-tile" href="category/{cat['slug']}.html">
        <div class="category-tile-label">{cat['label']}</div>
        <div class="category-tile-count">{count} {style_word}</div>
        <p class="category-tile-blurb">{cat['blurb']}</p>
      </a>'''

def update_index_category_grid():
    """Replace the content between the CATEGORY_GRID markers in index.html
    with freshly generated category tiles. Everything else in index.html
    (intro, tax-free notice, payment methods, footer) is left untouched."""
    with open(INDEX_PATH, encoding="utf-8") as f:
        html = f.read()
    new_block = '\n'.join(category_tile_html(c) for c in CATEGORIES)
    pattern = re.compile(
        r"(<!-- CATEGORY_GRID:START -->\n)(.*?)(\n *<!-- CATEGORY_GRID:END -->)",
        re.DOTALL,
    )
    if not pattern.search(html):
        raise RuntimeError(
            "CATEGORY_GRID:START / CATEGORY_GRID:END markers not found in index.html — "
            "can't auto-update the category grid. Check index.html wasn't edited to remove them."
        )
    html = pattern.sub(lambda m: m.group(1) + new_block + m.group(3), html)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"updated {INDEX_PATH} ({len(CATEGORIES)} category tiles)")


if not os.path.isdir(CATEGORY_DIR):
    os.makedirs(CATEGORY_DIR)

for product in PRODUCTS:
    build_product_page(product)

for category in CATEGORIES:
    build_category_page(category)

update_index_category_grid()

print("done")
