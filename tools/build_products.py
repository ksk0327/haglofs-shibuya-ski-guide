# -*- coding: utf-8 -*-
"""Generates the 5 Haglöfs ski-series product pages from structured data."""
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "products")

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

def related_html(items, current_slug):
    out = []
    for slug, name, spec in items:
        if slug == current_slug:
            continue
        out.append(f'''    <a href="{slug}.html"><span class="rel-name">{name}</span><span class="rel-spec">{spec}</span></a>''')
    return '\n'.join(out)

ALL_PRODUCTS = [
    ("vassi-gtx-pro-ii", "Vassi GTX Pro II Jacket", "28,000mm WP / 665g"),
    ("vassi-gtx-ii", "Vassi GTX II Jacket", "28,000mm WP / 720g"),
    ("alper-proof", "Alper Proof Jacket", "20,000mm WP / 670g"),
    ("latnja-gtx-insulated", "Latnja GTX Insulated Jacket", "Insulated / see staff"),
    ("nallo-touring-gtx", "Nallo Touring GTX Jacket", "28,000mm WP / 407g — lightest"),
]

TEMPLATE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name_en} — Haglöfs Shibuya</title>
<meta name="description" content="{meta_desc}">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="../index.html">Haglöfs Shibuya<small>Ski Series Guide</small></a>
    <nav><a href="../index.html">All items</a></nav>
  </div>
</header>

<div class="wrap">

  <a class="back-link" href="../index.html">&larr; All ski jackets</a>

  <div class="gallery">
{gallery}
  </div>

  <div class="product-head">
    <div class="model-tag">Haglöfs · Style {model_number}</div>
    <h1>{name_en}</h1>
    <p class="jp-name">{name_jp}</p>
    <p class="price">{price}<small>{price_note}</small></p>
  </div>

  <div class="key-features">
{key_features}
  </div>

  <section class="section-block">
    <h2>About this jacket</h2>
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
  </section>

  <section class="section-block">
    <h2>Compare with other Ski Series jackets</h2>
    <div class="related-grid">
{related}
    </div>
  </section>

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

