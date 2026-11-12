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
│   └── build_products.py          ← single source of truth — see below
└── README.md                      ← this file
```

No JavaScript is used anywhere. No build step, no npm, no dependencies — these are plain
HTML files that can be opened directly in a browser or served by any static host.

## One script drives (almost) everything — `tools/build_products.py`

As of 2026-11-12, running:

```
python3 tools/build_products.py
```

regenerates all three of the following from the same per-product data, so a change only
needs to be made in **one place**:

1. All 5 files in `products/` (full product detail pages).
2. Each product's fit-chart SVG at `assets/img/radar-<slug>.svg` (the 5-axis
   Resort/Powder/Off-piste/Touring/Cold chart).
3. Just the "Which jacket fits your trip?" rows inside `index.html` — the block between
   the `<!-- RADAR_LIST:START -->` / `<!-- RADAR_LIST:END -->` HTML comments. Everything
   else in `index.html` (intro text, the quick-compare table, payment methods) is still
   hand-maintained and untouched by the script.

To change a fit-chart score, a mini-spec chip, a card tag, or similar: find that
product's `build(...)` call in `tools/build_products.py`, edit the relevant keyword
argument (`radar_scores`, `mini_specs`, `card_tag`, `card_name`, `thumb_src`,
`thumb_alt`, `radar_alt`), then re-run the script above. Don't hand-edit the generated
rows inside the `RADAR_LIST:START`/`END` block in `index.html` directly — they'll be
overwritten the next time the script runs.

(This replaced an earlier setup where the fit charts were a one-off script and
`index.html`'s card content was typed by hand in two different places — worth knowing
if you're looking at git history and wondering why those don't exist anymore.)

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
4. **Vassi GTX Pro II colorway** — ✅ confirmed (2026-11-09) by 建部さん against the
   in-store tag: "True Black / Chlorophyll Green" is correct.
5. **bluesign® / PFAS-free DWR claims** — ✅ resolved (2026-11-08): 建部さん decided to
   drop these claims from all 5 pages rather than add them to Alper Proof, since this
   information is already on each product's physical in-store tag and doesn't need to
   be duplicated on the online guide. All "Certification" / "Water repellent finish"
   rows and related bullet points were removed across every product for consistency.
6. **Currency conversion** — ✅ resolved (2026-11-12): no fixed exchange rate is shown
   (rates change daily and a traveler could be from any country, so a hard-coded
   number would go stale or simply not cover their currency). Each product page has
   a small note under the price suggesting the customer search "JPY to [their
   currency]" themselves — needs no upkeep and works for anyone. A fully-automatic
   version (JavaScript fetching a live rate on page load) was discussed and declined
   by 建部さん: it would need the customer's phone to have a working internet
   connection in that moment, and would depend on a free external rate service
   staying available — 建部さん preferred the simpler, dependency-free text hint.
   The note no longer suggests asking staff for the rate (removed 2026-11-12, since
   staff can't know a given visitor's home currency either).
7. **Accepted payment methods** — ✅ added (2026-11-08), based on the store's
   payment-acceptance signage (PAYGATE by スマレジ): credit/debit cards, Japan
   QR/mobile payment (PayPay, d払い, 楽天ペイ, au PAY, メルペイ, WeChat Pay, UnionPay
   QR), and international e-wallets (Alipay+, Alipay, AlipayHK, GCash, Touch 'n Go
   eWallet, TrueMoney). 建部さん confirmed generic pictogram icons (not exact brand
   logos, for trademark reasons) + the text list are fine. Moved to the very bottom
   of the index page (2026-11-11) and shrunk, since it's lower-priority information
   than the product content above it. ✅ resolved (2026-11-12): one icon on the
   original sign (a yellow "Pay" mark) was never confidently identified — likely
   one of the Chinese QR-payment brands, per 建部さん — and was intentionally left
   off the list rather than guessed at. No action needed unless it's identified later.
8. **Tax-free shopping notice** — ✅ added (2026-11-08) to every product page and the
   index page, reflecting Japan's tax-free system reform that took effect
   2026-11-01: customers now pay the tax-included price in store and claim the
   refund at the airport on departure (passport + receipt, within 90 days), rather
   than getting an on-the-spot discount at checkout. Source: Japan Tourism Agency
   (観光庁) — https://www.mlit.go.jp/kankocho/tax-free/page01_000001_00021.html
9. **"Which jacket fits your trip?" charts** — ✅ added (2026-11-08) to the index
   page: a 5-axis chart (Resort / Powder / Off-piste / Touring / Cold) per jacket.
   The 1–5 scores were editorial starting points, then adjusted by 建部さん over
   several rounds to match how staff actually position each jacket — current
   scores: Vassi GTX Pro II [3,5,5,4,2], Vassi GTX II [3,4,4,3,3], Alper Proof
   [3,3,3,3,3], Latnja GTX Insulated [5,2,1,2,5], Nallo Touring GTX [3,3,4,5,1].
   Layout changed (2026-11-11) from a 2-column grid to a single vertical list —
   each jacket's own photo sits directly beside its chart, so it's unambiguous
   which chart belongs to which jacket on a phone screen. Updated again
   (2026-11-12): the separate product-listing grid at the top of the index page
   was removed, and its full card content (photo, tag, name, Japanese name,
   mini-specs) was merged directly into each row of this list, so every jacket
   now appears only once on the page — as one row with its card on the left and
   its fit chart on the right — instead of twice. The same fit chart was also
   added to each individual product page (just below the "Best for" badge),
   since previously it only existed on the index page.
10. **Price wording** — ✅ changed (2026-11-11) from "reference price — please
    confirm in store" (which read as uncertain) to "(tax included) — final total
    confirmed at checkout", a more reassuring phrasing.
11. **Color swatches** — ✅ added (2026-11-11): each colorway chip on a product page
    now shows a small color dot (or a split dot for two-tone colorways) so the
    color is visible without scrolling back up to the gallery photos. Swatch colors
    are approximate (mapped from the colorway name), not exact Pantone matches.
12. **Stock-availability note** — ✅ added (2026-11-11) under the Colors & Sizes
    section on every product page: "please ask staff to confirm what's currently
    in stock," since the site can't show real-time inventory.
13. **Sticky "Ask staff" bar** — ✅ added (2026-11-11): a small bar now stays pinned
    to the bottom of the screen on every product page (not the index page), so the
    "ask any staff member" prompt stays visible no matter how far the customer has
    scrolled down a long product page.
14. All text was rewritten in the Agent's own words from the factual specs (not copied
    verbatim from UPLND's marketing copy, nor from any other source material provided),
    to avoid any copyright concerns. Feel free to adjust tone/wording further.
15. **Japanese jacket names removed** — ✅ changed (2026-11-12): every page previously
    showed the Japanese product name under the English one (`.jp-name`). Since this
    site is for inbound, non-Japanese-speaking customers, 建部さん asked for it to be
    removed everywhere (product pages and the index-page cards). The `name_jp` data
    is still kept in `tools/build_products.py` (harmless, unused) in case it's wanted
    again later — it's just no longer rendered anywhere.
16. **Fit-chart size on product pages** — ✅ enlarged (2026-11-12): the chart was hard
    to make out at its original size next to the much larger product photo above it,
    so it's now shown much bigger (up to 340px, labeled "Fit chart"). The index page's
    charts (next to the small thumbnail) are unchanged.
17. **Index-page thumbnail size** — ✅ enlarged (2026-11-12): the small product photo in
    each "Which jacket fits your trip?" row was increased from 64px to 92px wide (card
    column widened from 54%→58% of the row, chart column 46%→42%, to make room).
18. **Index-page card layout bug** — ✅ fixed (2026-11-12): the thumbnail, tag, product
    name and mini-specs were all direct children of a 2-column CSS grid
    (`.radar-row-card`), so the grid's row-by-row auto-placement put the product name
    underneath the photo instead of next to it (visible once the thumbnail grew —
    建部さん caught this). Fixed by wrapping the tag/name/specs in their own
    `.radar-row-info` container, so the grid only has 2 real columns: photo, then
    text. This freed up room to enlarge the photo again, to 118px.
19. **"Fit chart" label on the index page** — ✅ added (2026-11-12): the small caption
    was already on each product page's chart; now the index page's charts have the
    same label (smaller size, to fit the narrower column), for consistency.
20. **Payment sign's unidentified yellow icon** — ✅ dropped (2026-11-12): per 建部さん,
    likely one of the Chinese QR-payment brands, but can't be confirmed, so it's
    intentionally left off the payment-methods list rather than guessed at.
21. **Cross-checked against the UPLND reference pages** (2026-11-12) — 建部さん asked for
    a pass comparing every product's price/specs/colorways against the live UPLND
    product pages (uplnd.com/products/<style-number>). Results:
    - Vassi GTX Pro II, Vassi GTX II, Nallo Touring GTX: everything matches exactly,
      no changes.
    - **Fixed a real typo:** Latnja GTX Insulated's "Turn Blue" colorway was renamed
      to "Tarn Blue" everywhere (display text, alt text, captions) — "Turn Blue" isn't
      a real Haglöfs colorway name, this was simply a misspelling. Image filenames
      were left as-is (internal only, not shown to customers).
    - **Colors — resolved (2026-11-12):** 建部さん confirmed the colorways already
      shown on this site are the complete, correct set carried in the Shibuya store
      (the extra colorways on UPLND's full online catalog — e.g. Alper Proof's
      "Deep Teal" and "Carmine Red / Tech Red" — are simply not stocked here). No
      changes needed.
    - **Sizes — resolved (2026-11-12):** every product page now shows sizes S–XL only
      (previously some pages also listed XXL). Per 建部さん, whether XXL exists
      depends on the specific item/color and isn't worth tracking per-SKU on this
      site, so the sizes shown are capped at S–XL everywhere and the note under
      "Colors & sizes" was reworded to: "Sizes shown above run S–XL. Some items and
      colors may also be available in other sizes (e.g. XXL) depending on style —
      please ask staff to confirm what's currently in stock." Alper Proof's old
      product-specific "No XXL in this style" wording was removed since the shared
      note now covers it.

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
3. Do the same for the small thumbnail on that product's row in `index.html`
   (`.radar-row-thumb`, inside its `.radar-row-card`).

Make sure whoever supplies the photos has the right to use them (official Haglöfs/brand
assets, or new photos taken in-store) — these were deliberately **not** scraped from the
UPLND reference pages.

## Adding a new product later

Two ways to do this — pick whichever is easier at the time:

**A. Quick/manual:** copy an existing file in `products/` as a starting point, edit the
text, and add a row for it in `index.html`'s `.radar-list` and `.compare` table. You'll
also need a 5-axis fit chart SVG at `assets/img/radar-<slug>.svg` (see the next section).

**B. Scripted (recommended for several products at once):** open `tools/build_products.py`,
copy one of the `build(...)` calls near the bottom, change its values for the new product,
and add it to the `ALL_PRODUCTS` list near the top (so it shows up in every other page's
"Compare with other Ski Series jackets" section automatically). Then run:

```
python3 tools/build_products.py
```

This regenerates every file in `products/` from scratch — it's safe to re-run any time.
Each product page automatically includes its fit chart at `assets/img/radar-<slug>.svg`
(set by the `slug` you give it) — make sure that file exists before regenerating, or the
image will show broken on that page.
(`index.html`'s "Which jacket fits your trip?" list and compare table are not
auto-generated; update those by hand.)

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
