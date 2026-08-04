# Willowood DFW Retail Buy Box

Interactive acquisition dashboard for the Dallas–Fort Worth retail buy box —
46 scored assets, FrontView REIT scoring engine, interactive map, and the 26
Offering Memoranda (OMs) served inline.

This is a **static site**. There is no build step. The whole thing is:

```
index.html        ← the dashboard (self-contained: CSS, JS, data, and the embedded map image)
check-oms.py      ← verifies every OM link matches a real file (run before each push)
*.pdf             ← the 26 Offering Memoranda, loose in the repo root
netlify.toml      ← tells Netlify to serve PDFs inline and publish the repo root
```

There is no `MO/` subfolder. The PDFs sit in the root alongside `index.html`, which is
what `OM_BASE = ""` expects.

---

## Current state — v05 (August 2026)

| | |
|---|---|
| Assets screened | 46 |
| With OM on file | 26 |
| From CoStar / LoopNet only | 20 |
| Size band | 7,000 – 30,000 SF |
| Check size | ≤ $11M ask |

### Changes in this version
- **Added** Calloway Center — 5932-5952 River Oaks Blvd, Fort Worth 76114 (SVN | Trinity Advisors)
- **Added** Custer Four Corners — 1480 N Custer Rd, Allen 75013 (SHOP Companies)

Both trip hard gates under the FVR Default thesis. Neither is a pricing near-miss.

**Custer Four Corners** is the better asset and the worse deal. Real estate scores 8.35 —
44,013 VPD frontage, demographics at the ceiling, e-commerce resistance of 10. It fails on
price. The OM's "100% Leased" claim is overstated: Suite 130 (1,820 SF, 15.65% of GLA) is
a "Pending Tenant" with a lease expiration of `Jan-00`, and its $89,180 of base rent sits
inside the $572,043 NOI backed only by a seller master lease of up to 24 months from
closing. True in-place NOI ex-Suite 130 is roughly $460,096 — a **4.71% going-in cap**
against a 5.85% ask. At $840.76/SF it is the most expensive asset in the set by a wide
margin (prior high was $763.74), underwritten on rents of $46.50–$50.97/SF NNN versus
$30.44 Allen submarket asking. No guarantor entity is disclosed for any of the six leases,
and three of them (Playa Bowls, 4Ever Young, Barrio Burrito Bar) are franchise systems.
The pro forma carries no vacancy factor and no TI/LC or capital reserve. Note also that
Bread Zeppelin — highest rent PSF in the center — signed a 5-year term while every other
tenant signed 10.

**Calloway Center** fails the 3-year WALT floor at 2.1 years occupied-weighted (1.7 years
across total GLA). Three leases totalling 36% of GLA roll by November 2027 on top of the
2,055 SF already vacant. The State Farm tenancy is an independent agent office, not
corporate credit, so `national_credit_pct` is 0 rather than the 14.9% the OM's framing
implies. The 7.60% headline is a proforma that requires leasing the vacancy at $14.00/SF
with full NNN recovery; actual in-place is 5.67% on $121,988. The genuine merit is a
75% mark-to-market — in-place rents average $13.37/SF against $23.47 submarket asking —
but West Fort Worth runs 9.2% vacancy with negative absorption, so treat that gap as a
question rather than an answer.

**Open verification items** carried into the next pass:
- Guarantor entity on all six Custer Four Corners leases. Corporate versus franchisee
  moves `national_credit_pct` and `is_ig` materially.
- Whether Calloway's annual rent escalations exist. The OM asserts them in the highlights
  but shows no bump schedule in the rent roll, so `rent_escalator_pct` is graded at 0.015
  rather than taking the claim at face value.

---

## How the scoring engine works

Everything downstream of the data is derived. Add a property object to
`const PROPERTIES = [...]` in `index.html` and the page recomputes rank, tier,
GO/CAUTION/NO-GO decision, recommended cap band, implied fair value, map pin,
ranking table row, submarket card, plan-of-attack picks, watch/pass lists, and
broker outreach order. Nothing needs to be updated by hand.

