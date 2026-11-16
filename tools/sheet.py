"""Render every size of a family on one sheet, to check against the TI tables before handing over.

    python3 tools/sheet.py check-valves /tmp/check-valves      # writes .svg and .png, first variant of each product
    python3 tools/sheet.py check-valves /tmp/cv-all --all      # every variant

Red dots are the connection points. Each row has its own scale (shown under the name).
"""
import json, sys, subprocess, html
import os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args=[a for a in sys.argv[1:] if not a.startswith('--')]
fam=args[0]; R=os.path.join(ROOT,'products',fam)+'/'
cat=json.load(open(os.path.join(ROOT,'tools','catalog.json')))
order=next(f['products'] for f in cat['families'] if f['slug']==fam)
allv = '--all' in sys.argv
def load(pid):
    t=open(R+pid+'/'+pid+'.js').read(); return json.loads(t[t.index('SDG.register(')+13:t.rindex(');')])
rows=[]
for pid in order:
    pk=load(pid); P=pk['product']
    vs=P['variants'] if allv else [P['variants'][0]]
    for v in vs:
        rows.append((P,v,[(sz,pk['symbols'][f"{pid}|{sz}|{v}"]) for sz in P['sizes']]))
W=1800; out=[]; y=10
for P,v,items in rows:
    # common scale per row: fit tallest into 170 px and total width into W
    tw=sum(s['box'][2] for _,s in items)+12*len(items); th=max(s['box'][3] for _,s in items)
    k=min(170/th,(W-260)/tw)
    out.append(f'<text x="10" y="{y+20}" font-size="15" font-weight="bold" font-family="sans-serif">{html.escape(P["name"])}</text>')
    out.append(f'<text x="10" y="{y+38}" font-size="12" font-family="sans-serif">{html.escape(v)} · {P["ti"]}</text>')
    out.append(f'<text x="10" y="{y+54}" font-size="11" fill="#555" font-family="sans-serif">scale {k:.2f} px/mm</text>')
    x=250; rh=th*k+50
    for sz,s in items:
        bx,by,bw,bh=s['box']
        g=[f'<g transform="translate({x-bx*k:.1f},{y+8-by*k:.1f}) scale({k:.4f})">',f'<path d="{s["fill"]}" fill="#5aa0ea"/>']
        for lw,d in s['strokes']: g.append(f'<path d="{d}" fill="none" stroke="#0b2447" stroke-width="{lw}" stroke-linejoin="round" stroke-linecap="round"/>')
        if s['arrow']: g.append(f'<polygon points="{s["arrow"][0]}" fill="#f3f8ff" stroke="#0b2447" stroke-width="{s["arrow"][1]}"/>')
        for p in s['ports']: g.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="{2.2/k}" fill="#e33"/>')
        g.append('</g>'); out+=g
        dims=s['dims']; lab=f'{sz}'
        out.append(f'<text x="{x}" y="{y+18+bh*k}" font-size="12" font-family="sans-serif" font-weight="bold">{html.escape(lab)}</text>')
        dl=' '.join(f'{a}={b}' for a,b in dims.items() if a in ('A','B','C','D'))
        out.append(f'<text x="{x}" y="{y+32+bh*k}" font-size="10" font-family="sans-serif" fill="#333">{html.escape(dl)}</text>')
        x+=max(bw*k,130)+14
    y+=rh+18
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{y}" viewBox="0 0 {W} {y}"><rect width="100%" height="100%" fill="white"/>'+''.join(out)+'</svg>'
name=args[1]
open(name+'.svg','w').write(svg); subprocess.run(['rsvg-convert',name+'.svg','-o',name+'.png'],check=True)
print(name, y)
