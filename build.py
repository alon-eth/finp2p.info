#!/usr/bin/env python3
"""finp2p.info static build. Pure stdlib. `python3 build.py` writes dist/. Pages share one chrome; the
explainer and map bodies are the artifact HTML files with their <title>/<style> hoisted into the head."""
import json, re, html, shutil, datetime
from pathlib import Path
ROOT=Path(__file__).parent; SRC=ROOT/'src'; DIST=ROOT/'dist'; DATA=ROOT/'data'
G=json.load(open(DATA/'graph.json')); APPS=json.load(open(DATA/'apps.json')); TYPES=json.load(open(DATA/'types.json')); CATS=json.load(open(DATA/'categories.json'))
SITE='https://finp2p.info'; TODAY=datetime.date.today().isoformat(); DATA_DATE=G.get('generated','2026-09-20')
NAV=[('/', 'Home'),('/how-it-works/','How it works'),('/network/','Network'),('/map/','Map'),('/apps/','Apps'),('/institutions/','Institutions'),('/sources/','Sources'),('/about/','About')]
BASE_CSS = """
:root{--ground:#F6F4EE;--paper:#FFFFFF;--ink:#17211F;--muted:#5C6865;--faint:#9AA39F;--line:#D8D3C6;--accent:#0C8F57;--accent-soft:rgba(12,143,87,.10);--warm:#B7791F;--warm-soft:rgba(183,121,31,.12);
 --serif:'Newsreader',Georgia,serif;--sans:'Instrument Sans','Helvetica Neue',Arial,sans-serif;--mono:'JetBrains Mono',ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ground:#0F1413;--paper:#161C1B;--ink:#EEF1EE;--muted:#9FAAA5;--faint:#6B7571;--line:#2A3331;--accent:#3ED08F;--accent-soft:rgba(62,208,143,.13);--warm:#E0A94A;--warm-soft:rgba(224,169,74,.14)}}
:root[data-theme="dark"]{--ground:#0F1413;--paper:#161C1B;--ink:#EEF1EE;--muted:#9FAAA5;--faint:#6B7571;--line:#2A3331;--accent:#3ED08F;--accent-soft:rgba(62,208,143,.13);--warm:#E0A94A;--warm-soft:rgba(224,169,74,.14)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--ground);color:var(--ink);font:16px/1.6 var(--sans)}
a{color:var(--accent)}
.site-nav{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--ground) 92%,transparent);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.site-nav .in{max-width:1240px;margin:0 auto;padding:0 20px;height:58px;display:flex;align-items:center;justify-content:space-between;gap:16px}
.brand{font:500 20px var(--serif);color:var(--ink);text-decoration:none;letter-spacing:-.01em}.brand b{color:var(--accent);font-weight:500}
.brand small{font:600 10px var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--faint);margin-left:10px;vertical-align:middle}
.site-nav ul{list-style:none;display:flex;gap:18px;margin:0;padding:0;font-size:13.5px}.site-nav ul a{color:var(--muted);text-decoration:none;padding:6px 0;border-bottom:2px solid transparent}.site-nav ul a:hover{color:var(--ink)}.site-nav ul a.on{color:var(--ink);border-bottom-color:var(--accent)}
.site-nav ul li.cta{margin-left:6px}.site-nav ul a.navbtn{background:var(--accent);color:#fff;border-radius:8px;padding:7px 13px;font-weight:600;border-bottom:0}.site-nav ul a.navbtn:hover{filter:brightness(1.08);color:#fff}.site-nav ul a.navbtn.on{outline:2px solid var(--accent);outline-offset:2px}
.themebtn{background:transparent;border:1px solid var(--line);color:var(--muted);width:34px;height:30px;border-radius:6px;cursor:pointer;display:inline-flex;align-items:center;justify-content:center}.themebtn svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.ic-sun{display:none}:root[data-theme="dark"] .ic-moon{display:none}:root[data-theme="dark"] .ic-sun{display:inline}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .ic-moon{display:none}:root:not([data-theme="light"]) .ic-sun{display:inline}}
.navtoggle{display:none;background:transparent;border:1px solid var(--line);color:var(--muted);width:34px;height:30px;border-radius:6px;cursor:pointer;align-items:center;justify-content:center}.navtoggle svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round}
@media (max-width:860px){.navtoggle{display:inline-flex}.site-nav .in{gap:10px}
 .site-nav ul{display:none;position:absolute;left:0;right:0;top:58px;flex-direction:column;gap:0;background:var(--ground);border-bottom:1px solid var(--line);padding:4px 20px 16px;box-shadow:0 12px 24px rgba(0,0,0,.10)}
 .site-nav.open ul{display:flex}
 .site-nav ul a{display:block;padding:12px 0;border-bottom:1px solid var(--line);font-size:15px}
 .site-nav ul li:last-child a{border-bottom:0}.site-nav ul li.cta{margin:12px 0 0}
 .site-nav ul a.navbtn{display:block;text-align:center;border-bottom:0;padding:11px 13px}}
@media (max-width:560px){.brand small{display:none}}
.site-foot{border-top:1px solid var(--line);margin-top:56px;padding:28px 20px 40px;font-size:12.5px;color:var(--faint)}.site-foot .in{max-width:1240px;margin:0 auto;display:flex;gap:20px;flex-wrap:wrap;justify-content:space-between}
.site-foot a{color:var(--muted)}
.page{max-width:900px;margin:0 auto;padding-block:44px 20px;padding-inline:20px}.page.wide{max-width:1240px}
h1{font:400 clamp(34px,5vw,54px)/1.08 var(--serif);letter-spacing:-.01em;margin:0 0 14px;text-wrap:balance}
h2{font:400 clamp(24px,3vw,32px)/1.2 var(--serif);margin:48px 0 8px;text-wrap:balance}h3{font:500 19px/1.3 var(--serif);margin:0 0 6px}
.eyebrow{font:600 12px var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin-bottom:14px}.eyebrow+h1{margin-top:0}
p{max-width:68ch;color:var(--muted);margin:10px 0}p strong,li strong{color:var(--ink);font-weight:600}.lede{font-size:19px;line-height:1.55}
.cards{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(min(260px,100%),1fr));margin-top:22px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:20px;text-decoration:none;color:inherit;display:block}.card:hover{border-color:var(--accent)}.card p{margin:6px 0 0;font-size:14px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:26px 0}.stat{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:14px 16px}.stat b{display:block;font:500 30px/1.1 var(--serif)}.stat span{font-size:12.5px;color:var(--muted)}
.tbl{overflow-x:auto;background:var(--paper);border:1px solid var(--line);border-radius:8px}table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{padding:9px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}
.pill{display:inline-block;padding:2px 8px;border-radius:999px;font:500 11px var(--mono);border:1px solid var(--line);color:var(--muted);margin:2px 4px 2px 0}.pill.prod{border-color:var(--accent);color:var(--accent)}.pill.prop{border-color:var(--warm);color:var(--warm)}
.ref{display:inline-block;font:500 10.5px var(--mono);color:var(--accent);border:1px solid var(--line);border-radius:4px;padding:1px 5px;margin:2px 3px 0 0;text-decoration:none}.ref.int{color:#C0504D;border-style:dashed}
.note{border-left:3px solid var(--warm);background:var(--warm-soft);padding:12px 14px;border-radius:6px;font-size:14px;color:var(--muted);margin:18px 0}
.btn{display:inline-block;padding:11px 16px;border-radius:8px;font-weight:600;border:1px solid var(--line);color:var(--ink);background:var(--paper);text-decoration:none;font-size:14px}.btn.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}select,input[type=search]{background:var(--paper);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:8px 10px;font:14px var(--sans)}
"""
FONTS='<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">'
THEME_JS="<script>(function(){try{var t=localStorage.getItem('f2p-theme');if(t)document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>"
NAV_JS="""<script>(function(){var n=document.getElementById('sitenav'),b=document.getElementById('navtoggle');function set(o){n.classList.toggle('open',o);b.setAttribute('aria-expanded',o?'true':'false')}
b.addEventListener('click',function(){set(!n.classList.contains('open'))});
n.querySelectorAll('#navmenu a').forEach(function(a){a.addEventListener('click',function(){set(false)})});
document.addEventListener('keydown',function(e){if(e.key==='Escape')set(false)});})();</script>"""
TOGGLE="""<button class="themebtn" id="themebtn" aria-label="Toggle theme"><svg class="ic-moon" viewBox="0 0 24 24"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg><svg class="ic-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>
<script>document.getElementById('themebtn').addEventListener('click',function(){var h=document.documentElement,cur=h.getAttribute('data-theme');var dark=cur?cur==='dark':matchMedia('(prefers-color-scheme: dark)').matches;var n=dark?'light':'dark';h.setAttribute('data-theme',n);try{localStorage.setItem('f2p-theme',n)}catch(e){}});</script>"""
LICENSE_URL='https://creativecommons.org/licenses/by/4.0/'
def jsonld(path,title,desc,img):
    org={"@type":"Organization","@id":SITE+"/#publisher","name":"Draper Goren Blockchain","url":"https://dgb.vc","sameAs":["https://www.alongoren.com"]}
    site={"@type":"WebSite","@id":SITE+"/#website","url":SITE+"/","name":"finp2p.info",
        "description":"An independent, sourced map of Ownera's FinP2P network.","inLanguage":"en","publisher":{"@id":SITE+"/#publisher"}}
    page={"@type":"WebPage","@id":SITE+path+"#page","url":SITE+path,"name":title,"description":desc,
        "isPartOf":{"@id":SITE+"/#website"},"primaryImageOfPage":{"@type":"ImageObject","url":img,"width":1200,"height":630},
        "datePublished":"2026-09-20","dateModified":TODAY,"publisher":{"@id":SITE+"/#publisher"},
        "license":LICENSE_URL,"isAccessibleForFree":True}
    g=[org,site,page]
    if path!='/':
        label=dict(NAV+[('/build/','Build with us')]).get(path,title)
        g.append({"@type":"BreadcrumbList","itemListElement":[
            {"@type":"ListItem","position":1,"name":"Home","item":SITE+"/"},
            {"@type":"ListItem","position":2,"name":label,"item":SITE+path}]})
    if path in ('/','/sources/'):
        g.append({"@type":"Dataset","@id":SITE+"/#dataset","name":"finp2p.info FinP2P network graph",
            "description":f"Machine-readable graph of Ownera's FinP2P network: {len(APPS)} SuperApps, derived app-to-app connections with their reasons, {len(insts)} publicly sourced institutions and the source documents behind them.",
            "url":SITE+"/sources/","license":LICENSE_URL,"creator":{"@id":SITE+"/#publisher"},
            "isAccessibleForFree":True,"keywords":["FinP2P","Ownera","tokenization","real-world assets","RWA","SuperApps"],
            "temporalCoverage":DATA_DATE,"dateModified":DATA_DATE,
            "distribution":[{"@type":"DataDownload","encodingFormat":"application/json","contentUrl":SITE+"/data/graph.json"}]})
    return '<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@graph":g})+'</script>'
