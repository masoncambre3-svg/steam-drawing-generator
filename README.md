# Steam Drawing Generator

Schematic editor for steam and condensate systems. Place Spirax Sarco products, draw pipe between them
at true scale, add labels, and export the drawing for a report.

It is a plain static site: no build step, no server, no login. Open `index.html` from disk, or host the
folder on Vercel or any static host. Nothing is sent anywhere; drawings are saved in the browser and as
files you download.

## Folder layout

```
index.html                 the page (markup only)
app/
  app.css                  styling
  loader.js                loads the product packs, then the editor
  app.js                   the editor: sheet, pipe, fittings, text, export
products/
  index.js                 list of packs in display order (generated)
  steam-traps/<ID>/<ID>.js one product per folder, plus preview.png
  strainers/<ID>/<ID>.js
  valves/<ID>/<ID>.js
  pumps/<ID>/<ID>.js
  separators/<ID>/<ID>.js
tools/                     the tracing kit used to make packs (not deployed)
```

Pipe, elbows, tees and reducers are drawn by `app/app.js` from ASME dimensions, so they have no pack.

## Adding a product

1. Trace it with the kit in `tools/` (see `tools/README.md`). That writes `products/<family>/<ID>/`.
2. `tools/make_packs.py` rewrites `products/index.js`.
3. Commit and push. Vercel redeploys on push. `app/` does not change.

## Products so far

| Family | Products |
|---|---|
| Steam traps | TD52, TD62M / TD62LM, FT450, IBV Series C, BPC32Y, SMC32Y |
| Strainers | Fig 16HP, Fig 16L, Fig 34, Fig 34HP, Fig 36, Fig 36HP |
| Valves | A3S / A3SS |
| Pumps | PTF / PTF-SS (2" x 2", 3" x 2"), PTF Top Inlet (3" x 3") |
| Separators | S5, S6 (1/2" to 2"), S4A (1/2" to 2" screwed/SW), S4A flanged (2-1/2" to 18") |
| Fittings (built in) | 90° elbow, tee, concentric reducer, eccentric reducer |
