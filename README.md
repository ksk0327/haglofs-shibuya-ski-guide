# Haglöfs Shibuya — Shop Guide (QR product pages)

Static, no-build, no-JavaScript website. English-language product pages for Haglöfs
items carried at the Shibuya store, meant to be opened by scanning a QR code placed
next to each item in store, mainly for inbound (non-Japanese-speaking) customers.

This README is written so it can be handed directly to a local Claude Code session for
deployment. If you are Claude Code reading this: follow "Deploy to GitHub Pages" below,
asking the user to confirm anything that needs their GitHub account.

## Multi-category architecture (added 2026-11-12)

The site started as a single "ski jacket series" guide (5 jackets, one flat list on
`index.html`). It's now a general shop guide that can grow to cover every product type
the store carries, organized as:

- **Top level — `index.html`:** a tile grid, one tile per **category** (product type):
  Jackets, Pants, Base Layers, Mid Layers, Backpacks & Bags. A category with no products
  yet shows as a greyed-out "Coming soon" tile, so the intended final shape of the site
  is visible immediately — it activates on its own once products are added to it.
- **Category pages — `category/<slug>.html`:** one page per category, e.g.
  `category/jackets.html`. Each has a **Men's / Women's tab switch** (pure CSS, no
  JavaScript — two radio buttons styled as pills) showing that gender's products as a
  card + fit-chart list, plus a quick-compare table where defined. A gender with no
  products yet shows a plain "not yet available" message instead of an empty list.
- **Product pages — `products/<slug>.html`:** unchanged in spirit — this is still what
  a QR code points to directly. Each links back up to its own category page (not
  straight to the top-level index), and its "Compare with other ___" section only
  lists products from the *same category* (not the whole site).

Activity use-cases (e.g. "Ski") are **tags** on a product, shown as a small pill, not a
separate category — so a ski jacket lives in exactly one place (`Jackets`), never
duplicated under both "Jackets" and "Ski".

## What's in this folder

