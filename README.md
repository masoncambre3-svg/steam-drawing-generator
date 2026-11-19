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
  app.js                   the editor: sheet, pipe, fittings, text, dimensions, export
  logo.js                  Spirax Sarco logo (vector) for the product logo option
products/
  index.js                 list of packs in display order (generated)
  steam-traps/<ID>/<ID>.js one product per folder, plus preview.png
  connectors/<ID>/<ID>.js  pipeline connectors and trapping stations
  strainers/<ID>/<ID>.js
  valves/<ID>/<ID>.js
  check-valves/<ID>/<ID>.js
  pumps/<ID>/<ID>.js
  separators/<ID>/<ID>.js
  manifolds/<ID>/<ID>.js
tools/                     the tracing kit used to make packs (not deployed)
```

Pipe, elbows, tees and reducers are drawn by `app/app.js` from ASME dimensions, so they have no pack.

## Adding a product

1. Trace it with the kit in `tools/` (see `tools/README.md`). That writes `products/<family>/<ID>/`.
2. `tools/make_packs.py` rewrites `products/index.js`. If the family has groups in `tools/catalog.json` (Steam traps,
   Pipeline connectors, Check valves), add the new ID to the right group there and run `make_packs.py --index`;
   an ID in no group shows under "Other".
3. Commit and push. Vercel redeploys on push. `app/` does not change.

## Drawing tools

- Dimension: click two points (they snap to product connections and pipe ends and turns), then click where the
  dimension line goes. Aligned, horizontal or vertical. Drag the end handles or the middle handle to adjust.
- Pipe run lengths: tick "Run lengths" on a pipe to label every straight run with its centreline length,
  point to point.
- Lengths read in ft-in, in or mm (Drawing style). ft-in and in round to 1" by default (1/2" and 1/16" are
  options). At 1" and 1/2", pipe runs drawn with the mouse step in that amount.
- Typed pipe lengths: while drawing a pipe, aim with the mouse, type a length (24, 2'-6", 600mm) and press Enter.
  A selected pipe lists every run's length; change one and the rest of the pipe moves with it.
- Grouping: Shift+click or Shift+drag a box to select several items, then Group (Ctrl+G). A group moves, copies,
  rotates and deletes as one. Alt+click edits one item inside a group. Ctrl+A selects everything.
- Equipment (app/equipment.js): U-tube exchanger, open tank with helical coil, air heater coil, jacketed kettle, reservoir
  (pressure powered pump packages: horizontal or vertical, 0-6 top and 0-6 bottom outlets each with its own size, vent out
  of the top or the bottom, threaded or flanged nozzles).
  Not traced: each is drawn from the sizes you type in the panel (nozzle sizes picked from a list), so it matches
  the real unit. Select one and drag the blue diamonds to stretch it. Hidden parts (tube bundle, coil in the tank,
  vessel wall inside the jacket) are dashed. Every nozzle is a connection point. To add another piece of equipment,
  add a builder and an entry to EQUIP in that file; app.js picks it up.
- Pipe turns: "Threaded elbows" (ASME B16.11 Class 3000 forged elbows drawn at each turn, bigger than the pipe, and
  counted in the bill of materials) or "Welded bends" (long-radius bends). Pipes that have never been set use threaded up
  to 2" and welded above; threaded goes up to 4". Threaded 90° elbows and tees are also in Fittings.
- Page size: on a computer the page fills the window and the board takes what is left; smaller or shorter screens get a
  compact layout, and "Hide panel" (toolbar) gives the board the full width.
- Pipe stays connected: a pipe end sitting on a product connection follows the product when it is moved, rotated,
  mirrored, resized or stretched. The run next to the product keeps its direction and the turn before it slides.
  A pipe you move or edit yourself is left where you put it. Changing a run length moves a product on the far end.
- Drop onto a pipe: drag a trap, strainer, valve, reducer or tee onto a pipe run (it highlights), let go, and the
  pipe is cut and both sides connect. It faces the way the pipe was drawn; Mirror (M) turns it round.
- Title block and parts list (side panel): tick "Border and title block" and fill in title, customer, site,
  drawing no., rev, drawn by (remembered), date and notes, with the logo on or off. "Bill of materials on the
  drawing" adds the parts table above the title block; "Item numbers on products" adds numbered balloons that
  match it. The block goes beside or under the drawing, whichever makes a page closer to letter, and is included
  in Copy image, PNG and SVG. Everything is saved with the drawing.
- "Bill of materials list" opens the list on its own: one line per model, size and connection with a count, pipe
  totals by size and schedule (rounded up to the next foot), equipment optional. Copy for Excel or download a CSV.
- Press ? (or the ? button at the end of the toolbar) for the list of keyboard shortcuts.
- Copy and paste: Ctrl+C / Ctrl+X / Ctrl+V (or the Copy and Paste buttons) work across drawings, projects and tabs
  in the same browser. Paste lands in the middle of the view.
- My assemblies: select several items, name them and click "Save as assembly". They show under "My assemblies" in
  the product list; click one to add it as a group. Export / Import moves them to another computer.
- Projects: save drawings by name into projects (kept in the browser). The open drawing saves as you work.
  Export a project to one .json file to back it up or move it; Import or Open reads it back.
- Spirax Sarco logo: tick it on any product, then pick on the body, above or below, and the size.

## Products so far

| Family | Products |
|---|---|
| Steam traps | TD52, TD62M / TD62LM (screwed, and flanged), TDC46M, TD120M (and PN160 / PN250), FT450, FT14 (screwed, PN16, ASME 150, JIS/KS 20K), FTC62 (screwed, SW, PN100, ASME 600), FTC80 (SW / ASME 600, BDV2 or plug), IBV Series C, HM34, BPC32Y, SMC32Y, UFT32, UFT14HC, UBP32, UTDS46M (trap units), UTD52L (on strainer connector), UIB30, UIB30H, UIB45 (on PC10HP), USM90, UTDS90 (4-bolt trap units) |
| Pipeline connectors | STS17.2 SB, DB US, DBB USH, DBB USH DSH (screwed / SW), PC4000 / PC4001 / PC40, PC90 (front and side views, SW / BW / Class 600 / 900), universal strainer connector (RH / LH, plug / blowdown valve) and straight connector (US) |
| Strainers | Fig 16HP, Fig 16L, Fig 34, Fig 34HP, Fig 36, Fig 36HP |
| Valves | A3S / A3SS |
| Check valves | DCV41, DCV10, SDCV44, LCV3/4/6/7 (screwed / SW, ASME flanged, PN flanged), CVS10, Sight Check |
| Pumps | Pressure powered: PTF / PTF-SS (2" x 2", 3" x 2"), PTF Top Inlet (3" x 3"), PTF4 (4" x 4"), PPEC (1", 1-1/2"; iron / steel / 316 SS). Automatic pump traps: APT10, APT14 (screwed, PN16, ASME 150, JIS/KS 10), APT14HC, APT14SHC |
| Separators | S5, S6 (1/2" to 2"), S4A (1/2" to 2" screwed/SW), S4A flanged (2-1/2" to 18") |
| Manifolds | MSC condensate collection, MSD steam distribution (4, 8, 12, 16 stations, with or without stand) |
| Fittings (built in) | 90° elbow, tee, concentric reducer, eccentric reducer (butt weld); 90° elbow and tee, threaded (Class 3000) |
