# Tracing kit

Python scripts that turn the outline drawing on a Spirax Sarco TI sheet into a product pack.
Needs: Python 3 with `pymupdf`, `opencv-python`, `numpy` (`scikit-image` for raster.py only); and `rsvg-convert` for
previews. apptest.py also needs `playwright` and Chrome.

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
- `universal.py`  universal (two bolt) trap units: UFT32, UFT14HC, UBP32, UTDS46M (trap unit only, one port at the
                  connector face), UIB45 / UIB30 / UIB30H (front view on the PC10HP, in and out at the connector ends),
                  UTD52L (vectorised picture). Also the shared helpers `_chains` (strokes with colour and dash flag),
                  `_pw` (piecewise map), `_finish` (silhouette, box, ports; `hidden` closes gaps without drawing them)
- `connectors.py` STS17.2 trapping stations (four horizontal types) and PC4000 / PC4001 / PC40
- `raster.py`    vectorise a raster TI picture: skeleton to polylines for strokes, filled outer contour for the fill;
                  `render()` for pictures `image()` cannot read (1-bit image masks)
- `manifolds.py`  MSC / MSD manifolds; station count made by repeating 4-station header blocks (see below)
- `separators.py` S5 / S6 (traced; caps keep drawn size, body to H, plugs slid to B and C, nozzles to A) and
                  S4A / S4A-FL (hand-built from helper shapes, all sizes from the TI table)
- `checkvalves.py` DCV41, DCV10, SDCV44, CVS10, Sight Check, LCV (three packs: screwed / SW, ASME flanged, PN flanged)
- `traps2.py`     TDC46M, TD62M-FL (flanged TD62M / TD62LM), TD120M and TD120M-PN, HM34 (raster); flange OD table `OD`;
                  helpers `_rigid` (move a group of chains as one piece, e.g. a flow arrow), `_cut_x` (cut a drawing off at
                  two x values, for welded ends), `_fy_flange` (flange y that still meets the neck)
- `make_packs.py` writes packs, previews, catalog and index
- `sheet.py`      every size of one family on one sheet (`python3 tools/sheet.py check-valves /tmp/cv`), for the check
                  before handing over and for the preview image the user asks for; `--all` every variant, `--only=A,B`
                  just those products
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
  shown), the bare-body side view on p6, and the no-trap MSC. Connectors still without a pack: PC10 / PC10HP on
  their own (TI-P128-10), PC20 (TI-P128-15), PC3_ (TI-P128-02).

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