Two parallel 1–10 scores, blended 60% Real Estate / 40% Tenant & Lease:

- **Real Estate** — Traffic & Frontage 25% · Demographics & MSA 15% ·
  E-Commerce Resistance 15% · Re-Tenantability 20% · Tenant Diversity 10% ·
  Value Creation 15%
- **Tenant & Lease** — Credit 30% · Lease Structure 15% · WALT 20% ·
  Escalators 15% · Renewal Options 5% · Rent Coverage 15%

Weights are adjustable live in the Investment Thesis panel (§02.5).

**Recommended cap band:** `MAX(5.5, 10.5 − blended × 0.525) ± 25 bps`
**Implied fair value:** `NOI ÷ recommended cap`, where `NOI = sale_price × cap_rate`

### Hard gates (auto NO-GO)
- Traffic under 10,000 VPD
- Trade-area population under 30,000 within 10 miles
- Specialized single-use building with no re-tenant path
- WALT under 3 years
- Non-IG tenant priced more than 50 bps inside the FVR-implied fair cap

---

## Adding a deal

Append an object to `const PROPERTIES` in `index.html`. Six sub-scores are
**derived** from raw fields; six are **hand-graded** and passed straight through.

**Derived — supply the raw input:**

| Field | Drives |
|---|---|
| `traffic_vpd` | Traffic score. Bands at 40K / 25K / 15K / 10K. Use frontage count, not the sum of both roads. |
| `trade_area_pop_10mi`, `median_hhi` | Demographics score. Median, not average — averages run well above median in urban trade areas. |
| `national_credit_pct`, `is_ig` | Credit score. A franchisee LLC is not corporate credit, even when the sign says Domino's. Neither is an independent insurance agent, even when the sign says State Farm. |
| `walt_years` | WALT score. SF-weighted from the rent roll. Weight across total GLA, not leased GLA — unleased suites count as zero. |
| `rent_escalator_pct` | Escalator score. SF-weighted; flat tenants pull it down. A claim in the highlights section is not a bump schedule. |
| `renewal_options` | Options score. |

**Hand-graded 1–10:** `ecommerce_resistance`, `re_tenantability`,
`tenant_diversity`, `value_creation`, `rent_coverage_score`

**Known gap:** the Lease Structure factor is currently hardcoded to 10 for every
asset in `subScores()`. That's 15% of the tenant score handed out as a free
perfect mark regardless of what the lease actually says. Fixing it re-ranks all
46 deals, so it should be one deliberate pass across the full set rather than
patched in one record at a time.

**Second known gap:** the pro forma trap. `cap_rate` and `noi` should always carry the
**actual in-place** figures, never the broker's proforma or "projected Year 1." Two of the
last three OMs led with a proforma cap (Calloway 7.60% vs 5.67% actual; Custer 5.85%
projected vs 4.71% on truly leased space). The engine has no way to detect this — it
trusts whatever `cap_rate` says.

---

## How the OMs work

Each property references its OM as a filename in the `href` field. Because the PDFs are
committed to this repo and deploy with the site, every OM link resolves automatically —
no external hosting, no separate upload. Click any deal in the dashboard and its OM
opens in the popup.

Filenames in `href` are URL-encoded (`%20` for spaces). The file on disk uses
normal spaces.

`OM_BASE` is prepended verbatim to each property's `href` to build its link:

```js
var OM_BASE = "";   // empty = PDFs sit in the repo ROOT, next to index.html
```

Empty means **no prefix**, so links resolve at the site root — `/Harmon Village -OM - LRG (1).pdf`.
That matches how this repo is actually organised: PDFs loose in the root, no subfolder.

If the PDFs ever move into a folder, set it to `"MO/"`. To host them on a separate site,
use a full URL. **The trailing slash matters** — `"MO"` without it produces
`MOHarmon Village...` and every link breaks at once.

### Verifying the links — run this before every push

`check-oms.py` compares every `href` against the files actually on disk:

```bash
python3 check-oms.py
```