def chrome(path,title,desc,body,extra_head='',wide=False,og_type='website'):
    img=f"{SITE}/og/{path.strip('/').replace('/','-') or 'home'}.png"
    nav=''.join(f'<li><a href="{p}"{" class=\"on\"" if p==path else ""}>{n}</a></li>' for p,n in NAV)+f'<li class="cta"><a href="/build/" class="navbtn{" on" if path=="/build/" else ""}">Build with us</a></li>'
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{SITE}{path}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1"><meta name="author" content="Draper Goren Blockchain">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="finp2p.info"><meta property="og:locale" content="en_US"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{html.escape(title)} - finp2p.info">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{html.escape(title)}"><meta name="twitter:description" content="{html.escape(desc)}"><meta name="twitter:image" content="{img}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/json" href="{SITE}/data/graph.json" title="finp2p.info network graph">
<meta name="theme-color" content="#F6F4EE" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#0F1413" media="(prefers-color-scheme: dark)">
{jsonld(path,title,desc,img)}
{FONTS}{THEME_JS}<style>{BASE_CSS}</style>{extra_head}</head>
<body><nav class="site-nav" id="sitenav"><div class="in"><a class="brand" href="/">FinP2P<b>.info</b><small>independent network map</small></a><ul id="navmenu">{nav}</ul><span style="display:flex;gap:8px">{TOGGLE}<button class="navtoggle" id="navtoggle" aria-label="Menu" aria-expanded="false" aria-controls="navmenu"><svg viewBox="0 0 24 24"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button></span></div></nav>{NAV_JS}
{body}
<footer class="site-foot"><div class="in" style="display:block;max-width:900px">
<p style="color:var(--ink);font-weight:600;margin:0 0 8px">Independence and disclosure</p>
<p style="margin:0 0 8px;max-width:none">finp2p.info is an independent publication. It is not operated, sponsored, reviewed or endorsed by Ownera or by XCap Ecosystem Ltd, and Ownera has no editorial input. Nothing here is an official statement about the FinP2P network; every claim is sourced to a public document and the derived connections are our own reading of published listings.</p>
<p style="margin:0 0 8px;max-width:none">The site is maintained by <a href="https://www.alongoren.com">Alon Goren</a> and the <a href="https://dgb.vc">Draper Goren Blockchain</a> venture studio. Our founding partner, Alon Goren, is on the board of Ownera. Draper Goren Holm, a fund he manages, is an investor in Ownera. He also serves on the board of LunarCrush, the data provider behind the proposed Social and Market Data SuperApp described on this site. Readers should weigh the content with those interests in mind.</p>
<p style="margin:0 0 8px;max-width:none">Nothing on this site is investment advice or an offer or solicitation of any security or financial instrument. Ownera, FinP2P and SuperApps are trademarks of XCap Ecosystem Ltd; all other names belong to their owners and are used for identification only. Data snapshot {DATA_DATE}; page built {TODAY}. Corrections: <a href="mailto:alon@dgb.vc">alon@dgb.vc</a>.</p>
<p style="margin:12px 0 0;max-width:none"><a href="/about/">About</a> · <a href="/sources/">Sources</a> · <a href="https://www.alongoren.com/superapp/">Social and Market Data SuperApp</a></p>
</div></footer>
</body></html>"""
def hoist(body_file):
    """artifact-style body: <title>, <link>, <style> at top; move title/style/link into head, keep rest as body"""
    s=open(body_file).read()
    title=re.search(r'<title>(.*?)</title>',s,flags=re.S).group(1); s=re.sub(r'<title>.*?</title>','',s,count=1,flags=re.S)
    links=''.join(re.findall(r'<link[^>]+>',s)); s=re.sub(r'<link[^>]+>','',s)
    style=re.search(r'<style>.*?</style>',s,flags=re.S).group(0); s=s.replace(style,'',1)
    return title,links+style,s
def write(path,content):
    out=DIST/path.strip('/')/'index.html' if path!='/' else DIST/'index.html'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(content); print('wrote',out.relative_to(DIST))
# ---------- data prep
nodes=[n for n in G['nodes'] if n['role']!='license']; apps_by=dict((a['slug'],a) for a in APPS)
SOURCES=G['sources']
PUBLIC=json.loads(json.dumps(G))   # public-safe snapshot: the only version that is ever written to dist/
PRIV=json.load(open(DATA/'private.json')) if (DATA/'private.json').exists() else None
if PRIV:   # local-only records with no public source: merged for our own reading, never published
    G['institutions']+=PRIV['institutions']; G['instEdges']+=PRIV['instEdges']; G['sources'].update(PRIV['sources'])
HIDDEN={i['name'] for i in G['institutions'] if not i.get('public')}   # unconfirmed (private materials only): hidden from pages
insts=[i for i in G['institutions'] if i['name'] not in HIDDEN]; iedges=[e for e in G['instEdges'] if e['inst'] not in HIDDEN]
assert not [i for i in PUBLIC['institutions'] if not i.get('public')], 'unsourced records in data/graph.json: move them to data/private.json'
prod=sum(1 for a in APPS if a['status']=='production'); sand=sum(1 for a in APPS if a['status']=='sandbox'); dev=sum(1 for a in APPS if a['status']=='development')
public=sum(1 for i in insts if i.get('public')); companies=len(set(a.get('companyName') for a in APPS if a.get('companyName')))
def refs(rs):
    out=[]
    for r in rs or []:
        sd=SOURCES.get(r); 
        if not sd: continue
        lab='SuperApps store' if r=='store' else 'internal, unconfirmed' if r=='internal' else (sd['pub'].split('/')[0].strip()+' '+sd['date'][:4])
        t=html.escape(sd['title'])
        out.append(f'<a class="ref{" int" if r=="internal" else ""}" href="{sd["url"]}" target="_blank" rel="noopener" title="{t}">{lab}</a>' if sd['url'] else f'<span class="ref int" title="{t}">{lab}</span>')
    return ''.join(out)
# ---------- home
home=f"""<main class="page">
<div class="eyebrow">Ownera's FinP2P network, mapped and sourced</div>
<h1>The network that connects the whole RWA ecosystem.</h1>
<p class="lede">FinP2P is the application layer that lets banks, venues, custodians and issuers move tokenized assets and cash between each other without integrating one by one. This site is an independent map of it: every SuperApp on the store, the institutions attached to each, how a transaction moves, and a public source for every claim.</p>
<div class="stats"><div class="stat"><b>{len(APPS)}</b><span>SuperApps on the store</span></div><div class="stat"><b>{prod}</b><span>in production</span></div><div class="stat"><b>{len(insts)}</b><span>named institutions and partners</span></div><div class="stat"><b>$5B+</b><span>monthly volume, JPM and HQLAx repo</span></div></div>
<div class="cards">
<a class="card" href="/network/"><h3>Every connected piece</h3><p>Ownera's own picture of the network with every real name filled in: counterparties, apps, chains, standards, cash rails, custody, platforms.</p></a>
<a class="card" href="/how-it-works/"><h3>How it works</h3><p>Three diagrams: the shape of the network, one transaction end to end, and where a data utility plugs in.</p></a>
<a class="card" href="/map/"><h3>The map</h3><p>All {len(APPS)} apps, {len(G['edges'])} derived connections and {len(insts)} institutions. Value-chain, network and institution views. Click anything.</p></a>
<a class="card" href="/apps/"><h3>App catalog</h3><p>Every SuperApp with status, company, category, what it orchestrates, and who it serves.</p></a>
<a class="card" href="/institutions/"><h3>Institutions</h3><p>Banks, market infrastructures, asset managers and technology partners, each with citations. Filter by kind, or to SuperApps store listing only.</p></a>
</div>
<h2>Why this exists</h2>
<p>Draper Goren Blockchain published <a href="https://dgb.vc/fifteen-layers">The Real-World Asset Stack: fifteen layers</a>, a map of what it takes for a real asset to go on-chain, from origination to collateral, naming 112 institutions across the layers. Most of those layers only become useful when they can talk to each other. FinP2P is the network where that is happening in production today, and Ownera's own store, developer documentation and industry reports contain enough public data to map it. This site is that map, kept current and honest about what is confirmed and what is not.</p>
<p>It is maintained by Alon Goren, who is on the board of Ownera, and whose fund Draper Goren Holm is an Ownera investor. That is a reason to be careful, so every institution on the site carries a public source, and anything we cannot source publicly is left off. Ownera does not operate, review or endorse this site. Full disclosure in the footer and on the <a href="/about/">about page</a>.</p>
<h2>What is on the network right now</h2>
<p><strong>Live:</strong> intraday repo between J.P. Morgan and HQLAx, in production since 2025, with up to $1 billion traded in a day. <strong>Coming:</strong> Goldman Sachs, Apex, Archax and DTCC on repo and collateral upgrades, per Ownera's Open Collateral Network site; live pilots this month, full production Q4 2026. <strong>Proven in sandbox:</strong> tokenized money market funds as collateral across 48 firms in the US and 30 in the UK and EU, with BlackRock, Citi, Fidelity, Franklin Templeton, State Street, UBS and others in the contributor lists.</p>
<p><a class="btn primary" href="/map/">Open the map</a> <a class="btn" href="/sources/">See the sources</a></p>
<h2>Building for the network?</h2>
<p>If you are building a SuperApp, planning a company for the network, or run an institution on it, <a href="/build/">tell us what you are working on</a>. Draper Goren Blockchain co-founds and backs the companies that make tokenized markets work, and we built one of these SuperApps ourselves.</p>
</main>"""
write('/',chrome('/','FinP2P.info: the FinP2P network, mapped','An independent, sourced map of Ownera\'s FinP2P network: every SuperApp, every named institution, how a transaction moves, and a public source for each claim.',home))
# ---------- how it works
t,head,body=hoist(SRC/'how-it-works.body.html')
body=body.replace('<div class="wrap">','<div class="wrap page">',1)
write('/how-it-works/',chrome('/how-it-works/','How FinP2P works','How Ownera\'s FinP2P network works: Routers inside each institution, peer-to-peer orchestration, one transaction end to end, and where data utilities plug in.',body,extra_head=head))
# ---------- map
t,head,body=hoist(SRC/'map.body.html')
# the map embeds its own dataset: re-emit it from the public-safe snapshot so nothing unsourced can ride along
m=re.search(r'<script id="data" type="application/json">(.*?)</script>',body,flags=re.S)
MG=json.loads(m.group(1).replace('<\\/script','</script'))
for k in ('nodes','edges','overlay','institutions','instEdges','sources'):
    if k in PUBLIC: MG[k]=PUBLIC[k]
body=body[:m.start(1)]+json.dumps(MG).replace('</script','<\\/script')+body[m.end(1):]
body=body.replace('All <strong>35 SuperApps</strong>',f'All <strong>{len(APPS)} SuperApps</strong>')
write('/map/',chrome('/map/','FinP2P SuperApp map','Interactive map of every SuperApp on Ownera\'s store, their derived connections, and the institutions attached to each, with sources.',body,extra_head=head,wide=True))
# ---------- apps
rows=[]
for a in sorted(APPS,key=lambda a:(a['status']!='production',a['status']!='sandbox',a['name'])):
    pc=[c['name'] for c in a['categories'] if c['is_primary'] and c['name']!='Featured SuperApps']; pt=[x['name'] for x in a['types'] if x['is_primary']]
    st=a['status']; pill=f'<span class="pill{" prod" if st=="production" else ""}">{st}</span>'
    orch=(a.get("orchestration") or a.get("shortDescription") or "").strip()
    if len(orch)>260: orch=orch[:260].rsplit(' ',1)[0].rstrip(' ,;:.')+'…'
    rows.append(f'<tr id="{a["slug"]}"><td><b>{html.escape(a["name"])}</b><br><span style="color:var(--muted);font-size:12.5px">{html.escape(a.get("companyName") or "")}</span></td><td>{pill}</td><td>{"".join(f"<span class=pill>{html.escape(c)}</span>" for c in pc)}</td><td>{html.escape(orch)}</td><td class="serves">{html.escape(", ".join(pt))}</td><td><a href="https://superapps.ownera.io/app/{a["slug"]}" target="_blank" rel="noopener">listing&nbsp;↗</a></td></tr>')
APPS_CSS='<style>table.apps{table-layout:fixed}table.apps td.serves{font-size:12.5px;color:var(--muted)}@media (max-width:900px){table.apps{table-layout:auto;min-width:880px}}</style>'
apps_page=f"""<main class="page wide"><div class="eyebrow">Catalog</div><h1>Every SuperApp on the store</h1><p class="lede">{len(APPS)} apps from {companies} companies: {prod} in production, {sand} in sandbox, {dev} in development. Pulled from the store's public API on {DATA_DATE}. Our proposed <a href="https://www.alongoren.com/superapp/">Social and Market Data SuperApp</a> is not yet listed and is not counted here.</p>
<div class="tbl"><table class="apps"><colgroup><col style="width:16%"><col style="width:8%"><col style="width:17%"><col style="width:32%"><col style="width:20%"><col style="width:7%"></colgroup><thead><tr><th>App</th><th>Status</th><th>Category</th><th>What it orchestrates</th><th>Serves</th><th></th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>{APPS_CSS}</main>"""
write('/apps/',chrome('/apps/','FinP2P SuperApp catalog',f'All {len(APPS)} SuperApps on Ownera\'s store with status, company, category, orchestration and participant types.',apps_page,wide=True))
# ---------- institutions
KIND={'bank':'Bank','asset manager':'Asset manager','market infrastructure':'Market infrastructure','custody tech':'Custody tech','stablecoin / payments':'Stablecoin / payments','data':'Data','technology':'Technology','fund services':'Fund services','real estate':'Real estate'}
byname={i['name']:i for i in insts}; name_by_slug={n['id']:n['name'] for n in G['nodes']}
irows=[]
for i in sorted(insts,key=lambda i:(i['kind'],i['name'])):
    ls=[e for e in iedges if e['inst']==i['name']]
    cls='internal' if not i.get('public') else ('store' if i['refs']==['store'] else 'public')
    irows.append(f'<tr data-kind="{html.escape(i["kind"])}" data-src="{cls}"><td><b>{html.escape(i["name"])}</b>{"" if i.get("public") else " <span class=\"pill\" style=\"border-color:#C0504D;color:#C0504D\">unconfirmed</span>"}</td><td>{KIND.get(i["kind"],i["kind"])}</td><td style="font-size:12.5px">{html.escape(", ".join(name_by_slug.get(e["app"],e["app"]) for e in ls))}</td><td>{refs(i["refs"])}</td></tr>')
inst_page=f"""<main class="page wide"><div class="eyebrow">Directory</div><h1>Banks, institutions and partners on FinP2P</h1><p class="lede">{len(insts)} organisations attached to at least one SuperApp, every one with a public source. Most trace to a few documents: the two GDF and ISDA collateral sandbox reports, the J.P. Morgan and HQLAx repo launch, DTCC's own account of its collateral experiment, CoinDesk on the Goldman real estate fund, Ownera's announcements and its Open Collateral Network site, and vendor partner pages.</p>
<div class="note">A name on this list means the organisation is publicly connected to an app or to the network in the cited document. It does not mean it transacts on FinP2P in production. Some SuperApps store "partners" are the app vendor's own clients. Read the citation.</div>
<div class="toolbar"><select id="fk"><option value="">All kinds</option>{''.join(f'<option value="{k}">{v}</option>' for k,v in KIND.items())}</select><select id="fs"><option value="">Any source</option><option value="public">Public source</option><option value="store">SuperApps store listing only</option></select><input type="search" id="fq" placeholder="Find an institution"></div>
<div class="tbl"><table id="it"><thead><tr><th>Institution</th><th>Kind</th><th>Attached to</th><th>Sources</th></tr></thead><tbody>{''.join(irows)}</tbody></table></div>
<script>(function(){{var k=document.getElementById('fk'),s=document.getElementById('fs'),q=document.getElementById('fq');function f(){{var t=q.value.toLowerCase();document.querySelectorAll('#it tbody tr').forEach(function(r){{r.style.display=((!k.value||r.dataset.kind===k.value)&&(!s.value||r.dataset.src===s.value)&&(!t||r.textContent.toLowerCase().indexOf(t)>=0))?'':'none'}})}}[k,s].forEach(function(e){{e.addEventListener('change',f)}});q.addEventListener('input',f)}})();</script></main>"""
write('/institutions/',chrome('/institutions/','Institutions on FinP2P','Every bank, market infrastructure, asset manager and technology partner publicly attached to a FinP2P SuperApp, with sources.',inst_page,wide=True))
# ---------- sources
cnt={}
for i in insts:
    for r in i['refs']: cnt.setdefault(r,[]).append(i['name'])
srows=''.join(f'<tr><td>{f"<a href=\"{s["url"]}\" target=\"_blank\" rel=\"noopener\">{html.escape(s["title"])}</a>" if s["url"] else html.escape(s["title"])}</td><td style="white-space:nowrap;color:var(--muted);font-size:12.5px">{html.escape(s["pub"])}<br>{s["date"]}</td><td style="font-size:12.5px">{len(cnt[r])}: {html.escape(", ".join(cnt[r]))}</td></tr>' for r,s in sorted(SOURCES.items(),key=lambda kv:-len(cnt.get(kv[0],[]))) if cnt.get(r))
src_page=f"""<main class="page wide"><div class="eyebrow">Evidence</div><h1>Sources</h1><p class="lede">Every document cited on this site, once, with the institutions that rely on it. Dates are the document's own. Ownera's <a href="https://www.ownera.io/news">news page</a> indexes its partnership announcements; the <a href="https://ocn.ownera.io/">Open Collateral Network</a> site hosts the full industry reports.</p>
<div class="tbl"><table><thead><tr><th>Source</th><th>Publisher · date</th><th>Cited by</th></tr></thead><tbody>{srows}</tbody></table></div>
<h2>Use the data</h2><p>The whole model behind this site is one file: <a href="/data/graph.json">graph.json</a> (apps, derived connections with their reasons, institutions with references, and every source). It is published under <a href="https://creativecommons.org/licenses/by/4.0/" rel="license">CC BY 4.0</a>, so you may reuse it anywhere with attribution to finp2p.info. Records we cannot tie to a public document are not in it.</p>
<h2>How the app-to-app connections were derived</h2><p>Ownera does not publish app-to-app links. The map derives them from each app's category, participant types and stated orchestration using ten explicit rules, listed at the bottom of the <a href="/map/">map page</a>. They are our reading of the listings, not an Ownera statement.</p></main>"""
write('/sources/',chrome('/sources/','Sources','Every public document behind finp2p.info, with the institutions that cite it.',src_page,wide=True))
# ---------- about
about=f"""<main class="page"><div class="eyebrow">About</div><h1>An independent reference for the FinP2P network.</h1>
<p class="lede">finp2p.info is maintained by Alon Goren, founding partner of the venture studio at <a href="https://dgb.vc">Draper Goren Blockchain</a>. He is on the board of Ownera, and of LunarCrush; Draper Goren Holm, a fund he manages, is an investor in Ownera. That is why the site exists, and it is why every claim on it cites a public source.</p>
<div class="note"><strong>This site is not an Ownera property.</strong> It is not operated, sponsored, reviewed or endorsed by Ownera or XCap Ecosystem Ltd, and Ownera has no editorial input. Where the site describes Ownera's plans it quotes or links Ownera's own public material. Where it draws connections between apps, those are our inferences from public listings and are labelled as such.</div>
<h2>What the site is</h2><p>A map of the FinP2P network built from public data: Ownera's SuperApps store and its JSON API, Ownera's developer documentation, the GDF and ISDA industry reports, Ownera's press announcements and Open Collateral Network site, and the app vendors' own pages. Where we add our own reading, such as the derived app-to-app connections, the page says so and shows the rules.</p>
<h2>What it is not</h2><p>Not an Ownera property, not reviewed or endorsed by Ownera, and not a statement that any named institution transacts on FinP2P in production unless the cited source says so. Institutions we cannot tie to a public source are not listed.</p>
<h2>Work with DGB</h2><p>Building a SuperApp or a company for the network? See <a href="/build/">Build with us</a>.</p>
<h2>Corrections</h2><p>If you represent an institution or app on this site and something is wrong or out of date, email <a href="mailto:alon@dgb.vc">alon@dgb.vc</a> with the correction and a public source. Corrections ship the same week.</p>
<h2>Related</h2><p><a href="https://dgb.vc/fifteen-layers">The Real-World Asset Stack: fifteen layers</a> is DGB's map of the whole tokenization lifecycle; this site is the network view of one layer of it. The <a href="https://www.alongoren.com/superapp/">Social and Market Data SuperApp</a> is DGB's own proposed data utility for the network.</p>
<p style="margin-top:28px;font-size:12.5px;color:var(--faint)">Data snapshot {DATA_DATE}. Ownera, FinP2P and SuperApps are trademarks of XCap Ecosystem Ltd.</p></main>"""
write('/about/',chrome('/about/','About finp2p.info','Who maintains finp2p.info, what it is and is not, and how to send a correction.',about))
# ---------- network (every connected piece, by layer)
L=json.load(open(DATA/'layers.json')); BLURB=json.load(open(DATA/'blurbs.json'))
byrole={}
for n in nodes: byrole.setdefault(n['role'],[]).append(n)
kinds=['bank','asset manager','market infrastructure','custody tech','stablecoin / payments','fund services','real estate','data','technology']
KINDN={'bank':'Banks','asset manager':'Asset managers','market infrastructure':'Market infrastructures and venues','custody tech':'Custody tech','stablecoin / payments':'Stablecoin and payments','fund services':'Fund services','real estate':'Real estate','data':'Data','technology':'Technology'}
def chip(name,url='',title='',key=''):
    t=f' title="{html.escape(title)}"' if title else ''
    if key: return f'<button class="chip" data-key="{html.escape(key)}"{t}>{html.escape(name)}</button>'
    return f'<a class="chip" href="{url}" target="_blank" rel="noopener"{t}>{html.escape(name)}</a>' if url else f'<span class="chip"{t}>{html.escape(name)}</span>'
