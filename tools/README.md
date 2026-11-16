# Tracing kit

Python scripts that turn the outline drawing on a Spirax Sarco TI sheet into a product pack.
Needs: Python 3 with `pymupdf`, `opencv-python`, `numpy`; and `rsvg-convert` for previews.

## Start of a session

1. Get this folder (clone the repo, or unzip the kit the user attaches).
2. The user attaches the TI PDFs for that day's product line. Point `sources.py` at them.
3. Agree the exact models, sizes and connection types before tracing.

## How a product is traced

1. Find the dimension drawing page in the PDF. Check it is vector: `page.get_drawings()` returns strokes.
   If the sheet only has a raster picture (FT450, the US-series strainers), it cannot be traced; redraw by
   hand from the picture and the table, and say so in the product `note`.
2. `ti_trace.collect(pdf, page, clip, outline_lw)` pulls the linework inside a clip box (PDF points).
   Pick the clip so dimension lines, leaders and centre lines fall outside it or are dropped.
   `refgrid.py`-style renders with a labelled grid make this quick: render the region, read coordinates.
3. Map drawing coordinates to millimetres from the TI table. Origin is the inlet connection on the pipe
   centreline, x with the flow, y down. Every size must come out at its table dimensions; check them.
   TI sheets usually have one outline for all sizes, so:
   - scale along the pipe to the face-to-face length
   - stretch or slide the parts that have their own dimension (height, cap depth, handwheel)
   - keep round things round (scale them uniformly as a unit)
4. `ti_trace.assemble(...)` finds the filled silhouette and returns fill + strokes.
5. Add the product to a module here and a builder in `make_packs.py`, then run
   `python3 tools/make_packs.py <family>/<ID>`. That writes the pack, a preview, and `products/index.js`.
6. Render a sheet of every size and look at it before handing over. Check widths and heights against the table.

## Files

- `ti_trace.py`   read vector linework from a PDF page, find the silhouette, helper shapes
- `symbols.py`    steam traps (TD52, TD62M, FT450, IBV-C, BPC32Y, SMC32Y)
- `strainers.py`  Fig 16HP, 16L, 34, 34HP, 36, 36HP; cap slides along the leg to hit dimension B; drain port
- `valves.py`     A3S / A3SS; handwheel scaled as a unit to dimension C
- `pumps.py`      Pivotrol PTF and PTF Top; nozzles and check valves scaled as a unit to dimension A
- `universal.py`  UFT32 trap unit (traced, x to A, y to B, connector centreline at C; one port at the connector face)
- `manifolds.py`  MSC / MSD manifolds; station count made by repeating 4-station header blocks (see below)
- `separators.py` S5 / S6 (traced; caps keep drawn size, body to H, plugs slid to B and C, nozzles to A) and
                  S4A / S4A-FL (hand-built from helper shapes, all sizes from the TI table)
- `checkvalves.py` DCV41, DCV10, SDCV44, CVS10, Sight Check, LCV (three packs: screwed / SW, ASME flanged, PN flanged)
- `make_packs.py` writes packs, previews, catalog and index
- `sheet.py`      every size of one family on one sheet (`python3 tools/sheet.py check-valves /tmp/cv`), for the check
                  before handing over and for the preview image the user asks for
- `apptest.py`    opens index.html from disk in headless Chrome (playwright) and adds every size and variant of one family
                  through the picker; reports load failures, picks the panel would not take and page errors
- `catalog.json`  families and product order shown in the app
- `sources.py`    where the source PDFs are for this session

## Notes from earlier sessions

- Some sheets (the PTF pump pages) leave a dash pattern set on ordinary outline strokes. Pass
  `short_dash_solid=True` to `collect` so short phase-0 pieces are kept and real dashed lines are dropped.
- Leaders and centre lines that sit inside the outline need explicit `drop` boxes.
- Not traced yet from TI-P207: PTF Top T-Bone (p885, the elevation shows the tee end-on), PTF4 (p901, vector,
  many leaders cross the tank), PTF-HP (p891) and PTF-HTF (p896), whose drawings do not come out of
  `get_drawings()` and need a closer look.

- S5 and S6 sheets carry the same outline at different scales. `separators.py` moves the S6 linework into the S5
  frame (`K6`, `O6`) so one set of landmarks works for both. The S6 cap leaders sit in different spots, see `DROP6`.
- Screwed / SW / BW versions of a flanged-only drawing: cut the nozzle off at the hub where the TI's
  "A Scrd" extension line sits, and close the end with a short line.
- Some sheets draw the outline as filled shapes instead of strokes (S4A 8"-18", TI-P139-03-US). `collect()` only
  reads strokes, so those are redrawn by hand. Check `Counter(d['type'] for d in page.get_drawings())` first:
  lots of `'f'` and few `'s'` means filled outlines.
- Product variants are one list per product, the same for every size. A product whose connections change with size
  (S4A: NPT/SW up to 2", flanged from 2-1/2") has to be split into two packs.
- When checking a pack against the TI table, the fill runs to the outer edge of the stroke and `box` adds another
  half line. Centreline size = box minus two line widths.
- The ports list can carry more than three connections; extras (vent, motive, exhaust) have no direction.
- MSC / MSD (TI-P115-03-US): traced from the 12-station front elevations, p7 and p8, left (no stand) and right
  (with stand) drawings. Every line on those pages is 0.5 pt, so outline vs detail can't be split by width; all of
  it goes in. Station count: the linework is cut into head / one 4-station block / tail at heights just below the
  header joints (only straight header walls cross them; `_band` clips lines and keeps curves whole), then
  N = head + (N/4 - 1) blocks + tail. Scale: one block = 2 x B from the TI table (210 MSC, 160 MSD).