It reads `OM_BASE` and looks in whatever location that points at, so it stays correct if
the layout ever changes. It reports three categories: **OK**, **MISSING**, and
**CASE MISMATCH**. The third one matters most — Netlify runs Linux and is case-sensitive, while Windows and macOS are not,
so `1200 Main St OM.pdf` opens fine on your laptop and 404s on the deployed site because
`index.html` asks for `1200 Main St OM.PDF`. It also lists any PDFs in the repo that nothing links to. Exit code is non-zero if anything is wrong, so it can gate a commit.

Thirteen of the 26 filenames are fragile — browser-download `(1)` / `(2)` / `(4)` suffixes,
underscore-for-space substitutions, a double space in `Henderson Crossing  - Cleburne`, and
one uppercase `.PDF` extension. Re-downloading any of these from the broker will almost
certainly produce a different filename. Either rename the file to match `index.html` or
update the `href` — but never guess; run the checker.

### PDFs required for this version

Two OMs are referenced by the new records. Upload them to the repo root with these
exact names:

```
Calloway Center - OM - SVN.pdf
Custer Four Corners - OM - SHOP.pdf
```

If a PDF is missing the popup still opens with the full scorecard — only the
inline preview breaks.

---

## First-time setup (connect repo → Netlify)

1. Create a new repository on GitHub (e.g. `willowood-buybox`) and push these files
   (see "Push to GitHub" below).
2. In Netlify: **Add new site → Import an existing project → GitHub** → pick this repo.
3. Build settings: leave **Build command** empty, set **Publish directory** to `.`
   (a single dot). Click **Deploy**.
4. Netlify gives the site a URL. Rename it under **Site configuration → Change site name**
   if you want `willowoodbuybox.netlify.app`.

After this, **every `git push` auto-deploys** — no more drag-and-drop.

### Push to GitHub

If the repo already exists, this is all you need:

```bash
git add .
git commit -m "v05 — 46 assets, adds Calloway Center + Custer Four Corners (both NO-GO)"
git push
```

First time only:

```bash
git init
git add .
git commit -m "v05 — 46 assets, adds Calloway Center + Custer Four Corners (both NO-GO)"
git branch -M main
git remote add origin https://github.com/<you>/willowood-buybox.git
git push -u origin main
```

---

## Updating later
- **Change data, scoring, or text:** edit `index.html`, commit, push. Live in ~1 min.
- **Add or replace an OM:** upload the PDF to the repo root, make sure the property's
  `href` in `index.html` matches the exact filename, then run `python3 check-oms.py`
  before pushing.
- **Counts in prose — there are FIVE of them, not two.** The engine sets `hero-count`,
  `hero-inrange` and `rank-count` at runtime from `PROPERTIES.length`, but five strings
  are hardcoded and will silently drift. When the asset count changes, search for and
  update every one:

  | String | Location |
  |---|---|
  | `Vol. 05 · August 2026` | hero eyebrow badge |
  | `Forty-six candidates (26 with verified` | hero paragraph |
  | `All 46 Deals` | map section header |
  | `Pipeline (46 deals): 26 with verified` | Data Sources & Methodology |
  | `26 OM-verified deals, directional for the 20` | Data Confidence bullet |

  These four numbers were out of sync with each other for several versions (the site read
  "Forty-two candidates," "All 38 Deals," "37 Assets" and "Pipeline (42 deals)"
  simultaneously). Reconcile all five in the same commit or the drift compounds.

---

## Notes
- Largest PDF is ~11 MB; all are well under GitHub's 50 MB warning threshold. GitHub's
  web uploader caps at 100 files and 25 MB per file per drag-and-drop, which is fine here.
- The DFW map is a real street map embedded directly in `index.html` as base64, so it
  renders everywhere (local file, Netlify, anyone's browser) with no network dependency.
  Pin positions come from a linear lat/lng fit — a new deal needs real coordinates or
  it lands in the wrong place. The two v05 coordinates are geocoded from street address
  and should be eyeballed on the map before you rely on them for drive-time work.
- Opening `index.html` from the local filesystem works, but browsers block inline PDF
  previews under the `file://` protocol. Use the "Open OM in new tab" button, or view
  the deployed site.