</body>
</html>
'''

def build(slug, name_en, name_jp, model_number, price, price_note, meta_desc,
          gallery_labels, kf_items, about, features, specs_rows,
          size_headers, size_rows, size_note, colors, sizes, images=None):
    gallery = gallery_images_html(images) if images else gallery_html(gallery_labels)
    key_features = kf_html(kf_items)
    feat_list = feature_list_html(features)
    specs = specs_table_html(specs_rows)

    if size_headers:
        head, body = size_table_html(size_headers, size_rows)
        size_section = f'''    <h2>Size chart (cm)</h2>
    <div class="size-table-wrap">
      <table class="size">
        <thead><tr>{head}</tr></thead>
        <tbody>
{body}
        </tbody>
      </table>
    </div>
    <p class="size-note">{size_note}</p>'''
    else:
        size_section = f'''    <h2>Size chart</h2>
    <p>{size_note}</p>'''

    colors_html = chips_html(colors)
    sizes_html = chips_html(sizes)
    related = related_html(ALL_PRODUCTS, slug)

    html = TEMPLATE.format(
        name_en=name_en, name_jp=name_jp, model_number=model_number,
        price=price, price_note=price_note, meta_desc=meta_desc,
        gallery=gallery, key_features=key_features, about=about,
        features=feat_list, specs=specs, size_section=size_section,
        colors=colors_html, sizes=sizes_html, related=related,
    )
    out_path = os.path.join(OUT_DIR, f"{slug}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", out_path)


# ---------------------------------------------------------------
# 1) Vassi GTX Pro II Jacket Men
# ---------------------------------------------------------------
build(
    slug="vassi-gtx-pro-ii",
    name_en="Vassi GTX Pro II Jacket Men",
    name_jp="ヴァッシ ゴアテックス プロ II ジャケット〔メンズ〕",
    model_number="608577",
    price="¥126,500",
    price_note=" reference price — please confirm in store",
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
        "PFAS-free water-repellent (DWR) finish",
        "bluesign® approved fabric",
    ],
    specs_rows=[
        ("Shell fabric", "3-layer GORE-TEX Pro, 100% recycled polyamide, 70 denier"),
        ("Waterproofness", "28,000mm"),
        ("Breathability (RET)", "13.5 — lower RET = more breathable"),
        ("Weight", "665g (men's size L)"),
        ("Water repellent finish", "PFAS-free DWR"),
        ("Certification", "bluesign® approved"),
    ],
    size_headers=["Size", "Chest", "Waist width", "Hem width", "Body length", "Sleeve length"],
    size_rows=[
        ["S", "121.5", "110.0", "112.0", "83.0", "84.0"],
        ["M", "127.5", "116.0", "118.0", "84.0", "85.5"],
        ["L", "133.5", "122.0", "124.0", "85.0", "87.5"],
        ["XL", "139.5", "128.0", "130.0", "86.0", "89.0"],
        ["XXL", "145.5", "134.0", "136.0", "87.0", "90.5"],
    ],
    size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value. Reference model is 166cm tall, shown in size M.",
    colors=["Purple Night / Evening", "True Black / Chlorophyll Green"],
    sizes=["S", "M", "L", "XL", "XXL"],
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
)

# ---------------------------------------------------------------
# 2) Vassi GTX II Jacket Men
# ---------------------------------------------------------------
build(
    slug="vassi-gtx-ii",
    name_en="Vassi GTX II Jacket Men",
    name_jp="ヴァッシ ゴアテックス II ジャケット〔メンズ〕",
    model_number="608574",
    price="¥93,500",
    price_note=" reference price — please confirm in store",
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
        "RECCO® reflector",
        "PFAS-free water-repellent (DWR) finish",
        "bluesign® approved fabric",
    ],
    specs_rows=[
        ("Shell fabric", "3-layer GORE-TEX, 100% recycled polyester, 75 denier"),
        ("Membrane", "PFAS-free GORE-TEX ePE laminate"),
        ("Waterproofness", "28,000mm"),
        ("Breathability (RET)", "20"),
        ("Weight", "720g (men's size L)"),
        ("Water repellent finish", "PFAS-free DWR"),
        ("Certification", "bluesign® approved"),
    ],
    size_headers=["Size", "Chest", "Waist width", "Hem width", "Body length", "Sleeve length"],
    size_rows=[
        ["S", "118.0", "109.5", "111.5", "80.5", "83.5"],
        ["M", "124.0", "115.5", "117.5", "81.5", "85.0"],
        ["L", "130.0", "121.5", "123.5", "82.5", "87.0"],
        ["XL", "136.0", "127.5", "129.5", "83.5", "88.5"],
        ["XXL", "142.0", "133.5", "135.5", "84.5", "90.0"],
    ],
    size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value.",
    colors=["Purple Night", "Teak Brown / Woodland", "Dew Green", "Tarn Blue"],
    sizes=["S", "M", "L", "XL", "XXL"],
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
)

# ---------------------------------------------------------------
# 3) Alper Proof Jacket Men
# ---------------------------------------------------------------
build(
    slug="alper-proof",
    name_en="Alper Proof Jacket Men",
    name_jp="アルパー プルーフ ジャケット〔メンズ〕",
    model_number="607936",
    price="¥59,400",
    price_note=" reference price — please confirm in store",
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
        ("Shell fabric", "3-layer PROOF™ Pro, 100% recycled polyester, 75 denier"),
        ("Waterproofness", "20,000mm"),
        ("Breathability", "20,000 g/m²/24h"),
        ("Weight", "670g (men's size L)"),
    ],
    size_headers=["Size", "Chest", "Waist width", "Hem width", "Body length", "Sleeve length"],
    size_rows=[
        ["S", "118.0", "109.0", "111.0", "80.5", "84.5"],
        ["M", "124.0", "115.0", "117.0", "81.5", "86.0"],
        ["L", "130.0", "121.0", "123.0", "82.5", "88.0"],
        ["XL", "136.0", "127.0", "129.0", "83.5", "89.5"],
    ],
    size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value. No XXL in this style.",
    colors=["Northern Blue / Tarn Blue", "Seaweed Green / Chlorophyll Green", "Teak Brown", "True Black"],
    sizes=["S", "M", "L", "XL"],
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
)

# ---------------------------------------------------------------
# 4) Latnja GTX Insulated Jacket Men
# ---------------------------------------------------------------
build(
    slug="latnja-gtx-insulated",
    name_en="Latnja GTX Insulated Jacket Men",
    name_jp="ラティニャ ゴアテックス インシュレイテッド ジャケット〔メンズ〕",
    model_number="607469",
    price="¥69,300",
    price_note=" reference price — please confirm in store",
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
        "PFAS-free DWR finish",
        "RECCO® reflector",
    ],
    specs_rows=[
        ("Shell fabric", "75 denier, 100% recycled polyester / GORE-TEX® 2L ePE"),
        ("Lining", "100% recycled polyester"),
        ("Insulation", "100% recycled polyester / Mimic SILVER, body-mapped across 3 zones"),
        ("Waterproofness", "28,000mm"),
        ("Breathability (RET)", "RET > 13"),
        ("Weight", "860g (men's size L)"),
    ],
    size_headers=["Size", "Chest", "Waist width", "Shoulder width", "Body length", "Sleeve length"],
    size_rows=[
        ["S", "118.0", "109.0", "48.5", "81.0", "84.0"],
        ["M", "124.0", "115.0", "50.5", "82.0", "85.5"],
        ["L", "130.0", "121.0", "52.5", "83.0", "87.5"],
        ["XL", "136.0", "127.0", "54.5", "84.0", "89.0"],
        ["XXL", "142.0", "133.0", "56.5", "85.0", "90.5"],
    ],
    size_note="All measurements in cm, garment laid flat (external measurements). Multiply by 0.39 for an approximate inch value.",
    colors=["Chlorophyll Green", "Chalk Beige", "Turn Blue", "True Black"],
    sizes=["S", "M", "L", "XL", "XXL"],
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
         "alt": "Latnja GTX Insulated Jacket, Turn Blue colorway, front",
         "caption": "Turn Blue — Front"},
        {"src": "../assets/img/latnja-gtx-insulated-turn-blue-back.webp",
         "alt": "Latnja GTX Insulated Jacket, Turn Blue colorway, back",
         "caption": "Turn Blue — Back"},
    ],
)

# ---------------------------------------------------------------
# 5) Nallo Touring GTX Jacket Men
# ---------------------------------------------------------------
build(
    slug="nallo-touring-gtx",
    name_en="Nallo Touring GTX Jacket Men",
    name_jp="ナロ ツーリング ゴアテックス ジャケット〔メンズ〕",
    model_number="608333",
    price="¥97,900",
    price_note=" reference price — please confirm in store",
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
        "PFAS-free DWR finish",
        "bluesign® approved fabric",
    ],
    specs_rows=[
        ("Face fabric", "100% recycled polyamide, 30 denier, 3-layer GORE-TEX ripstop"),
        ("Lining", "100% polyamide"),
        ("Pocket mesh", "95% polyamide, 5% polyurethane"),
        ("Waterproofness", "28,000mm"),
        ("Breathability (RET)", "13"),
        ("Weight", "407g (men's size L)"),
        ("Water repellent finish", "PFAS-free DWR"),
        ("Certification", "bluesign® approved"),
    ],
    size_headers=["Size", "Chest", "Hem width", "Waist", "Body length", "Sleeve length"],
    size_rows=[
        ["S", "118.0", "112.0", "112.0", "77.5", "83.5"],
        ["M", "124.0", "118.0", "118.0", "78.5", "85.0"],
        ["L", "130.0", "124.0", "124.0", "79.5", "86.5"],
        ["XL", "136.0", "130.0", "130.0", "80.5", "88.5"],
        ["XXL", "142.0", "136.0", "136.0", "81.5", "90.0"],
    ],
    size_note="All measurements in cm, garment laid flat. Multiply by 0.39 for an approximate inch value.",
    colors=["Chlorophyll Green", "Chalk Beige"],
    sizes=["S", "M", "L", "XL", "XXL"],
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
)

print("done")