- Universal traps and connectors (TI-P712-01, P127-01, P187-03, P113-01, P113-03, P614-04-US, P128-22, P128-33),
  2026-11-16:
  - Trap units (UFT14HC, UBP32, UTDS46M) are drawn as the TI draws them, face on the left and body running +x, so they
    are the mirror of UFT32. The port is the outermost face (spigot or gasket), where the TI's length starts.
  - None of these TI drawings are to scale both ways. Set x and y separately, and inside a view set the parts that
    have their own dimension separately (UBP32 spigot to A; UIB connector to D and A, bucket to E and C).
  - UIB45 draws the PC10HP grey, UIB30 draws it dashed. `_chains(..., dashed=True)` keeps dashed strokes and says
    which they are, so the connector can be told apart from the trap and drawn solid.
  - UIB views: parts of the connector that lie on its round body keep their shape (`_on_circle`); its end blocks
    stretch to A. The connector's round body hides the top of the bucket and lip, so those are closed with `hidden`
    lines for the silhouette only.
  - STS17.2 tables give overall sizes (A end face to end face, B centreline to the lowest point), and the arrows on
    the DBB drawings point somewhere else; the table is right (the drawings at the C scale match it). Scale from C,
    stretch only the screwed end pieces (inner end at the start of the end hex, xLi / xRi) for A and the DBB bleed
    end for B. Pieces that only partly lie in the stretch zone must move rigidly (levers, nuts) or the outline
    opens: only chains inside the end piece band (yc +- hb) are stretched.
  - Pages 8 to 12 of TI-P128-22 draw every line as its own path, so chains are single segments; map point by point.
  - Not done from TI-P128-22: DBB USV and DBB USV DSH (p11, p12; the table's A is the overall length over the
    vertical valves' levers and the inlet is on a vertical end), and every flanged version (ASME 150 / 300, PN40),
    which the TI only draws with screwed ends. Flanged would need flanges added at each end (and the DBB bleed end).
  - PC4000 / PC4001: the only complete view is the side view with the pipe end on. In and out are the same point
    (the app then offers no drop inline); a third port is the trap connector face. The PC4001 sheet hides a copy of
    the bypass valve under the white body: drop black (grey 0) strokes inside the body.
  - UTD52L (TI-P614-04-US) is a raster picture. `raster.py` vectorises it; mask dimension lines, centre lines and
    lettering first (white boxes), use thresh 170 because some edges are drawn grey. The connector face to face is
    not in the TI; it is measured from the picture. Its connector is sold separately (TI-2-519-US).
  - Families can be reordered in catalog.json; Pipeline connectors sits after Steam traps.
  - App test: `apptest.py "Steam traps"` placed 65, `apptest.py "Pipeline connectors"` placed 30, no errors.

- TD traps, HM34, 4-bolt traps and connectors (TI-P187-04, P068-20, P150-11, 2-404-US, P805-01, P804-01, P806-01,
  P127-03-US), 2026-11-16:
  - TI-P068-08 (TD62M / TD62LM screwed / SW) was attached too; that is the existing TD62M pack and was not changed.
    It only lists "screwed"; SW has the same outline and could be added as a second variant.
  - Flanged traps: a flange chain is one whose bbox lies outside the flange back (allow 0.4 pt: the TD62M flange back
    edge is drawn slightly skew). Flange y is scaled to the real OD, but `_fy_flange` keeps the body scale up to the neck
    joint so neck and flange still meet. Flange OD from B16.5 / EN 1092-1 / JIS B 2220 (`traps2.OD`).
  - Flange thickness is not in any of these TIs. TDC46M and TD120M keep it in proportion to the drawn flange and let the
    necks take up the rest of the length. TD62M-FL has almost no neck, so its body keeps its drawn width and the flange
    takes up the rest of B (that comes out close to B16.5 thickness plus raised face: 600 thicker than 300).
  - TD120M BW / SW: the TI draws the flanged trap only; `_cut_x` cuts the necks at the TI's B extension lines and the
    end is closed with a short line. PN160 / PN250 have no DN20, so they are a second pack (TD120M-PN).
  - Several TIs merge table cells (TD120M A, B1, PN250 B2; TDC46M B). The rendered page shows which rows a value spans.
  - HM34 (TI-2-404-US) is a 1-bit CCITT image mask: `raster.image()` cannot read it, so `raster.render()` renders the area
    at the picture's own resolution (765 px across). The outer wall on the picture has a break (x 200, y 546-578);
    `HM34_FIX` paints it in before vectorising. Crop with at least the silhouette `close` (27 px) of white margin round
    the drawing: `cv2.morphologyEx` treats the image edge as filled and the fill runs out to the crop edge otherwise.
    The picture is not to scale (x 0.30 mm/px, y 0.24-0.25), so x is set from A and y from F and G.
  - USM90 / UTDS90: the trap's spigot is about 5 mm below the PC90 pipe centreline. The port is put at the pipe
    centreline, read from the TI's third view (trap on its connector, same y as the side view), so a trap snaps onto the
    PC90 side view's trap face and lines up as the TI shows. UTDS90's B and C cannot both be met at one y scale.
  - PC90: front view flow is right to left (TI arrow), so in is the right end and out is at x = -A. Drop-inline handles
    it (it flips the product so in faces upstream); tested both pipe directions. Class 600 / 900 weld neck flanges are
    built from B16.5 (`connectors.WN`); the TI's B for flanged is exactly OD/2 + 77, which checks the diameters.
  - PC90 side view: the flange circle is drawn only where it is not behind the body (`hidden` closes the fill).
  - TI-P127-03-US: every line is its own tiny path (about 1,000 per view), drawn at 0.21 pt; pieces do not quite meet,
    so `_finish(..., close=10)` (new optional argument, default 3 as before). Leaders inside a view are dropped by
    size, not just by box, because the plug's own short edges sit inside the leader's box. Stray dots are left out
    when finding the end faces (one sat beyond the right face and moved the outlet port).
  - Fix (later the same day): UPC-ST came out with its body short of both ports (about 4 mm a side on 1/2", 20 mm on
    1"). Each end face on p3 is one straight segment, so only its two end points exist, and the end face search trimmed
    the band (+0.5 / -1.5 pt) and threw both away. The straight view now keeps the band's edges. Lesson: when finding a
    face from points in a band, check a long straight face still has a point inside it, and compare every finished
    size's box with its ports on the sheet (the red dots), not just the A label.
  - Not done: the PC90 BD adaptor's own shape (drawn as the blank cap, 2 mm shorter as the table gives), the universal
    connectors' end views, UTD52H / UTD52SL / UTD52SH (TI-P017-12-US, not attached), and a socket weld variant for the
    old TD62M pack.
  - App test: `apptest.py "Steam traps"` placed 122, `apptest.py "Pipeline connectors"` placed 88, no errors. Also
    tested in the page from disk: drop-inline for every new inline product in both pipe directions (in upstream, both
    pipes joined), and USM90 / UTDS90 / UTDS46M snapping onto the PC90 side view trap face.

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
