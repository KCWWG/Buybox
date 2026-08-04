#!/usr/bin/env python3
"""
check-oms.py  --  run this from the repo root, next to index.html

Compares every OM link in index.html against the PDFs actually on disk and
reports exactly which ones will 404 on Netlify. Case-sensitive, because
Netlify's servers are Linux and Windows/macOS are not -- a file that opens
fine on your laptop can still 404 once deployed.

    python3 check-oms.py
"""
import json, os, re, sys, unicodedata
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "index.html")

if not os.path.exists(INDEX):
    sys.exit("index.html not found -- run this from the repo root.")

html = open(INDEX, encoding="utf-8").read()

m = re.search(r'var OM_BASE = "([^"]*)"', html)
om_base = m.group(1) if m else ""

lb = html.index("const PROPERTIES = [") + len("const PROPERTIES = ")
end = html.index("];", lb) + 1
props = json.loads(html[lb:end])

links = [(p.get("name") or p["address"], p["href"]) for p in props if p.get("href")]

folder = os.path.join(HERE, om_base) if om_base else HERE
print(f"OM_BASE   = {om_base!r}")
print(f"looking in: {folder}")
print(f"OM links  : {len(links)}\n")

if not os.path.isdir(folder):
    sys.exit(f"FOLDER MISSING: {folder}\nEither create it or change OM_BASE in index.html.")

on_disk = os.listdir(folder)
# Normalise unicode so macOS-decomposed filenames still match.
norm = {unicodedata.normalize("NFC", f): f for f in on_disk}
lower = {k.lower(): k for k in norm}

missing, casewrong, ok = [], [], []
for name, href in sorted(links):
    want = unicodedata.normalize("NFC", unquote(href))
    if want in norm:
        ok.append(want)
    elif want.lower() in lower:
        casewrong.append((name, want, norm[lower[want.lower()]]))
    else:
        missing.append((name, want))

print(f"OK              : {len(ok)}")
print(f"CASE MISMATCH   : {len(casewrong)}   <- works locally, 404s on Netlify")
print(f"MISSING         : {len(missing)}\n")

if casewrong:
    print("--- CASE MISMATCH (rename the file on disk to match index.html) ---")
    for name, want, actual in casewrong:
        print(f"  {name}")
        print(f"    index.html wants : {want}")
        print(f"    file on disk is  : {actual}\n")

if missing:
    print("--- MISSING (no file with this name) ---")
    for name, want in missing:
        print(f"  {name}")
        print(f"    expects: {want}")
        stem = want.rsplit(" - ", 1)[0][:18].lower()
        near = [f for f in on_disk if stem and stem in f.lower()]
        if near:
            print(f"    close?  {near}")
        print()

extras = [f for f in on_disk if f.lower().endswith(".pdf")
          and unicodedata.normalize("NFC", f) not in
          {unicodedata.normalize("NFC", unquote(h)) for _, h in links}]
if extras:
    print("--- PDFs on disk that nothing links to ---")
    for f in sorted(extras):
        print(f"  {f}")

sys.exit(1 if (missing or casewrong) else 0)
