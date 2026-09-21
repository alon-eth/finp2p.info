#!/usr/bin/env python3
"""Render one 1200x630 share image per page into src/og/. Needs Chrome; run locally after copy or
data changes, then commit the PNGs. Vercel only copies them. Usage: python3 tools/make-og.py"""
import json, subprocess, tempfile, html, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; DATA=ROOT/'data'; OUT=ROOT/'src'/'og'; OUT.mkdir(parents=True,exist_ok=True)
CHROME=next((p for p in ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',shutil.which('google-chrome') or '',shutil.which('chromium') or ''] if p and Path(p).exists()),None)
assert CHROME, 'no Chrome found'
G=json.load(open(DATA/'graph.json')); APPS=json.load(open(DATA/'apps.json'))
insts=len(G['institutions']); edges=len(G['edges']); srcs=len({r for i in G['institutions'] for r in i['refs']})
prod=sum(1 for a in APPS if a['status']=='production'); sand=sum(1 for a in APPS if a['status']=='sandbox'); dev=sum(1 for a in APPS if a['status']=='development')
co=len({a.get('companyName') for a in APPS if a.get('companyName')})
PAGES=[
 ('home','Ownera’s FinP2P network, mapped and sourced','The network that connects the whole RWA ecosystem.',
  f'{len(APPS)} SuperApps, {insts} named institutions, every connection derived and every claim sourced.'),
 ('how-it-works','How it works','Every institution runs its own Router.',
  'Three diagrams: the shape of the network, one transaction end to end, and where a data utility plugs in.'),
 ('network','Every connected piece','The FinP2P puzzle, with the real names filled in.',
  f'{insts} institutions, {len(APPS)} apps, plus the chains, standards, cash rails and custody underneath. Each with a source.'),
 ('map','Interactive map','Every SuperApp on the store, drawn.',
  f'{len(APPS)} apps, {edges} derived connections, {insts} institutions. Value chain, network and institution views.'),
 ('apps','Catalog','Every SuperApp on the store.',
  f'{len(APPS)} apps from {co} companies: {prod} in production, {sand} in sandbox, {dev} in development.'),
 ('institutions','Directory','Banks and institutions on FinP2P.',
  f'{insts} organisations publicly attached to a SuperApp, every one with a citation.'),
 ('sources','Evidence','Every claim, tied to a public document.',
  f'{srcs} sources behind finp2p.info, listed once, with the institutions that rely on each.'),
 ('about','About','An independent reference for the FinP2P network.',
  'Maintained by the Draper Goren Blockchain venture studio. Not operated, reviewed or endorsed by Ownera.'),
 ('build','Build with us','Building a SuperApp, or building for the network?',
  'Draper Goren Blockchain co-founds and backs the companies that make tokenized markets work.'),
]
TPL="""<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400&family=DM+Sans:wght@400;600&display=swap">
<style>html,body{{margin:0;width:1200px;height:630px;background:#0F1413;color:#F2F5F3;font-family:'DM Sans',system-ui,sans-serif;overflow:hidden}}
.w{{position:relative;width:1200px;height:630px;padding:72px 80px;box-sizing:border-box}}
.brand{{font:400 30px 'Fraunces',Georgia,serif}}.brand i{{font-style:normal;color:#3ED08F}}.tag{{font:600 14px 'DM Sans';letter-spacing:.16em;text-transform:uppercase;color:#8A9591;margin-left:16px;vertical-align:middle}}
.eye{{margin-top:104px;font:600 18px 'DM Sans';letter-spacing:.16em;text-transform:uppercase;color:#3ED08F}}
h1{{margin:22px 0 0;font:400 {size}px/1.06 'Fraunces',Georgia,serif;letter-spacing:-.01em;max-width:1000px}}
.sub{{margin-top:28px;font-size:23px;color:#B7C0BC;max-width:940px;line-height:1.4}}
.dots{{position:absolute;right:80px;top:60px;display:flex;gap:16px}}.dots i{{width:22px;height:22px;border-radius:50%;display:block}}
.line{{position:absolute;left:80px;right:80px;bottom:60px;height:1px;background:#2A3330}}
</style><div class="w">
<div><span class="brand">FinP2P<i>.info</i></span><span class="tag">Independent network map</span></div>
<div class="dots"><i style="background:#E0B25A"></i><i style="background:#6C9BF2"></i><i style="background:#E06C6C"></i><i style="background:#3ED08F"></i><i style="background:#C98BD9"></i></div>
<div class="eye">{eye}</div><h1>{h1}</h1><div class="sub">{sub}</div><div class="line"></div></div>"""
tmp=Path(tempfile.mkdtemp())
for slug,eye,h1,sub in PAGES:
    size=72 if len(h1)<46 else 62 if len(h1)<62 else 54
    f=tmp/f'{slug}.html'; f.write_text(TPL.format(size=size,eye=html.escape(eye),h1=html.escape(h1),sub=html.escape(sub)))
    subprocess.run([CHROME,'--headless=new','--disable-gpu','--hide-scrollbars','--force-device-scale-factor=1',
        '--window-size=1200,630',f'--screenshot={OUT}/{slug}.png','--virtual-time-budget=6000',f.as_uri()],
        check=True,capture_output=True)
    print('wrote', (OUT/f'{slug}.png').relative_to(ROOT))
shutil.copy(OUT/'home.png', ROOT/'src'/'og.png')   # legacy path, kept for links already shared