- The p7-8 drawings are "reference only" and the with-stand drawings disagree with their own overall height
  (65", 64-3/4"). The stand leg is cut and moved so the 12-station overall matches the TI number.
- Very dense sheets (p7 has 18,000 strokes, mostly near-zero pieces) make huge packs. `manifolds.simplify()`
  flattens each chain and runs Douglas-Peucker at 0.25 mm, and `parts(..., dec=1)` writes one decimal. That took
  MSC from about 5 MB to 1.6 MB with no visible change. Use both for any big assembly drawing.
- `parts()` passes any extra product keys through. `sizeLabel` (e.g. "Stations", "Model") and `variantLabel`
  change the panel labels in the app.
- app/logo.js is the vector logo from the cover of TI-P146-05 (11 filled paths, nonzero fill). Any TI cover has
  the same logo if it ever needs redoing.
- Still to do from TI-P115-03-US: 1-1/2" header and Class 300 flanges (only the drawn 2" Class 150 flange is
  shown), the bare-body side view on p6, and the no-trap MSC. UFT32 connectors (PC10HP, PC20, PC3_, PC4_)
  need TI-P128.

- Check valves (TI-P601-18, P601-32-US, P154-10-US, P029-16, P029-21, P022-01), 2026-11-16:
  - Read landmarks (faces, centreline, extents) from the vectors, not from a refgrid picture: print each collected chain's
    bbox (`np.vstack([T.flat(sg) for sg in segs])`). Reading the grid picture was off by several points more than once.
  - `collect()` only keeps a chain whose bbox sits inside the clip (+0.5 pt). A top edge drawn in one stroke with a
    dimension extension line drops out silently (SDCV44 top at y 624.7; LCV flanged left raised face at x 327.25).
    Compare the collected extents with the picture before mapping.
  - Several of these drawings are not to scale (DCV10: the face to face comes out 30% short if x and y share a scale).
    Scale along and across the pipe separately and set each from the table.
  - Wafer and sanitary valves (DCV10, SDCV44, CVS10) are drawn with the flow up the page. They are turned with
    X = (y_inlet - y) * k, Y = (x - x_centre) * k (a true rotation, not a mirror), so the TI flow arrow ends up pointing +x.
  - SDCV44 radii are mapped piecewise (bore C, recess D, body A from the table); the hinge pin and plug stay round.
  - Sight Check: the TI drawing cannot hit B and C at once (the tube would run into the body). A, B and D are exact; the
    tube and cap are one piece scaled to fit B, so C comes out short. Said in the product note.
  - CVS10: clamp lips keep their drawn shape and the body between them stretches to A (the 1/2" is 40 long and 25 across).
  - LCV table on p10 has merged cells. Check which rows a value spans from the word positions
    (`page.get_text('words')`, compare y with the row labels): ASME 125 and ASME 150 7-1/4" covers 1/2" to 1".
  - Packs cannot have a different variant list per size (`variantsFor` exists only for the built-in fittings in app.js),
    so LCV is three packs: screwed / SW (1/2"-2"), ASME flanged (no 1-1/4"), PN flanged (1/2"-4" incl. 1-1/4").
  - The product button shows `name.split(" /")[0]`; keep that part different for every product in a family.
  - LCV flanged: flange chains (by x range) scale about the centreline to the flange OD (ASME B16.5, EN 1092-1); the body
    scales with A below the neck and stretches above it so the bolt tops land on B.
  - Not done from these sheets: LCV with JIS / KS flanges, DCV10 PN25 (no dimensions on the US sheet), the SDCV44 and
    DCV10 end elevations.
  - App test: `python3 tools/apptest.py "Check valves"` placed all 109 symbols with no errors. After each add it calls
    `selectIds([]); refresh(); panel()` so the picker comes back (Escape does not reset it).

## Conventions the app relies on

- Symbol key: `ID|size|variant`, sizes written like `3/4"` and `1-1/2"`.
- `ports`: inlet first, outlet second. A third port with a direction in degrees is a drain (strainer cap).
- Default color is blue; the app recolors, so packs carry geometry only.
- Flanged products: flange diameter from ASME B16.5 when the TI does not give it. Say so in `note`.

## Editor notes (sticky pipe, drop-inline, assemblies)

- Sticky connections are worked out from positions, not stored links: `takeSnap()` records every product's
  connection points and every pipe's points at each commit/load; `reconnect()` moves pipe ends that were on a
  connection that has since moved. A pipe whose points changed for any other reason is left alone. Tolerance is
  0.6 mm (`CTOL`), so pipe ends must be snapped exactly onto connections (snapping already does this).
- Drop-inline uses the first two ports of a product as in and out. It only offers itself when those two are
  straight through (the line between them is horizontal or vertical in the pack's own coordinates) and the product
  has at most 3 ports. **Keep "in" then "out" as the first two ports in every new pack** so new products get it.
- Mirror swaps in and out in place for products whose in and out are level (same y in the pack), so an inline
  product stays on its pipe.
- Assemblies (`sdg-assemblies`) and the clipboard (`sdg-clip`) are in localStorage with positions relative to the
  middle of what was saved. A product missing from the library on paste is skipped with a warning.
- The shortcuts sheet (? key) is built from the KEYS list in app.js. Add a line there whenever a shortcut is added
  to the keydown handler.