# detail records for the popup
DETAIL={}
for i in insts:
    ls=[e for e in iedges if e['inst']==i['name']]
    primary=i['refs'][0] if i['refs'] else ''
    DETAIL['inst:'+i['name']]={'name':i['name'],'kind':KIND.get(i['kind'],i['kind']),'blurb':BLURB.get(i['name'],''),
      'items':[{'title':name_by_slug.get(e['app'],e['app']),'note':e['note'],'href':f'/apps/#{e["app"]}'} for e in ls],
      'sources':[{'label':SOURCES[r]['pub'].split('/')[0].strip()+' · '+SOURCES[r]['date'],'title':SOURCES[r]['title'],'url':SOURCES[r]['url']} for r in i['refs'] if r in SOURCES and SOURCES[r]['url']]}
for n in nodes:
    a=apps_by.get(n['id'],{})
    il=[e for e in iedges if e['app']==n['id']]
    DETAIL['app:'+n['id']]={'name':n['name'],'kind':(n['company']+' · '+n['status']),'blurb':(n['short']+((' Orchestrates: '+n['orch']) if n['orch'] else '')),
      'items':[{'title':e['inst'],'note':e['note'],'href':''} for e in il],
      'sources':[{'label':'SuperApps store listing','title':n['name']+' on superapps.ownera.io','url':n['url']}]}
