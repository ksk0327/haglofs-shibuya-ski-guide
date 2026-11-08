# Haglöfs Shibuya — Ski Series Guide (QR product pages)

Static, no-build, no-JavaScript website. Five English-language product pages for the
Haglöfs ski jacket series, meant to be opened by scanning a QR code placed next to each
jacket in the Shibuya store, mainly for inbound (non-Japanese-speaking) customers.

This README is written so it can be handed directly to a local Claude Code session for
deployment. If you are Claude Code reading this: follow "Deploy to GitHub Pages" below,
asking the user to confirm anything that needs their GitHub account.

## What's in this folder

```
ski-series/
├── index.html                     ← landing page: all 5 jackets + a quick-compare table
├── products/
│   ├── vassi-gtx-pro-ii.html
│   ├── vassi-gtx-ii.html
│   ├── alper-proof.html
│   ├── latnja-gtx-insulated.html
│   └── nallo-touring-gtx.html
├── assets/
│   ├── style.css                  ← single shared stylesheet, no framework
│   └── img/                       ← EMPTY — see "Adding real photos" below
├── tools/
│   └── build_products.py          ← regenerates all product pages from structured data
└── README.md                      ← this file
```

No JavaScript is used anywhere. No build step, no npm, no dependencies — these are plain
HTML files that can be opened directly in a browser or served by any static host.

## Important: things to double-check before going live

The product copy, specs, and prices were sourced from the UPLND online store
(https://uplnd.com) product pages, since that was the reference the content owner (建部さん)
provided. Status as of the latest update:

1. **Prices** — confirmed correct against the in-store tags (建部さん, 2026-11). ✅
2. **Alper Proof colorways** — confirmed: Northern Blue / Tarn Blue, Seaweed Green /
   Chlorophyll Green, Teak Brown, True Black. ✅
3. **Latnja GTX Insulated specs** — fully confirmed from the in-store product tag:
   waterproofness (28,000mm), membrane (GORE-TEX® ePE 2-layer), insulation (Mimic
   SILVER, 3-zone mapped), breathability (RET > 13), weight (860g, men's L), full
   size chart (S–XXL, cm), and all 4 colorways (Chlorophyll Green, Chalk Beige,
   Turn Blue, True Black). ✅ All content for this product is now confirmed.
4. All text was rewritten in the Agent's own words from the factual specs (not copied
   verbatim from UPLND's marketing copy, nor from any other source material provided),
   to avoid any copyright concerns. Feel free to adjust tone/wording further.

## Adding real product photos

Every photo slot on every page is currently a dashed placeholder box (so it's obvious
nothing has been swapped in yet). To add real photos:

1. Drop image files into `assets/img/`, named like `vassi-gtx-pro-ii-1.jpg`,
   `vassi-gtx-pro-ii-2.jpg`, etc. (slug matches the HTML filename).
2. In the relevant `products/<slug>.html` file, find the `.gallery` block and replace
   each placeholder `<div class="slide">...</div>` with:
   ```html
   <div class="slide"><img src="../assets/img/vassi-gtx-pro-ii-1.jpg" alt="Vassi GTX Pro II Jacket — front"></div>
   ```
3. Do the same for the small thumbnail on that product's card in `index.html`
   (`.product-card .thumb`).

Make sure whoever supplies the photos has the right to use them (official Haglöfs/brand
assets, or new photos taken in-store) — these were deliberately **not** scraped from the
UPLND reference pages.

## Adding a new product later

Two ways to do this — pick whichever is easier at the time:

**A. Quick/manual:** copy an existing file in `products/` as a starting point, edit the
text, and add a card for it in `index.html`'s `.product-grid` and `.compare` table.

**B. Scripted (recommended for several products at once):** open `tools/build_products.py`,
copy one of the `build(...)` calls near the bottom, change its values for the new product,
and add it to the `ALL_PRODUCTS` list near the top (so it shows up in every other page's
"Compare with other Ski Series jackets" section automatically). Then run:

```
python3 tools/build_products.py
```

This regenerates every file in `products/` from scratch — it's safe to re-run any time.
(`index.html`'s product grid and compare table are not auto-generated; update those by hand.)

## Deploy to GitHub Pages

These steps assume a free GitHub account and the `gh` CLI (or just git + the GitHub
website — either works).

1. **Create the account** (skip if you already have one): go to https://github.com/signup
   and sign up with an email address.

2. **Create a new repository** — e.g. named `haglofs-shibuya-ski-guide`. Easiest via the
   GitHub website: click "+" → "New repository" → give it a name → "Create repository"
   (leave it empty, no README/license, since we already have our own files).

3. **Push these files to it.** From inside this `ski-series/` folder:
   ```
   git init
   git add .
   git commit -m "Initial ski series product guide"
   git branch -M main
   git remote add origin https://github.com/<your-username>/haglofs-shibuya-ski-guide.git
   git push -u origin main
   ```
   (Replace `<your-username>` and the repo name with the real ones. If `git` asks for
   credentials, use a GitHub personal access token as the password, or sign in via the
   `gh` CLI first with `gh auth login`.)

4. **Enable GitHub Pages:** on the repository's GitHub page, go to
   Settings → Pages → under "Build and deployment", set Source to
   "Deploy from a branch", Branch to `main` / `/ (root)`, then Save.

5. **Wait ~1 minute**, then the site will be live at:
   ```
   https://<your-username>.github.io/haglofs-shibuya-ski-guide/
   ```
   Each product page's QR code should point to, e.g.:
   ```
   https://<your-username>.github.io/haglofs-shibuya-ski-guide/products/vassi-gtx-pro-ii.html
   ```

6. **This repository should be public** (GitHub Pages on a free account requires a public
   repo). There's no login/customer data involved, so this is fine — but worth knowing,
   since anyone could technically find the repo on GitHub too (not just via the QR code).

## Generating the QR codes

Once the live URL for each product page is known (step 5 above), a QR code can be
generated for each with any QR generator, or with Python:

```python
import qrcode
qrcode.make("https://<your-username>.github.io/haglofs-shibuya-ski-guide/products/vassi-gtx-pro-ii.html").save("vassi-gtx-pro-ii-qr.png")
```

Repeat for all 5 product URLs. Print each QR code and place it next to its jacket in store.
