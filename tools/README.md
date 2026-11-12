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
- `separators.py` S5 / S6 (traced; caps keep drawn size, body to H, plugs slid to B and C, nozzles to A) and
                  S4A / S4A-FL (hand-built from helper shapes, all sizes from the TI table)
- `make_packs.py` writes packs, previews, catalog and index
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

## Conventions the app relies on

- Symbol key: `ID|size|variant`, sizes written like `3/4"` and `1-1/2"`.
- `ports`: inlet first, outlet second. A third port with a direction in degrees is a drain (strainer cap).
- Default color is blue; the app recolors, so packs carry geometry only.
- Flanged products: flange diameter from ASME B16.5 when the TI does not give it. Say so in `note`.
