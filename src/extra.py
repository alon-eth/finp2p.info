# What changed (+ RSS) and site search. exec'd by build.py after devpages.py, sharing its globals.
from email.utils import format_datetime
from urllib.parse import quote
CH=json.load(open(DATA/'changes.json'))['entries']

# ---------- /changes/ and RSS
def ch_id(e): return 'c-'+e['date']+'-'+re.sub('[^a-z0-9]+','-',e['title'].lower()).strip('-')[:50]
KINDLAB={'network':'Network','site':'This site'}
crows=''.join(f'''<article class="chg" id="{ch_id(e)}" data-kind="{e['kind']}"><div class="chg-meta"><time datetime="{e['date']}">{e['date']}</time><span class="pill{" prod" if e['kind']=="network" else ""}">{KINDLAB[e['kind']]}</span></div>
<h3>{html.escape(e['title'])}</h3><p>{html.escape(e['body'])}</p><p style="font-size:13.5px">{f'<a href="{e["link"]}">On this site</a>' if e.get('link') else ''}{' · ' if e.get('link') and e.get('url') else ''}{f'<a href="{e["url"]}" target="_blank" rel="noopener">Source ↗</a>' if e.get('url') else ''}</p></article>''' for e in CH)
CH_CSS='<style>.chg{border-top:1px solid var(--line);padding:18px 0 6px}.chg-meta{display:flex;gap:10px;align-items:center;font:500 12.5px var(--mono);color:var(--faint)}.chg h3{margin:8px 0 2px;font-size:21px}.chg p{margin:6px 0}</style>'
changes=f"""<main class="page"><div class="eyebrow">What changed</div><h1>What changed on the FinP2P network.</h1>
<p class="lede">New SuperApp listings, apps moving to production, new partnerships, and changes to this site, newest first. Every network entry links to its public source.</p>
<p><a class="btn" href="/changes/feed.xml">Follow by RSS</a> <span style="font-size:13px;color:var(--faint);margin-left:8px">Paste the feed URL into any reader: {SITE}/changes/feed.xml</span></p>
<div class="toolbar"><select id="ck"><option value="">Everything</option><option value="network">Network changes only</option><option value="site">Site changes only</option></select></div>
<div id="chl">{crows}</div>
<script>(function(){{var k=document.getElementById('ck');k.addEventListener('change',function(){{document.querySelectorAll('#chl .chg').forEach(function(a){{a.style.display=(!k.value||a.dataset.kind===k.value)?'':'none'}})}})}})();</script>
<p style="margin-top:28px;font-size:13.5px">Know of a change we missed? Email <a href="mailto:alon@dgb.vc">alon@dgb.vc</a> with a public source.</p></main>"""
write('/changes/',chrome('/changes/','What changed on FinP2P','New SuperApp listings, production launches, partnerships and site updates for Ownera\'s FinP2P network, newest first, each with a source. RSS available.',changes,extra_head=CH_CSS))
def rfc822(d): return format_datetime(datetime.datetime.fromisoformat(d+'T12:00:00+00:00'))
items=''.join(f'''<item><title>{html.escape(e['title'])}</title><link>{SITE}/changes/#{ch_id(e)}</link><guid isPermaLink="false">{ch_id(e)}</guid><pubDate>{rfc822(e['date'])}</pubDate><category>{KINDLAB[e['kind']]}</category><description>{html.escape(e['body']+(' Source: '+e['url'] if e.get('url') else ''))}</description></item>''' for e in CH)
(DIST/'changes').mkdir(exist_ok=True)
(DIST/'changes'/'feed.xml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>finp2p.info: what changed</title><link>{SITE}/changes/</link><atom:link href="{SITE}/changes/feed.xml" rel="self" type="application/rss+xml"/><description>Changes on Ownera's FinP2P network and on finp2p.info, an independent community resource not affiliated with Ownera.</description><language>en</language><lastBuildDate>{rfc822(CH[0]['date'])}</lastBuildDate>{items}</channel></rss>
''')

# ---------- search index + /search/
IDX=[]
def add(t,k,d,u): IDX.append({'t':t,'k':k,'d':re.sub(r'\s+',' ',d or '').strip()[:240],'u':u})
PAGE_DESC={'/':'Overview of the FinP2P network and this site','/how-it-works/':'Diagrams: network shape, one transaction end to end, data utility path','/network/':'Every connected piece by layer: counterparties, apps, chains, standards, cash, custody','/map/':'Interactive map of apps, derived connections and institutions','/apps/':'Catalog of every SuperApp with status, company and category','/institutions/':'Directory of banks, infrastructures and partners with citations','/sources/':'Every public document behind the site','/developers/':'Community guide to building on FinP2P','/faq/':'Frequently asked questions','/about/':'Who maintains this site, disclosure, corrections','/build/':'Build with Draper Goren Blockchain','/agents/':'Guide for AI agents and LLMs','/changes/':'What changed on the network and the site'}
for p,n in NAV+[('/build/','Build with us'),('/agents/','For AI agents'),('/changes/','What changed')]: add(n,'Page',PAGE_DESC.get(p,''),p)
for path,h in DEV_TEXT.items():
    if path=='/faq/': continue
    for sid,title in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>',h): add(strip_tags(title),'Guide',PAGE_DESC[path],f'{path}#{sid}')
for _,qs in FAQ:
    for q,ans in qs: add(q,'FAQ',strip_tags(ans),f'/faq/#{qid(q)}')
for n in nodes: add(n['name'],'App',f"{n['company']} · {n['status']}. {n['short']}",f"/apps/#{n['id']}")
for i in insts:
    ls=', '.join(name_by_slug.get(e['app'],e['app']) for e in iedges if e['inst']==i['name'])
    add(i['name'],'Institution',f"{KIND.get(i['kind'],i['kind'])}{'. On: '+ls if ls else ''}. {BLURB.get(i['name'],'')}",'/network/#'+quote('inst:'+i['name']))
for l in L['layers']:
    for it in l['items']: add(it['name'],'Network layer',f"{l['title']}. {it.get('note','')}",'/network/#'+quote('layer:'+l['id']+':'+it['name']))
for s_ in PUBLIC['sources'].values():
    if s_['url']: add(s_['title'],'Source',f"{s_['pub']}, {s_['date']}",s_['url'])
for e in CH: add(e['title'],'Change',f"{e['date']}. {e['body']}",f'/changes/#{ch_id(e)}')
(DIST/'search-index.json').write_text(json.dumps(IDX,ensure_ascii=False))
SEARCH_CSS='<style>#sq{width:100%;font-size:18px;padding:13px 14px;border-radius:8px}#sr{list-style:none;padding:0;margin:18px 0}#sr li{border-top:1px solid var(--line);padding:12px 0}#sr a.t{font:500 18px var(--serif);color:var(--ink);text-decoration:none}#sr a.t:hover{color:var(--accent)}#sr p{margin:3px 0 0;font-size:14px}#sr mark{background:var(--accent-soft);color:var(--ink);border-radius:3px;padding:0 1px}.sk{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px}.sk button{font:12.5px var(--sans);border:1px solid var(--line);background:var(--paper);color:var(--muted);border-radius:999px;padding:4px 10px;cursor:pointer}.sk button.on{border-color:var(--accent);color:var(--accent)}</style>'
KINDS=['App','Institution','Network layer','Source','Guide','FAQ','Page','Change']
search=f"""<main class="page"><div class="eyebrow">Search</div><h1>Search finp2p.info</h1>
<form role="search" action="/search/" onsubmit="return false"><label for="sq" style="position:absolute;left:-9999px">Search</label><input type="search" id="sq" name="q" placeholder="Try: repo, stablecoin, custody adapter, Goldman, KYC" autocomplete="off" autofocus></form>
<div class="sk" id="sk"><button type="button" data-k="" class="on">All</button>{''.join(f'<button type="button" data-k="{k}">{k}s</button>' for k in KINDS)}</div>
<p id="sn" style="font-size:13px;color:var(--faint)">{len(IDX)} entries: every app, institution, network component, source, FAQ answer and guide section.</p>
<ul id="sr"></ul>
<script id="sidx" type="application/json">{json.dumps(IDX,ensure_ascii=False).replace('</','<\\/')}</script>
<script>(function(){{var I=JSON.parse(document.getElementById('sidx').textContent),q=document.getElementById('sq'),r=document.getElementById('sr'),n=document.getElementById('sn'),K='';
function esc(s){{return String(s).replace(/[&<>"]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]}})}}
function norm(s){{return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')}}
I.forEach(function(x){{x.nt=norm(x.t);x.nd=norm(x.d+' '+x.k)}});
function hl(s,ws){{s=esc(s);ws.forEach(function(w){{if(w.length>1)s=s.replace(new RegExp('('+w.replace(/[.*+?^${{}}()|[\\]\\\\]/g,'\\\\$&')+')','ig'),'<mark>$1</mark>')}});return s}}
function run(){{var v=q.value.trim(),ws=norm(v).split(/\\s+/).filter(Boolean),out=[];
 try{{history.replaceState(null,'',v?'?q='+encodeURIComponent(v):location.pathname)}}catch(e){{}}
 if(!ws.length&&!K){{r.innerHTML='';n.textContent=I.length+' entries: every app, institution, network component, source, FAQ answer and guide section.';return}}
 I.forEach(function(x){{if(K&&x.k!==K)return;var s=0;for(var i=0;i<ws.length;i++){{var w=ws[i],a=x.nt.indexOf(w),b=x.nd.indexOf(w);if(a<0&&b<0)return;s+=(a===0?12:a>0?7:0)+(b>=0?2:0)}}if(x.nt===ws.join(' '))s+=20;out.push([s,x])}});
 out.sort(function(a,b){{return b[0]-a[0]}});n.textContent=out.length+' result'+(out.length===1?'':'s')+(v?' for “'+v+'”':'');
 r.innerHTML=out.slice(0,60).map(function(o){{var x=o[1],ext=/^https?:/.test(x.u);return '<li><span class="pill">'+esc(x.k)+'</span> <a class="t" href="'+esc(x.u)+'"'+(ext?' target="_blank" rel="noopener"':'')+'>'+hl(x.t,ws)+(ext?' ↗':'')+'</a><p>'+hl(x.d,ws)+'</p></li>'}}).join('')+(out.length?'':'<li><p>Nothing found. Try a shorter word, or browse the <a href="/map/">map</a>.</p></li>')}}
document.getElementById('sk').addEventListener('click',function(e){{var b=e.target.closest('button');if(!b)return;K=b.dataset.k;this.querySelectorAll('button').forEach(function(x){{x.classList.toggle('on',x===b)}});run()}});
q.addEventListener('input',run);var p=new URLSearchParams(location.search).get('q');if(p){{q.value=p}}run()}})();</script>
</main>"""
write('/search/',chrome('/search/','Search finp2p.info','Search every SuperApp, institution, network component, source, FAQ answer and guide section on finp2p.info.',search,extra_head=SEARCH_CSS))
