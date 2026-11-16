"""Open the app from disk in headless Chrome and add every size and variant of one family through the picker.

    python3 tools/apptest.py "Check valves"

Reports packs that failed to load, picks that the panel would not take, products with no geometry, and page errors.
Needs playwright (pip) and Chrome; set CHROME if it is not at /usr/bin/google-chrome. Not deployed.
"""
import json
from playwright.sync_api import sync_playwright
import os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
url='file://'+ROOT+'/index.html'
FAM=sys.argv[1] if len(sys.argv)>1 else 'Check valves'
CHROME=os.environ.get('CHROME','/usr/bin/google-chrome')
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME,args=['--allow-file-access-from-files'])
    pg=b.new_page(viewport={'width':1600,'height':1000})
    pg.on('console',lambda m: errs.append(m.text) if m.type in ('error','warning') else None)
    pg.on('pageerror',lambda e: errs.append('PAGEERROR '+str(e)))
    pg.goto(url); pg.evaluate('f=>{window.FAMNAME=f}',FAM); pg.wait_for_function('typeof LIB!=="undefined" && LIB.products && LIB.products.length>0',timeout=20000)
    print('failed packs', pg.evaluate('SDG.failed'))
    print('families', pg.evaluate('LIB.families'))
    ids=pg.evaluate('LIB.products.filter(q=>q.family===FAMNAME).map(q=>q.id)'); print('products',ids)
    pg.get_by_role('button',name=FAM,exact=True).click()
    placed=0; missing=[]
    for pid in ids:
        info=pg.evaluate(f'(()=>{{const q=LIB.products.find(q=>q.id==="{pid}");return [q.sizes,q.variants,q.name]}})()')
        pg.evaluate(f'document.querySelectorAll("#products button.prod")[{ids.index(pid)}].click()')
        for sz in info[0]:
            pg.locator('#sizes button',has_text=sz).filter(has_text=sz).first.click() if False else pg.evaluate(f'(()=>{{for(const b of document.querySelectorAll("#sizes button")) if(b.textContent.trim()==={json.dumps(sz)}) b.click();}})()')
            for v in info[1]:
                pg.evaluate(f'(()=>{{const bs=[...document.querySelectorAll("#variants button")]; const t={json.dumps(v)}.toLowerCase(); for(const b of bs) if(b.textContent.trim().toLowerCase()===t) b.click();}})()')
                st=pg.evaluate('[ui.pick.product,ui.pick.size,ui.pick.variant]')
                if st!=[pid,sz,v]: missing.append((pid,sz,v,st)); continue
                pg.click('#addBtn'); placed+=1; pg.evaluate('selectIds([]); refresh(); panel()')
    print('placed',placed,'mismatch',missing[:5])
    print('items', pg.evaluate('doc.items.filter(i=>i.type==="sym" && LIB.products.find(q=>q.id===i.product).family==="Check valves").length'))
    bad=pg.evaluate('doc.items.filter(i=>i.type==="sym").filter(i=>!lookup(`${i.product}|${i.size}|${i.variant}`)).length')
    print('items without geometry',bad)
    pg.screenshot(path='/tmp/sdg_apptest.png')
    print('errors',errs)
    b.close()