for l in L['layers']:
    for it in l['items']:
        DETAIL['layer:'+l['id']+':'+it['name']]={'name':it['name'],'kind':l['title'],'blurb':it.get('note',''),'items':[],'sources':[{'label':'Source','title':it['src'],'url':it['src']}]}
inst_cols=''.join(f'<div class="col"><h4>{KINDN[k]} <small>{sum(1 for i in insts if i["kind"]==k)}</small></h4>{"".join(chip(i["name"],key="inst:"+i["name"]) for i in sorted(insts,key=lambda i:i["name"]) if i["kind"]==k)}</div>' for k in kinds if any(i['kind']==k for i in insts))
app_groups=[('Business SuperApps',['issuer','distribution','trading','finance']),('Utilities and connectors',['ledger','custody','payments','messaging','data','identity'])]
app_cols=''.join(f'<div class="col"><h4>{t} <small>{sum(len(byrole.get(r,[])) for r in rs)}</small></h4>{"".join(chip(n["name"]+(" · live" if n["status"]=="production" else ""),key="app:"+n["id"]) for r in rs for n in sorted(byrole.get(r,[]),key=lambda n:n["name"]))}</div>' for t,rs in app_groups)
layer_blocks=''.join(f'<section class="layer"><h3>{html.escape(l["title"])}</h3><p>{html.escape(l["blurb"])}</p><div class="chips">{"".join(chip(it["name"],key="layer:"+l["id"]+":"+it["name"]) for it in l["items"])}</div></section>' for l in L['layers'])
NET_CSS='<style>button.chip{font-family:var(--sans);cursor:pointer}button.chip:hover{border-color:var(--accent)}.modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;z-index:80}.modal-bg.on{display:block}.modal{position:fixed;right:0;top:0;bottom:0;width:min(460px,100%);background:var(--paper);border-left:1px solid var(--line);padding:26px 24px 32px;overflow:auto;z-index:81;transform:translateX(100%);transition:transform .2s}.modal.on{transform:none}.modal h3{font:500 24px/1.2 var(--serif);margin:0 0 4px}.modal .kind{color:var(--muted);font-size:13px;margin-bottom:12px}.modal p{font-size:14.5px;margin:8px 0}.modal ul{padding-left:16px;margin:6px 0;font-size:13.5px;color:var(--muted)}.modal li{margin:4px 0}.modal li b{color:var(--ink);font-weight:600}.modal .src{margin-top:22px;padding-top:12px;border-top:1px solid var(--line);font-size:13px}.modal .src a{display:block;margin:4px 0;color:var(--accent)}.modal .close{position:absolute;top:14px;right:14px;background:transparent;border:1px solid var(--line);color:var(--muted);border-radius:6px;width:30px;height:30px;cursor:pointer}@media (prefers-reduced-motion:reduce){.modal{transition:none}}.col{background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:14px}.col h4{margin:0 0 8px;font:600 12px var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}.col h4 small{color:var(--accent);margin-left:6px}.cols{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));margin:14px 0}.chips{display:flex;flex-wrap:wrap;gap:6px}.chip{display:inline-block;font-size:12.5px;padding:4px 9px;border:1px solid var(--line);border-radius:999px;color:var(--ink);text-decoration:none;background:var(--ground)}a.chip:hover{border-color:var(--accent)}.layer{margin-top:26px}.layer p{margin:4px 0 10px;font-size:14px}.tier{margin-top:34px;padding-top:16px;border-top:1px solid var(--line)}.tier .eyebrow{margin-bottom:6px}.orch{margin:18px 0;padding:14px 18px;border:2px solid var(--accent);border-radius:10px;background:var(--accent-soft);text-align:center;font:500 18px var(--serif)}.orch small{display:block;font:13px var(--sans);color:var(--muted);margin-top:4px}</style>'
net=f"""<main class="page wide"><div class="eyebrow">Every connected piece</div><h1>The FinP2P puzzle, with the real names filled in.</h1>
<p class="lede">Ownera draws its network as counterparties running Routers, an orchestration layer in the middle, and three things underneath: many blockchains, each institution's internal platforms, and a store of SuperApps. This page is that picture with every publicly named piece in place. Hover a chip for the note, click it for the source.</p>
<div class="tier"><div class="eyebrow">Counterparties: who runs or is attached to a Router</div><p>{len(insts)} organisations publicly attached to the network or to an app on it. </p><div class="cols">{inst_cols}</div></div>
<div class="orch">FinP2P application orchestration<small>one Router per institution · intents become orchestration plans · executed peer to peer with signed proofs</small></div>
<div class="tier"><div class="eyebrow">SuperApp store: what runs on the Routers</div><p>{len(nodes)} apps. "live" marks production status on the store.</p><div class="cols">{app_cols}</div></div>
<div class="tier"><div class="eyebrow">Underneath: chains, standards, cash, custody, platforms, industry</div>{layer_blocks}</div>
<p style="margin-top:28px"><a class="btn primary" href="/map/">See the connections drawn</a> <a class="btn" href="/sources/">Sources</a></p></main>
<div class="modal-bg" id="mbg"></div><aside class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="mtitle"><button class="close" id="mclose" aria-label="Close">×</button><h3 id="mtitle"></h3><div class="kind" id="mkind"></div><div id="mbody"></div><div class="src" id="msrc"></div></aside>
<script id="detail" type="application/json">{json.dumps(DETAIL).replace('</script','<\\/script')}</script>
<script>(function(){{var D=JSON.parse(document.getElementById('detail').textContent),m=document.getElementById('modal'),bg=document.getElementById('mbg');function esc(s){{return String(s).replace(/[&<>"]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]}})}}
function open(key){{var d=D[key];if(!d)return;document.getElementById('mtitle').textContent=d.name;document.getElementById('mkind').textContent=d.kind;var b='';if(d.blurb)b+='<p>'+esc(d.blurb)+'</p>';if(d.items.length){{b+='<p style="margin-top:14px"><b>'+(key.indexOf('app:')===0?'Institutions and partners on this app':'Participates in')+'</b></p><ul>'+d.items.map(function(it){{return '<li><b>'+(it.href?'<a href="'+it.href+'" style="color:inherit">'+esc(it.title)+'</a>':esc(it.title))+'</b><br>'+esc(it.note)+'</li>'}}).join('')+'</ul>'}}document.getElementById('mbody').innerHTML=b;document.getElementById('msrc').innerHTML=d.sources.length?('<b style="color:var(--ink)">Source</b>'+d.sources.map(function(s){{return '<a href="'+s.url+'" target="_blank" rel="noopener" title="'+esc(s.title)+'">'+esc(s.label)+' ↗</a>'}}).join('')):'';m.classList.add('on');bg.classList.add('on');try{{history.replaceState(null,'','#'+encodeURIComponent(key))}}catch(e){{}}document.getElementById('mclose').focus()}}
function close(){{m.classList.remove('on');bg.classList.remove('on');try{{history.replaceState(null,'',location.pathname)}}catch(e){{}}}}
document.querySelectorAll('button.chip[data-key]').forEach(function(b){{b.addEventListener('click',function(){{open(b.dataset.key)}})}});bg.addEventListener('click',close);document.getElementById('mclose').addEventListener('click',close);document.addEventListener('keydown',function(e){{if(e.key==='Escape')close()}});
if(location.hash.length>1){{open(decodeURIComponent(location.hash.slice(1)))}}}})();</script>"""
write('/network/',chrome('/network/','The FinP2P network, every connected piece','Every publicly named piece of the FinP2P network by layer: counterparties, SuperApps, blockchains, token standards, cash rails, custody, internal platforms and industry bodies, each with a source.',net,extra_head=NET_CSS,wide=True))
# ---------- build with us (DGB + contact)
CF_STYLE='<style>#cf input,#cf select,#cf textarea{background:var(--ground);color:var(--ink);border:1px solid var(--line);border-radius:6px;padding:9px 10px;font:14px var(--sans)}#cf input:focus,#cf select:focus,#cf textarea:focus{outline:none;border-color:var(--accent)}</style>'
build_page=f"""<main class="page"><div class="eyebrow">Build with us</div><h1>Building a SuperApp, or building for the network? Talk to us.</h1>
<p class="lede">This site is maintained by the <a href="https://dgb.vc">Draper Goren Blockchain</a> venture studio. We built the <a href="https://www.alongoren.com/superapp/">Social and Market Data SuperApp</a> for the network ourselves, our founding partner Alon Goren is on the board of Ownera, and we back and build the companies that make tokenized markets work. If you are working on anything that touches FinP2P, we want to hear from you.</p>
<div class="cards">
<div class="card"><h3>You are building a SuperApp</h3><p>Listed or not yet. We can share what we learned shipping a data utility end to end: the adapter contract, the schema process, the ingest test, the Docker template. And we will put you on the map.</p></div>
<div class="card"><h3>You are a founder planning to build for the network</h3><p>Issuer tools, data, identity, custody, connectors, a vertical business app. DGB is a venture studio: when the company does not exist yet, we co-found it; when it does, we want to be the earliest check.</p></div>
<div class="card"><h3>You are an institution or vendor on the network</h3><p>Tell us what you run on it and we will make sure your entry here is right. Corrections ship the same week, with a source.</p></div>
</div>
<h2>About Draper Goren Blockchain</h2>
<p>A hybrid venture studio and venture fund building and backing the infrastructure for tokenized real-world assets: real estate and credit, music catalogs and athletes' earnings, and the AI rebuilding how all of it runs. When the company already exists we want to be the earliest check in it; when it does not exist yet, we build it. Founded by Alon Goren with Tim Draper and run with David Bleznak. Alon is on the board of Ownera; a predecessor fund he manages, Draper Goren Holm, is an Ownera investor.</p>
<p>DGB published <a href="https://dgb.vc/fifteen-layers">The Real-World Asset Stack: fifteen layers</a>, the map of what it takes for a real asset to go on-chain. finp2p.info is the network view of that stack. More at <a href="https://dgb.vc">dgb.vc</a>.</p>
<h2 id="contact">Get in touch</h2>
<form id="cf" class="card" style="max-width:640px" novalidate>
 <div style="display:grid;gap:12px;grid-template-columns:1fr 1fr">
  <label style="font-size:13px;color:var(--muted)">Name<br><input id="c-name" name="name" type="text" required style="width:100%;margin-top:4px"></label>
  <label style="font-size:13px;color:var(--muted)">Email<br><input id="c-email" name="email" type="email" required style="width:100%;margin-top:4px"></label>
 </div>
 <label style="font-size:13px;color:var(--muted);display:block;margin-top:12px">Company or project<br><input id="c-org" name="organization" type="text" style="width:100%;margin-top:4px"></label>
 <label style="font-size:13px;color:var(--muted);display:block;margin-top:12px">I am<br><select id="c-int" name="interest" style="width:100%;margin-top:4px"><option>building a SuperApp</option><option>a founder planning to build for the network</option><option>an institution or vendor on the network</option><option>press or research</option><option>something else</option></select></label>
 <label style="font-size:13px;color:var(--muted);display:block;margin-top:12px">What are you working on?<br><textarea id="c-msg" name="message" rows="5" style="width:100%;margin-top:4px"></textarea></label>
 <input type="text" name="website" id="c-web" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px" aria-hidden="true">
 <div style="display:flex;gap:12px;align-items:center;margin-top:14px;flex-wrap:wrap"><button class="btn primary" type="submit" id="c-send">Send</button><span id="c-toast" style="font-size:13px;color:var(--muted)"></span></div>
 <p style="font-size:12px;color:var(--faint);margin-top:12px">Goes to alon@dgb.vc. We read everything. No newsletter, no list.</p>
</form>
{CF_STYLE}
<script>(function(){{var f=document.getElementById('cf'),t=document.getElementById('c-toast'),b=document.getElementById('c-send');var RE=/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/;
f.addEventListener('submit',function(e){{e.preventDefault();var v=function(id){{return document.getElementById(id).value.trim()}};var p={{name:v('c-name'),email:v('c-email'),organization:v('c-org'),interest:v('c-int'),message:v('c-msg'),website:v('c-web')}};
if(!p.name||!RE.test(p.email)){{t.textContent='Name and a valid email are required.';return}}b.disabled=true;t.textContent='Sending…';
fetch('/api/contact/',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(p)}}).then(function(r){{if(!r.ok)throw new Error('relay');return r.json()}}).then(function(d){{if(d&&d.ok){{t.textContent='Got it. We will be in touch shortly.';f.reset()}}else throw new Error('relay')}}).catch(function(){{b.disabled=false;var body='Name: '+p.name+'\\nEmail: '+p.email+'\\nCompany: '+p.organization+'\\nI am: '+p.interest+'\\n\\n'+p.message;t.innerHTML='Could not send from here. <a href="mailto:alon@dgb.vc?subject='+encodeURIComponent('finp2p.info: '+p.interest)+'&body='+encodeURIComponent(body)+'">Open in your mail app instead</a>.'}})}})}})();</script>
</main>"""
write('/build/',chrome('/build/','Build on FinP2P with Draper Goren Blockchain','For SuperApp builders, founders planning to build for the FinP2P network, and institutions on it: who DGB is and how to reach us.',build_page))
# ---------- static
shutil.copy(SRC/'og.png',DIST/'og.png')
(DIST/'og').mkdir(exist_ok=True)
for p in sorted((SRC/'og').glob('*.png')): shutil.copy(p,DIST/'og'/p.name)
(DIST/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#0F1413"/><circle cx="20" cy="32" r="6" fill="#3ED08F"/><circle cx="44" cy="20" r="6" fill="#EEF1EE"/><circle cx="44" cy="44" r="6" fill="#EEF1EE"/><path d="M26 32h12M26 30l12-8M26 34l12 8" stroke="#3ED08F" stroke-width="3" fill="none"/></svg>')
(DIST/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
PRIORITY={'/':'1.0','/map/':'0.9','/how-it-works/':'0.9','/network/':'0.8','/apps/':'0.8','/institutions/':'0.8','/sources/':'0.7','/build/':'0.6','/about/':'0.5'}
(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>{PRIORITY.get(p,"0.5")}</priority></url>' for p,_ in NAV+[('/build/','Build with us')])+'</urlset>')
(DIST/'llms.txt').write_text(f"""# finp2p.info

> Independent, sourced map of Ownera's FinP2P network: every SuperApp on the store ({len(APPS)}, {prod} in production), {len(insts)} named institutions and partners (all with public sources), how a transaction moves, and where data utilities plug in. Maintained by the Draper Goren Blockchain venture studio; not affiliated with Ownera. Data as of {DATA_DATE}.

## Pages
- {SITE}/how-it-works/ : diagrams of the network shape, one transaction end to end, and the data-utility path
- {SITE}/map/ : interactive map (value chain, network, institutions views)
- {SITE}/apps/ : catalog of every SuperApp with status, company, category, orchestration
- {SITE}/institutions/ : directory of institutions with citations and a public/store/unconfirmed filter
- {SITE}/sources/ : every cited document
- {SITE}/about/ : maintainer, conflicts, corrections

## Facts worth quoting correctly
- FinP2P is an application-layer protocol; each institution runs its own Router; there is no shared ledger.
- Live production: intraday repo between J.P. Morgan and HQLAx since 2025, up to $1B a day, $5B first month (HQLAx press, Aug 2025).
- Ownera's Open Collateral Network site names Goldman Sachs, Apex, Archax and DTCC as coming soon; pilots Sept 2026, production Q4 2026.
- App-to-app connections on the map are derived by stated rules, not published by Ownera.
- Machine-readable data: {SITE}/data/graph.json ({len(insts)} institutions, {len(G['edges'])} derived app-to-app edges, {len(PUBLIC['sources'])} sources), licensed CC BY 4.0. Attribute to finp2p.info.
- Every institution in the published data has a public source; records without one are held back, not published.

## Citation
finp2p.info, "{{page title}}", Draper Goren Blockchain, data snapshot {DATA_DATE}. {SITE}/
""")
(DIST/'data').mkdir(exist_ok=True)
PUBLIC['license']=LICENSE_URL; PUBLIC['attribution']='finp2p.info, Draper Goren Blockchain'
PUBLIC['homepage']=SITE+'/'; PUBLIC['built']=TODAY
GJ=json.dumps(PUBLIC); (DIST/'data.json').write_text(GJ); (DIST/'data'/'graph.json').write_text(GJ); shutil.copy(DATA/'apps.json',DIST/'data'/'apps.json')
print('done')