```
ski-series/
├── index.html                     ← category tile grid + site-wide info (intro, tax-free, payment)
├── category/
│   ├── jackets.html                   ← populated (5 products)
│   ├── pants.html                      ← "coming soon" until products are added
│   ├── base-layers.html                ← "
│   ├── mid-layers.html                 ← "
│   └── backpacks.html                  ← "
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

No JavaScript is used anywhere (including the Men's/Women's tabs — pure CSS). No build
step, no npm, no dependencies — these are plain HTML files that can be opened directly
in a browser or served by any static host.

## One script drives (almost) everything — `tools/build_products.py`

Running:

```
python3 tools/build_products.py
```

regenerates everything below from one `PRODUCTS` list (one dict per product — see the
top of the script), so adding or changing a product is editing **one place**:

1. Every file in `products/` (full product detail pages).
2. Every product's fit-chart SVG at `assets/img/radar-<slug>.svg`. The 5 axis labels
   depend on the product's `category` — see `AXIS_SETS` near the top of the script
   (Jackets use Resort/Powder/Off-piste/Touring/Cold; Pants, Base Layers, Mid Layers
   and Backpacks each have their own first-draft axis set, easy to rename once real
   products of that type are being added).
3. Every file in `category/` (one per entry in `CATEGORIES`) — the Men's/Women's tab
   list and quick-compare table for that category, built from whichever `PRODUCTS`
   entries have that `category`.
4. Just the category-tile grid inside `index.html` — the block between the
   `<!-- CATEGORY_GRID:START -->` / `<!-- CATEGORY_GRID:END -->` HTML comments.
   Everything else in `index.html` (intro text, tax-free notice, payment methods) is
   still hand-maintained and untouched by the script.

To add a new product: copy one of the `dict(...)` entries in the `PRODUCTS` list near
the middle of `tools/build_products.py`, change its values (including `category`,
`subcategory`, `gender`, `activity_tags`), then re-run the script above. Its product
page, fit chart, and card on its category page all appear automatically — no other
file needs hand-editing. Don't hand-edit the generated blocks inside `category/*.html`
or the `CATEGORY_GRID:START`/`END` markers in `index.html` directly — they'll be
overwritten the next time the script runs.

(This replaced an earlier setup where the fit charts were a one-off script and
`index.html`'s card content was typed by hand in two different places — worth knowing
if you're looking at git history and wondering why those don't exist anymore. The
single-ski-jacket-list version of `index.html` was itself replaced by the
multi-category tile grid on 2026-11-12 — see the architecture section above.)

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
22. **Multi-category architecture** — ✅ built (2026-11-12): 建部さん asked to start
    adding pants, women's items, and non-ski categories going forward. Rather than
    bolting these onto the flat ski-jacket list, the site was restructured first (see
    "Multi-category architecture" near the top of this file): `index.html` is now a
    category tile grid (Jackets / Pants / Base Layers / Mid Layers / Backpacks & Bags),
    each category has its own page with CSS-only Men's/Women's tabs, and
    `tools/build_products.py` generates all of it from one `PRODUCTS` data list. The
    existing 5 ski jackets were migrated in as `category="jackets"`, `gender="mens"`,
    `activity_tags=["Ski"]` (one of them, Nallo Touring GTX, also tagged `"Touring"`)
    with no content changes. The 4 empty categories show as "Coming soon" tiles and
    will activate automatically once products are added to them. Fit-chart axes for
    the 4 not-yet-populated categories (Pants, Base Layers, Mid Layers, Backpacks) are
    first-draft proposals in `AXIS_SETS` — worth a quick review with 建部さん before
    the first real product in each lands, since they're easy to rename now and harder
    to change once a fit-chart score has been set against them.
23. **First 5 pants added — men's ski pants (2026-11-13), DRAFT, pending confirmation.**
    建部さん gave the 5 product names (mirroring the jacket lineup): Vassi GTX Pro II
    Bib, Vassi GTX II Pant, Alper Proof Pant, Nallo Touring GTX Pant, Latnja GTX
    Insulated Pant — all men's. Specs/prices/colorways/size charts were sourced from
    UPLND's reference product pages (model numbers 608576, 608575, 607939, 608335,
    607470) the same way the original 5 jackets were, and **have not yet been checked
    against the physical in-store tags** — treat everything below as a first draft,
    the same way items 1–21 above started out for the jackets.
    - All 5 use `sizes=["S","M","L","XL"]` (XXL dropped from the size rows, per the
      site-wide S–XL rule 建部さん set on 2026-11-12) and the same shared stock-note
      disclaimer as the jackets.
    - **Latnja GTX Insulated Pant** is missing two things no reference source had: a
      cm size chart (the product page currently shows a note asking customers to ask
      staff instead of a table — every other product on the site has a real table, so
      this one stands out and should get real measurements before launch) and a
      confident weight figure (used 632g from Haglöfs' own SE site; UPLND didn't list
      a weight; a different third-party retailer listed 600g). Its listed colorways
      (6 — Chlorophyll Green, Chalk Beige, True Black, Tarn Blue, Woodland Brown,
      Seaweed Green) are UPLND's full online range and, per the pattern already seen
      with the jackets, likely include some colors this store doesn't actually stock —
      needs the same "which of these are really on the shelf" check 建部さん did for
      the jackets on 2026-11-12.
    - ~~No real photos yet for any of the 5~~ — ✅ resolved, see item 24 below: real
      photos and confirmed colorways are now in for all 5 pants.
    - Prices assume the same "(tax included) — final total confirmed at checkout"
      wording as the jackets; not yet checked against the in-store tags either.
    - Alper Proof Pant's shell fabric spec omits a denier number (UPLND's page didn't
      give one for this item, unlike its jacket counterpart's "75 denier") — worth
      checking the physical tag for the real number.

24. **Pants colorways confirmed + real photos added (2026-11-13).** 建部さん sent
    in-store product photos for all 5 pants, one product per message, with the
    instruction that each photo set represents the colors actually carried in this
    store. Each photo's filename embeds the item's Haglöfs color-code suffix (e.g.
    `...2C5` = True Black), which was cross-checked against Haglöfs' own product
    pages / retailer listings for that exact model number:
    - **Vassi GTX Pro II Bib** — True Black, Purple Night, Chlorophyll Green. Exact
      match to the UPLND draft — no colorway change, just real photos added.
    - **Vassi GTX II Pant** — True Black, Tarn Blue, Chalk Beige. Exact match to the
      draft — no colorway change, just real photos added.
    - **Alper Proof Pant** — True Black, Tarn Blue, Seaweed Green confirmed by photo.
      **"Carmine Red" removed** from the colors list — no red pair was among the
      photos sent, so per 建部さん's "this is what's on the shelf" framing it's
      treated as not currently stocked here. (The Tarn Blue confirmation used the
      same color-code suffix, `3N5`, that was separately confirmed as Tarn Blue on
      both the Vassi GTX II Pant for this store and, directly, on Haglöfs' own site
      for this exact Alper Proof Pant model — see sources below.)
    - **Latnja GTX Insulated Pant** — True Black, Tarn Blue, Chalk Beige, Chlorophyll
      Green confirmed by photo (4 of the original 6-color UPLND draft). **"Woodland
      Brown" and "Seaweed Green" removed** — not among the photos sent, so not
      currently stocked here, same reasoning as Alper Proof Pant above.
    - **Nallo Touring GTX Pant** — Chalk Beige, True Black confirmed by photo — exact
      match to the draft (this one only had 2 colors to begin with) — no colorway
      change, just real photos added.
    - All 5 products now have real front/back photos per confirmed colorway, replacing
      every dashed-placeholder gallery and house-icon category-page thumbnail from
      item 23. Weight, size-chart, and denier open questions from item 23 are
      otherwise unchanged and still pending.
    - Sources used to confirm the color-code → color-name mapping: Haglöfs' own
      product pages (`haglofs.com/.../alper-proof-pant-men-6079392C5`, `...-6079393N5`,
      `.../latnja-gtx-insulated-pant-men-6074705S9`, `...-6074705YE`), and retailer
      listings on outnorth.com, mplusstore.es and alpinstore.com for the Vassi/Nallo
      pants.

25. **Pants fit-chart axes unified with jackets (2026-11-13).** 建部さん asked for the
    "ski series" fit charts (jackets + pants) to use the same axes, rather than pants
    having their own separate set. `AXIS_SETS["pants"]` was changed from
    `["Warmth","Breathability","Mobility","Durability","Weather protection"]` to the
    same `["Resort","Powder","Off-piste","Touring","Cold"]` used by jackets. Since
    each pant is the bottom half of a matching jacket model (same shell/insulation
    technology, same use case), each pant's `radar_scores` was set to mirror its
    jacket counterpart exactly rather than re-scored from scratch:
    - Vassi GTX Pro II Bib ← Vassi GTX Pro II Jacket: `[3, 5, 5, 4, 2]`
    - Vassi GTX II Pant ← Vassi GTX II Jacket: `[3, 4, 4, 3, 3]`
    - Alper Proof Pant ← Alper Proof Jacket: `[3, 3, 3, 3, 3]`
    - Latnja GTX Insulated Pant ← Latnja GTX Insulated Jacket: `[5, 2, 1, 2, 5]`
    - Nallo Touring GTX Pant ← Nallo Touring GTX Jacket: `[3, 3, 4, 5, 1]`
    Base Layers / Mid Layers / Backpacks keep their own separate first-draft axes for
    now (item 22) — this change was scoped to the ski series (jackets + pants) only,
    since that's what's live today. Worth revisiting whether those should also unify
    with jackets once real products land in them.

26. **First 8 women's products added — jackets + pants (2026-11-13), DRAFT, pending
    confirmation.** 建部さん gave 8 product names mirroring 4 of the 5 men's model
    families (no Nallo Touring GTX women's item was given): Vassi GTX Pro II
    Jacket/Bib, Vassi GTX II Jacket/Pant, Alper Proof Jacket/Pant, Latnja GTX Insulated
    Jacket/Pant — all women's (`gender="womens"`). She did not say whether she had
    the women's model numbers/specs on hand, so — per her standing instruction to make
    a reasonable assumption and say so when she doesn't answer — these were researched
    directly from Haglöfs' own women's product pages (model numbers 607792, 607798,
    607793, 607816, 607937, 607938, 607471, 607472) the same way the men's lineup was,
    and **have not yet been checked against the physical in-store tags or photos**.
    Several specific assumptions were made and need her review before launch:
    - **Prices were assumed identical to the matching men's item** (e.g. Vassi GTX
      Pro II Jacket Women = ¥126,500, same as the men's version) since Haglöfs
      typically prices men's/women's versions of the same technology the same —
      this has NOT been checked against any women's-specific pricing.
    - **No cm size chart was available** from Haglöfs' women's product pages for any
      of the 8 items (only "model is 174–177cm, wears size M" is given, no body
      measurements) — all 8 show the same "ask staff" fallback note the Latnja GTX
      Insulated Pant (men's) used in item 23.
    - **Sizes shown are capped to `["S","M","L","XL"]`**, matching the site-wide rule
      (item 10 / 2026-11-12) — but Haglöfs' women's sizing actually runs XS–XXL on
      most of these items. Worth confirming with 建部さん whether this store's
      women's stock actually starts at XS rather than S, since that's a real
      difference from the men's line, not just a display simplification.
    - **Waterproofness/breathability figures were assumed identical to the men's
      version's shell technology** wherever the women's product page didn't restate
      them (flagged inline in each item's specs table, e.g. "(assumed)") — several
      Haglöfs women's pages give far less spec detail than the men's pages did.
    - **Colors are a first-draft list** sourced from retailer listings (outnorth,
      alpinstore, snowleader, etc.), not yet confirmed against this store's actual
      stock — needs the same photo-based color confirmation 建部さん did for the
      men's lineup (items 21 and 24) once she can send photos.
    - **No real photos yet** for any of the 8 — each shows the same dashed/house-icon
      placeholder as a new product without photos.
    - Fit-chart (`radar_scores`) for each women's item mirrors its matching men's
      counterpart exactly (same shell/insulation technology, same axes per item 25) —
      e.g. Alper Proof Jacket Women uses the same `[3,3,3,3,3]` as Alper Proof Jacket
      Men.
    - **Self-caught fix while adding these:** the "Compare with other ___ in this
      category" section on every product page was comparing across genders (e.g. a
      women's jacket page would list men's jackets as its comparison set) since the
      category only had one gender in it until now. Fixed so `related_html` filters
      by the product's own gender as well as its category — verified via a visual
      check of the Vassi GTX Pro II Jacket Women page before this fix (showed men's
      jackets in the compare list) and after (shows only the other 3 women's jackets).

27. **Women's model numbers corrected + 6 of 8 items confirmed with real photos, 2
    new Nallo Touring GTX women's items added (2026-11-13, round 2).** 建部さん sent
    real in-store photos for 6 of the 8 draft women's items from item 26, plus 2
    brand-new women's products not in the original list (Nallo Touring GTX
    Jacket/Pant Women — the men's lineup's 5th model family, which she hadn't
    mentioned having in women's sizing until these photos arrived).
    - **Critical model-number fix for all 4 "Vassi family" women's items.** The
      draft model numbers in item 26 (607792, 607798, 607793, 607816) turned out to
      be from an older/different Haglöfs catalog season. Haglöfs' current own site
      lists these same 4 products under different numbers — 608582 (Vassi GTX Pro II
      Jacket Women), 608581 (Vassi GTX Pro II Bib Women), 608578 (Vassi GTX II Jacket
      Women), 608580 (Vassi GTX II Pant Women) — confirmed by cross-checking against
      photo filename prefixes once photos for the other 6 items showed the same
      pattern (filenames are `<model_number><color_code>_..._1440x.webp`, and every
      other item's filename model number matched Haglöfs' current site exactly).
      **Model numbers in `build_products.py` corrected to 608582/608581/608578/608580.**
    - **Photo-recovery gap — now resolved.** The actual in-store photos for these
      same 4 Vassi-family items were lost on our side earlier in this round (a
      technical issue with this chat session, before they could be saved). 建部さん
      resent all 4 batches (22 photos total, front + back per colorway) later the
      same day, and every photo's filename prefix (`608582...`, `608581...`,
      `608578...`, `608580...`) matched the model numbers and colors already
      corrected above exactly — strong independent confirmation that the
      Haglöfs-current-site research was right. All 4 products now have real
      front/back photos wired in, same as the other 6.
    - **Colors corrected for all 4 Vassi-family items** (previous draft guesses were
      wrong — sourced from the wrong catalog season): Vassi GTX Pro II Jacket Women
      is now True Black / Chlorophyll Green, Maroon Trail / Misty Mauve (was True
      Black / Chlorophyll Green, Lantana Pink / Oak Brown). Vassi GTX Pro II Bib
      Women is now True Black, Dew Green, Misty Mauve (was True Black, Woodland
      Brown). Vassi GTX II Jacket Women is now Tarn Blue, Dew Green, Misty Mauve
      (was Teak Brown / Woodland Brown, Dew Green, Misty Mauve). Vassi GTX II Pant
      Women is now True Black, Tarn Blue, Chalk Beige (was True Black, Tarn Blue,
      Woodland Brown).
    - **Real photos added, colors corrected, for 6 confirmed items** — Alper Proof
      Jacket Women (True Black, Teak Brown, Dew Green / Chlorophyll Green, Maroon
      Trail / Misty Mauve — previous draft's "Tech Red / Carmine Red" guess was
      wrong, no red colorway is in store), Alper Proof Pant Women (True Black, Tarn
      Blue, Chlorophyll Green, Maroon Trail — previous "Carmine Red" guess dropped),
      Latnja GTX Insulated Jacket Women (True Black, Tarn Blue, Chalk Beige,
      Chlorophyll Green — fixed from "Seaweed Green"), Latnja GTX Insulated Pant
      Women (True Black, Tarn Blue, Chalk Beige, Chlorophyll Green — "Carmine Red"
      swapped for Chalk Beige, which is what's actually in store). Each item's photo
      was viewed directly to confirm its color before adding it — only one in-store
      photo per color was sent for these 6 items (no separate back-view shot), so
      each of their `images` entries is a single front photo per colorway rather
      than a front/back pair like the men's lineup. (The 4 Vassi-family items, by
      contrast, got full front+back pairs — see above.)
    - **2 new products added — not in 建部さん's original 8-item list:** Nallo
      Touring GTX Jacket Women (model 608334, colors Chalk Beige / Misty Mauve) and
      Nallo Touring GTX Pant Women (model 608336, colors True Black / Chalk Beige),
      completing the 5th model family in women's sizing. Since Haglöfs' women's pages
      for these two didn't restate full specs, weight/waterproofness/breathability
      figures mirror the men's Nallo Touring GTX Jacket/Pant exactly and are flagged
      "(assumed, mirrors men's version)" throughout — same approach as item 26.
    - **Prices still not confirmed in JPY.** No JPY-denominated price could be found
      for any of these 8 items — only DKK (Danish retail), EUR, and GBP listings.
      The existing draft JPY prices from item 26 were kept as-is since they're close
      to a rough DKK→JPY conversion of the newer official listings, but none of this
      round's prices have been checked against this store's actual price tags.

28. **New "Ski" category added on top of Jackets/Pants (2026-11-13).** 建部さん
    pointed out that skiing is Haglöfs' strongest category and asked for a
    dedicated "Ski" tile on the homepage, rather than making the customer think
    of it as "Jackets" and "Pants" separately. Implementation:
    - A brand-new `category/ski.html` page was added, shown first in the "Shop by
      category" grid on index.html (ahead of Jackets, which comes second) since
      she called it out as the flagship category.
    - This is a **cross-cutting activity view**, not a new garment-type category:
      every current jacket and pant already has `"Ski"` in its `activity_tags`, so
      the Ski page pulls in all of them (10 jackets + 10 pants = 20 styles) and
      groups them into "Jackets" and "Pants" subsections, each with its own
      quick-compare table — same Men's/Women's tab pattern as every other
      category page, just with two subsections stacked inside each tab instead of
      one flat list.
    - **Jackets and Pants themselves are untouched and keep showing exactly what
      they did before** — 建部さん specifically asked to keep them as general
      garment-type categories, since she plans to add non-ski items to them later
      (softshell, insulation, etc. for other activities). The new `ski_products_in()`
      helper filters by `"Ski" in activity_tags` on top of the existing category
      filter, so a future non-ski jacket added to the `jackets` category simply
      won't show up on the Ski page — no further changes needed when that happens.
    - The "Compare with other ___ in this category" section on individual product
      pages is unaffected — it's still scoped to the product's own `category`
      field (jackets or pants), not the new Ski grouping.
    - Verified via a full rebuild + tag-balance check + visual check of
      index.html (Ski tile now shows "20 styles", first in the grid) and
      category/ski.html in both Men's and Women's tabs (Jackets section, its
      compare table, then Pants section, then its compare table — all 20 styles
      present, all images and compare-table links resolve correctly).

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
3. If you're adding photos by hand rather than through `tools/build_products.py` (see
   below), do the same for the small thumbnail on that product's row in its category
   page, e.g. `category/jackets.html` (`.radar-row-thumb`, inside its `.radar-row-card`).

Make sure whoever supplies the photos has the right to use them (official Haglöfs/brand
assets, or new photos taken in-store) — these were deliberately **not** scraped from the
UPLND reference pages.

## Adding a new product later

Open `tools/build_products.py`, copy one of the `dict(...)` entries in the `PRODUCTS`
list, and change its values for the new product — most importantly:

- `slug` — used for its URL (`products/<slug>.html`) and its fit-chart file name.
- `category` — must match one of the slugs in `CATEGORIES` (`jackets`, `pants`,
  `base-layers`, `mid-layers`, `backpacks`). This decides which category page it
  appears on and which fit-chart axes it uses.
- `gender` — `"mens"` or `"womens"`. Decides which tab it appears under on its
  category page.
- `activity_tags` — a list like `["Ski"]`, shown as small pills on its card and
  product page. Not a category — just a label.
- `radar_scores` — five 1–5 numbers matching that category's `AXIS_SETS` order.

Then run:

```
python3 tools/build_products.py
```

This regenerates every product page, every category page, every fit-chart SVG, and
the category-tile grid on `index.html` — it's safe to re-run any time. If the new
product is the first one in a category that was previously empty, that category's
"Coming soon" tile on `index.html` automatically turns into a real link.

## Adding a whole new category later

Add an entry to the `CATEGORIES` list (slug, label, blurb) and, if it needs its own
fit-chart axes, an entry in `AXIS_SETS` keyed by that same slug (5 axis names). If you
want a quick-compare table on that category's page, add an entry to `COMPARE_HEADERS`
too and give each of that category's products a `compare` dict with matching keys.
Then add products with that `category` value as above.

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
