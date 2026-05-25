[README.md](https://github.com/user-attachments/files/28229745/README.md)
# Willowood DFW Retail Buy Box

Interactive acquisition dashboard for the Dallas–Fort Worth retail buy box —
38 scored assets, FrontView REIT scoring engine, interactive map, and the 18
Offering Memoranda (OMs) served inline.

This is a **static site**. There is no build step. The whole thing is:

```
index.html        ← the dashboard (self-contained: CSS, JS, and the embedded map image)
MO/               ← the 18 Offering Memorandum PDFs (linked from each property)
netlify.toml      ← tells Netlify to serve PDFs inline and publish the repo root
```

---

## How the OMs work
Each property in `index.html` references its OM as `MO/<filename>.pdf`. Because the
`MO/` folder is committed to this repo and deploys with the site, every OM link
resolves automatically — no external hosting, no separate upload. Click any deal in
the dashboard and its OM opens in the popup.

If you ever move the PDFs elsewhere, open `index.html`, find the line:
```js
var OM_BASE = "";   // empty = OMs live in this same repo under MO/
```
and set it to the new base URL (with a trailing slash). Leaving it empty keeps them local.

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

---

## Updating later
- **Change data, scoring, or text:** edit `index.html`, commit, push. Live in ~1 min.
- **Add or replace an OM:** drop the PDF into `MO/`, make sure the property's `href`
  in `index.html` matches the exact filename, commit, push.

---

## Notes
- Largest PDF is ~11 MB; all are well under GitHub's 50 MB warning threshold.
- The DFW map is a real street map embedded directly in `index.html`, so it renders
  everywhere (local file, Netlify, anyone's browser) with no network dependency.
