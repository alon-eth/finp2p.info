# Privacy pages for finp2p.info (launched 2026-11-06). exec'd by build.py.
import math
PJ=json.load(open(DATA/'privacy.json')); PS=PJ['sources']; PAPER=PJ['paper_url']
def pref(ids):
    out=[]
    for r in ids or []:
        s=PS.get(r)
        if s: out.append(f'<a class="ref" href="{s["url"]}" target="_blank" rel="noopener" title="{html.escape(s["title"])}">{html.escape(s["pub"].split(",")[0])} {s["date"][:4]}</a>')
    return ''.join(out)

# ---------- home hooks
PRIV_HOME=f'''<a class="privband" href="/privacy/"><span class="pill prod">New</span><span><b>Need-to-know privacy on FinP2P.</b> Only the parties to a trade see the trade, on every chain. Who sees what, privacy by chain, and what it costs.</span><span class="arr">→</span></a>
<style>.privband{{display:flex;gap:12px;align-items:center;margin:22px 0 4px;padding:14px 16px;border:1px solid var(--accent);border-radius:10px;background:var(--accent-soft);color:var(--muted);text-decoration:none;font-size:15px}}.privband b{{color:var(--ink)}}.privband .arr{{margin-left:auto;color:var(--accent);font-size:20px}}.privband:hover{{filter:brightness(1.03)}}</style>'''
PRIV_CARD='<a class="card" href="/privacy/" style="border-color:var(--accent)"><h3>Need-to-know privacy</h3><p>How FinP2P keeps trades visible only to the parties in them, across every chain: who sees what, privacy by chain, costs, and six questions to ask any vendor.</p></a>\n'

# ---------- the network diagram: three institutions, one trade, one bystander
DIAG='''<figure class="pfig"><svg viewBox="0 0 760 330" role="img" aria-labelledby="dgt dgd"><title id="dgt">Need-to-know privacy on FinP2P</title><desc id="dgd">Bank A and Fund B trade peer to peer through their own Routers. Bank C runs a Router on the same network and sees nothing. At settlement the trade lands on whichever chain the parties chose, using that chain's own privacy.</desc>
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="var(--accent)"/></marker></defs>
<g font-size="13">
<rect x="30" y="30" width="190" height="96" rx="8" fill="var(--paper)" stroke="var(--accent)" stroke-width="2"/><text x="125" y="58" text-anchor="middle" font-weight="600">Bank A</text><text x="125" y="80" text-anchor="middle" fill="var(--muted)">its own Router,</text><text x="125" y="98" text-anchor="middle" fill="var(--muted)">inside its own walls</text>
<rect x="540" y="30" width="190" height="96" rx="8" fill="var(--paper)" stroke="var(--accent)" stroke-width="2"/><text x="635" y="58" text-anchor="middle" font-weight="600">Fund B</text><text x="635" y="80" text-anchor="middle" fill="var(--muted)">its own Router,</text><text x="635" y="98" text-anchor="middle" fill="var(--muted)">inside its own walls</text>
<rect x="285" y="150" width="190" height="70" rx="8" fill="var(--ground)" stroke="var(--line)" stroke-dasharray="5 4"/><text x="380" y="178" text-anchor="middle" fill="var(--muted)" font-weight="600">Bank C</text><text x="380" y="200" text-anchor="middle" fill="var(--muted)">same network, sees nothing</text>
<path d="M222,64 L538,64" stroke="var(--accent)" stroke-width="2.5" marker-end="url(#ah)"/><path d="M538,92 L222,92" stroke="var(--accent)" stroke-width="2.5" marker-end="url(#ah)"/>
<text x="380" y="54" text-anchor="middle" fill="var(--accent)" font-weight="600">trade terms, peer to peer</text><text x="380" y="112" text-anchor="middle" fill="var(--muted)">signed proofs back, no central hub</text>
<path d="M125,128 L125,262" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="4 4"/><path d="M635,128 L635,262" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="4 4"/>
<rect x="30" y="262" width="700" height="48" rx="8" fill="var(--paper)" stroke="var(--line)"/><text x="380" y="284" text-anchor="middle" font-weight="600">Settlement on the chain the parties chose</text><text x="380" y="301" text-anchor="middle" fill="var(--muted)" font-size="12">using that chain's own privacy: zero-knowledge proofs, encryption, a private network, or a custodian's omnibus account</text>
</g></svg><figcaption><b>Business logic and trade data stay between the Routers in the trade.</b> Every institution keeps its own signed record of the trade. The chain only has to hide the settlement from everyone else. Drawn from Ownera's developer documentation and its paper on multi-chain need-to-know privacy.</figcaption></figure>'''

# ---------- who sees what
SEE=[('Trade terms: asset, price, size','yes','yes','no','no','hidden*','on request'),
     ('Who the counterparties are','yes','yes','no','no','depends on chain','on request'),
     ('Wallets, contract addresses, settlement instructions','yes','yes','no','no','depends on chain','on request'),
     ('Signed proof that the trade settled','yes','yes','no','no','no','on request'),
     ('Metadata: that a trade happened, and when','yes','yes','no','no','depends on chain','on request')]
def cell(v):
    c={'yes':'pv-y','no':'pv-n','on request':'pv-r'}.get(v,'pv-m'); return f'<td class="{c}">{html.escape(v)}</td>'
SEE_COLS=['Your Router','Counterparty Router','Other institutions on the network','Ownera, as vendor','Anyone reading the chain','Your regulator']
SEE_TBL=f'''<div class="tbl"><table class="pv"><thead><tr><th>Information</th>{''.join(f'<th>{c}</th>' for c in SEE_COLS)}</tr></thead><tbody>{''.join(f'<tr><td>{r[0]}</td>'+''.join(cell(v) for v in r[1:])+'</tr>' for r in SEE)}</tbody></table></div>
<p class="fn">* Hidden by the chain's own privacy feature at settlement. What still shows depends on the chain: see <a href="#chains">privacy by chain</a>. "Ownera, as vendor": Ownera supplies the Router as software, on-premises or as a managed service, and says it is not a party to any trade: no Ownera system sits between the Routers, sees the data or holds the keys. "Your regulator": an institution can hand a supervisor the trades in scope from its own signed record. This table is our reading of Ownera's public documentation and paper, not an Ownera statement.</p>'''

# ---------- privacy by chain
ST={'live':('live','prod'),'coming':('coming','prop'),'changed':('changed','')}
crow=[]
for c in PJ['chains']:
    lab,cls=ST[c['status']]
    fee=f'<b>{html.escape(c["fee"])}</b><br><span class="fn">{html.escape(c["fee_note"])}</span>' if c['fee'] else '<span class="fn">varies</span>'
    crow.append(f'<tr data-st="{c["status"]}"><td><b>{html.escape(c["name"])}</b><br><span class="fn">{html.escape(c["kind"])}</span></td><td data-th="Status"><span class="pill {cls}">{lab}</span><br><span class="fn">{html.escape(c["since"])}</span></td><td data-th="How it works">{html.escape(c["model"])}</td><td data-th="Hidden">{html.escape(c["hides"])}</td><td data-th="Still visible">{html.escape(c["visible"])}</td><td data-th="Typical fee">{fee}</td><td data-th="Sources">{pref(c["refs"])}</td></tr>')
CHAIN_TBL=f'''<div class="toolbar"><select id="pst"><option value="">All chains</option><option value="live">Live</option><option value="coming">Coming</option><option value="changed">Changed or removed</option></select></div>
<div class="tbl stack"><table class="pc" id="pct"><colgroup><col style="width:13%"><col style="width:11%"><col style="width:26%"><col style="width:15%"><col style="width:15%"><col style="width:10%"><col style="width:10%"></colgroup><thead><tr><th>Chain</th><th>Status</th><th>How it works</th><th>Hidden</th><th>Still visible</th><th>Typical fee</th><th>Sources</th></tr></thead><tbody>{''.join(crow)}</tbody></table></div>
<script>(function(){{var s=document.getElementById('pst');s.addEventListener('change',function(){{document.querySelectorAll('#pct tbody tr').forEach(function(r){{r.style.display=(!s.value||r.dataset.st===s.value)?'':'none'}})}})}})();</script>
<p class="fn">Status as of {PJ['snapshot']}. Fees are typical network fees for one token transfer from a live snapshot, not quotes, and exclude on- and off-ramp costs. FinP2P's Routers reach many of these chains through adapters (see the <a href="/network/">network page</a>); a chain appearing here does not mean it is connected to FinP2P today. Know of a change? Email <a href="mailto:alon@dgb.vc">alon@dgb.vc</a> with a public source.</p>'''

# ---------- cost chart (log scale, inline SVG, themed by CSS variables)
COST=[['Euroclear (legacy)',6.1,'2025 fee income per transaction','euroclear-2025']]+PJ['costs']; W,H0,RH=760,30,34; x0,x1=170,660
VMAX=6.5
def X(v): return x0+math.sqrt(v/VMAX)*(x1-x0)   # square-root scale: between linear and log
def money(v): return f'${v:.2f}' if v>=0.01 else f'${v:.4f}'.rstrip('0') if v>=0.0001 else f'${v:.7f}'.rstrip('0')
grid=''.join(f'<line x1="{X(t):.1f}" y1="{H0-8}" x2="{X(t):.1f}" y2="{H0+RH*len(COST)}" stroke="var(--line)"/><text x="{X(t):.1f}" y="{H0-14}" text-anchor="middle" font-size="11" fill="var(--faint)">${t:g}</text>' for t in (0.01,0.1,0.5,1,2,4,6))
bars=''
for i,(n,v,note,_) in enumerate(COST):
    y=H0+i*RH; hl=n.startswith('Euroclear'); col="var(--warm)" if hl else "var(--accent)"; w=X(v)-x0
    mark=f'<rect x="{x0}" y="{y+6}" width="{max(w,2):.1f}" height="18" rx="{4 if w>=8 else 1}" fill="{col}">'
    mark+=f'<title>{n}: {money(v)} per transaction{(" ("+note+")") if note else ""}</title></rect>'
    bars+=f'<text x="{x0-10}" y="{y+19}" text-anchor="end" font-size="13" fill="var(--ink)" font-weight="{600 if hl else 400}">{n}</text>{mark}<text x="{max(X(v),x0+2)+8:.1f}" y="{y+19}" font-size="12.5" fill="{"var(--ink)" if hl else "var(--muted)"}" stroke="var(--paper)" stroke-width="5" paint-order="stroke" font-weight="{600 if hl else 400}">{money(v)}{" gross" if n=="Canton" else ""}</text>'
COST_SVG=f'''<figure class="pfig"><svg viewBox="0 0 {W} {H0+RH*len(COST)+16}" role="img" aria-labelledby="cct ccd"><title id="cct">Typical network fee for one token transfer, by chain</title><desc id="ccd">Square-root scale in US dollars. Euroclear about $6 of fee income per settled transaction in 2025; Canton about $1 gross per median transaction; Ethereum and Avalanche about two cents; most other chains a fraction of a cent.</desc>{grid}{bars}</svg>
<figcaption><b>Cost per transaction, US dollars, square-root scale</b>: Euroclear's 2025 fee income per settled transaction (orange) against the typical network fee for one token transfer on each chain (green). Square-root scale, between a straight dollar scale and a log scale: note the uneven gridlines. The smallest bars are drawn at a minimum 2-pixel width so they stay visible. Live fee snapshot, {PJ['snapshot']}. Euroclear: about €1.9 billion of 2025 business income over about 359 million settled transactions, roughly €5.30 (about $6.10) each; that income also covers custody and asset servicing, not only settlement. Canton from the draft Universal Burn CIP (5North, Digital Asset), gross, before rewards returned to operators. Network fees only: today's rails also cover custody, compliance and reconciliation, and on-chain figures exclude on- and off-ramp costs. {pref(["euroclear-2025","canton-cip","fee-eth","fee-base","hedera-fees","fee-xrpl","fee-stellar"])}</figcaption></figure>'''

# ---------- one chain or many
CMP=[('Who sees the trade','Only the chain\'s nodes in the trade','Only the institutions\' Routers in the trade'),
     ('Where privacy applies','Assets on that chain','Every connected chain and legacy ledger, including delivery versus payment between chains'),
     ('Where assets and cash live','On, or moved to, that chain','Wherever they already are'),
     ('Liquidity and throughput','One chain\'s','The sum of the connected chains'),
     ('Application language','That chain\'s smart-contract language','Business logic written once, settled on any chain'),
     ('Fee per transaction','That chain\'s fee model','The fee of whichever chain the trade settles on'),
     ('Record of trades','On that chain','Each institution\'s own off-chain record, with counterparty-signed proofs for every trade')]
CMP_TBL=f'''<div class="tbl stack"><table><thead><tr><th></th><th>Need-to-know on one chain</th><th>Need-to-know across chains (FinP2P)</th></tr></thead><tbody>{''.join(f'<tr><td><b>{a}</b></td><td data-th="One chain">{b}</td><td data-th="Across chains">{c}</td></tr>' for a,b,c in CMP)}</tbody></table></div>'''

QS=[('Who can see my trade terms?','Not "is it encrypted," but exactly which parties can read price, size and asset.'),
    ('What metadata still leaks?','Even private systems can show who traded, when and how often. Ask for the list.'),
    ('Does the vendor see my trades?','The answer should be no, or governed by a contract you have read.'),
    ('How does my regulator get access?','Precisely and on request, from records you control, not through a back door.'),
    ('What happens if a chain fails, or switches its privacy feature off?','It has happened. Your record of the trade should not depend on any single chain surviving.'),
    ('Can I settle against cash on another chain, and what does it cost per trade at my volume?','Privacy that stops at the edge of one chain does not help if your cash lives on another.')]
QS_HTML='<ol class="pq">'+''.join(f'<li><label><input type="checkbox"> <b>{html.escape(q)}</b></label><span>{html.escape(a)}</span></li>' for q,a in QS)+'</ol>'

PCSS='''<style>.pfig{margin:20px 0 6px;background:var(--paper);border:1px solid var(--line);border-radius:8px;padding:16px 16px 10px;overflow-x:auto}.pfig svg{display:block;width:100%;height:auto;min-width:600px;font-family:var(--sans)}.pfig svg text{fill:currentColor}.pfig figcaption{font-size:13px;color:var(--muted);margin-top:10px;line-height:1.5}.pfig figcaption b{color:var(--ink);font-weight:600}
.fn{font-size:12.5px;color:var(--faint)}p.fn{max-width:none}
table.pv td,table.pv th{text-align:center}table.pv td:first-child,table.pv th:first-child{text-align:left}table.pv{min-width:760px}
.pv-y{color:var(--accent);font-weight:600}.pv-n{color:var(--faint)}.pv-m{color:var(--warm)}.pv-r{color:var(--ink)}
table.pc td{font-size:13px}
blockquote.pq1{margin:18px 0;padding:6px 0 6px 18px;border-left:3px solid var(--accent);font:400 21px/1.4 var(--serif);color:var(--ink);max-width:62ch}blockquote.pq1 cite{display:block;margin-top:6px;font:500 12.5px var(--sans);color:var(--muted);font-style:normal}
ol.pq{padding-left:0;list-style:none;counter-reset:q;max-width:72ch}ol.pq li{counter-increment:q;border-top:1px solid var(--line);padding:12px 0 12px 40px;position:relative}ol.pq li::before{content:counter(q);position:absolute;left:0;top:10px;width:26px;height:26px;border-radius:50%;border:1px solid var(--accent);color:var(--accent);font:600 13px/26px var(--sans);text-align:center}ol.pq label{cursor:pointer;color:var(--ink)}ol.pq input{accent-color:var(--accent);margin-right:6px}ol.pq span{display:block;color:var(--muted);font-size:14.5px;margin-top:2px}
.twol{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr));margin:18px 0}.twol .card h3{font-size:18px}
</style>'''

priv_page=f'''<main class="page wide" style="max-width:1080px"><div class="eyebrow">Need-to-know privacy</div>
<h1>Only the parties to a trade should see the trade.</h1>
<p class="lede">On most public blockchains, every trade is visible to anyone who looks. Institutions will not move serious volume onto rails like that. FinP2P keeps trade data between the institutions actually in the trade, and uses each chain's own privacy at settlement, so the same guarantee holds on every chain an institution uses. This page explains how, chain by chain, with a source for every claim.</p>
<p class="fn" style="font-size:14px">Why it matters: <a href="/privacy/why/">what public blockchains give away, and why regulators and central banks now say so &rarr;</a></p>
<nav class="toc" aria-label="On this page"><a href="#how">How FinP2P does it</a><a href="#who">Who sees what</a><a href="#chains">Privacy by chain</a><a href="#cost">What it costs</a><a href="#compare">One chain or many</a><a href="#questions">Six questions</a><a href="#read">Read more</a></nav>

<h2 id="how">How FinP2P keeps trades need-to-know</h2>
<p>Privacy has to work in two places: in each institution's own systems, where trades are negotiated and recorded, and on the ledger, where they settle. FinP2P keeps those two layers apart, which is what lets the same privacy work on any chain.</p>
{DIAG}
<ol class="steps">
<li><strong>Each institution runs its own Router.</strong> Its business logic and trade data stay inside its own perimeter.</li>
<li><strong>Only the Routers in a trade see the trade.</strong> Connections are peer to peer. There is no central hub that sees everything.</li>
<li><strong>Privacy starts before settlement.</strong> Wallets, contract addresses and settlement instructions are exchanged only between the parties, at the pre-trade and trade stages.</li>
<li><strong>Settlement uses the chain's own privacy.</strong> Zero-knowledge proofs or encryption on public chains, private networks, or a custodian's omnibus accounts. Proofs go only to the parties.</li>
<li><strong>Every institution keeps its own signed record.</strong> A complete off-chain log of its trades across every chain, with proofs signed by its counterparties. If a chain fails, pauses a feature or disappears, the record does not.</li>
</ol>
<div class="twol"><div class="card"><h3>Live in production</h3><p>Intraday repo between J.P. Morgan and HQLAx has run on FinP2P Routers since 2025, with $5 billion traded in the first month. {pref(["hqlax"])}</p></div><div class="card"><h3>Adding a chain keeps the guarantee</h3><p>Because privacy is managed at the Router, adding a chain, a counterparty or an application does not change who can see a trade. {pref(["ownera-arch"])}</p></div></div>

<h2 id="who">Who sees what</h2>
<p>One trade between two institutions on FinP2P, and what each party can see.</p>
{SEE_TBL}

<h2 id="chains">Privacy by chain</h2>
<p>Every network is adding privacy in its own way and on its own schedule. Some are live, some are coming, and some have pulled features back. This is the independent, sourced view of where each one stands: what it hides, what still shows, and what a transaction costs.</p>
{CHAIN_TBL}

<h2 id="cost">What a transaction costs</h2>
<p class="lede" style="color:var(--ink)">Even the highest-fee blockchains are far cheaper than legacy rails.</p>
<p>Euroclear's 2025 fee income works out to roughly $6 per settled transaction. The highest-fee chain here costs about a dollar; on most, a transfer costs a fraction of a cent. At institutional volumes, that is the difference between a budget line and a rounding error, and privacy should not mean giving it up.</p>
{COST_SVG}

<h2 id="compare">One chain or many: the trade-offs</h2>
<p>Canton deserves real credit: it was the first network to build need-to-know privacy into its design for institutions, and it delivers it well. On the question that matters most, who can see my trade, both models give the same answer. The differences are scope and economics. FinP2P supports Canton as one of its chains, including delivery versus payment between Canton and other ledgers.</p>
{CMP_TBL}
<p class="fn">Summarised from Ownera's white paper, Multi-Chain Need-to-Know Privacy (v1.2, October 2026), and Canton's own documentation. {pref(["canton-privacy","canton-sync"])}</p>

<h2 id="questions">Six questions to ask any privacy vendor</h2>
<p>Whatever infrastructure you are looking at, FinP2P or anyone else's, these questions separate real privacy from marketing. Tick them off as you go.</p>
{QS_HTML}

<h2 id="read">Read more</h2>
<p><a class="btn primary" href="{PAPER}" target="_blank" rel="noopener">Ownera's white paper: Multi-Chain Need-to-Know Privacy ↗</a> <a class="btn" href="/how-it-works/#who-sees-what">Who sees what in one transaction</a> <a class="btn" href="/faq/#privacy">Privacy FAQ</a></p>
<div class="note">finp2p.info is independent and is not run, reviewed or endorsed by Ownera. Alon Goren is on the board of Ownera, and Draper Goren Holm, a fund he manages, is an Ownera investor. Nothing here is investment advice.</div>
</main>'''
write('/privacy/',chrome('/privacy/','Need-to-know privacy on FinP2P','Only the parties to a trade should see the trade. How FinP2P keeps trades private on every chain: who sees what, privacy by chain, transaction costs, and six questions to ask any vendor.',priv_page,extra_head=PCSS,wide=True,
    extra_ld=[{"@type":"Article","@id":SITE+"/privacy/#article","headline":"Need-to-know privacy on FinP2P","author":{"@id":SITE+"/#publisher"},"publisher":{"@id":SITE+"/#publisher"},"datePublished":"2026-11-06","dateModified":TODAY,"mainEntityOfPage":SITE+"/privacy/","about":["Need-to-know privacy","FinP2P","tokenization","blockchain privacy"]},
              {"@type":"Dataset","@id":SITE+"/privacy/#chains","name":"Privacy by chain","description":"Status, privacy model, what is hidden and visible, and typical transfer fee for institutional blockchains, each with sources.","url":SITE+"/privacy/#chains","license":LICENSE_URL,"creator":{"@id":SITE+"/#publisher"},"temporalCoverage":PJ['snapshot']}]))

why_page=f'''<main class="page"><div class="eyebrow"><a href="/privacy/" style="color:inherit;text-decoration:none">Need-to-know privacy</a> · Explainer</div>
<h1>Why public blockchains are a problem for institutions</h1>
<p class="lede">Every trade on a public blockchain is a press release nobody asked to send. For a retail trader that is a quirk, and an opportunity to be front-run. For a bank, a fund or a market maker it is a deal-breaker.</p>

<p>Positions, hedges, counterparties and timing become public the moment they settle. Competitors can read them, bots can trade against them, and analytics firms can put a name on them.</p>
<h2>What the leakage costs</h2>
<div class="stats"><div class="stat"><b>1.55M</b><span>"sandwich" trades by one operation on Solana in 30 days, per ESMA</span></div><div class="stat"><b>~$13M</b><span>profit from those trades, buying just ahead of other people's orders</span></div></div>
<p>Europe's markets regulator called the practice widespread, often undisclosed, and at odds with "the principles of fairness and integrity." {pref(["esma-mev"])}</p>
<h2>Regulators are saying it out loud</h2>
<p>In December 2025 the SEC chairman made the case directly: institutions need to build positions, test strategies and provide liquidity without telegraphing them, and if every order and hedge were visible in real time, markets would invite "front-running, copycat behavior, and 'pile-on' dynamics." {pref(["sec-atkins"])}</p>
<blockquote class="pq1">Pushed in the wrong direction, crypto "could become the most powerful financial surveillance architecture ever invented."<cite>SEC Chairman Paul Atkins, 15 December 2025</cite></blockquote>
<p>Central banks reached the same place for the new rails. The BIS Project Agorá report, written with seven central banks and more than 40 firms: <strong>"A shared ledger does not require shared data."</strong> Information should be shared "on a need-to-know basis." {pref(["bis-agora"])} J.P. Morgan's blockchain unit wrote that the promise of tokenization "hinges critically on addressing institutional-grade privacy." {pref(["jpm-epic"])}</p>

<h2>What institutions need instead</h2>
<p>Traditional markets are already private, and not by accident: a repo between two banks is known to the two banks, their custodians and, when required, their regulator. Nobody else. That model has a name, need-to-know, and the job now is to make it true on-chain, on every chain institutions use.</p>
<p><a class="btn primary" href="/privacy/">How FinP2P delivers need-to-know privacy</a> <a class="btn" href="/privacy/#chains">Privacy by chain</a></p>
<div class="note">finp2p.info is independent and is not run, reviewed or endorsed by Ownera. Alon Goren is on the board of Ownera, and Draper Goren Holm, a fund he manages, is an Ownera investor.</div>
</main>'''
write('/privacy/why/',chrome('/privacy/why/','Why public blockchains are a problem for institutions','Every trade on a public blockchain is visible to anyone who looks. The evidence on front-running, and what the SEC, the BIS and J.P. Morgan say institutions need instead.',why_page,extra_head=PCSS,og_type='article',
    extra_ld=[{"@type":"Article","@id":SITE+"/privacy/why/#article","headline":"Why public blockchains are a problem for institutions","author":{"@id":SITE+"/#publisher"},"publisher":{"@id":SITE+"/#publisher"},"datePublished":"2026-11-06","dateModified":TODAY,"mainEntityOfPage":SITE+"/privacy/why/","isPartOf":{"@id":SITE+"/privacy/#article"}}]))

# ---------- how it works: who sees what in the example transaction
HIW_SEC='''<h2 id="who-sees-what">Who sees what in that transaction</h2>
<p>Need-to-know privacy applied to the primary sale above: <strong>only the parties to a trade see the trade.</strong> Each Router receives the instructions and proofs it needs, and nothing more.</p>
<div class="tblwrap"><table><thead><tr><th>Party</th><th>What it sees</th><th>What it does not see</th></tr></thead><tbody>
<tr><td>Investor's Router</td><td>The whole plan it authored, every receipt and proof</td><td>The issuer's or payment provider's internal systems</td></tr>
<tr><td>Issuer's Router</td><td>The sale, its own token instruction, the proofs it needs</td><td>The investor's other positions and trades</td></tr>
<tr><td>Payment provider's Router</td><td>The cash leg it holds and releases</td><td>Anything beyond the instructions and proofs it needs</td></tr>
<tr><td>Every other Router</td><td>Nothing</td><td>The trade exists at all</td></tr>
<tr><td>The chain</td><td>The settlement, hidden by its own privacy feature</td><td>The business logic, which never goes on-chain</td></tr>
</tbody></table></div>
<p>Our reading of Ownera's documentation and its privacy paper. More on the <a href="/privacy/">privacy page</a>, including privacy by chain.</p>
'''
def PRIV_HIW(body):
    k='<h2>3. What the Router works with</h2>'; assert k in body, 'how-it-works anchor missing'
    return body.replace(k,HIW_SEC+k,1)

# ---------- network page: privacy note on the chains layer
def PRIV_NET(net):
    k='<div class="tier"><div class="eyebrow">Underneath: chains'; assert k in net
    return net.replace(k,'<div class="note" style="margin-top:28px"><strong>Privacy on these chains:</strong> FinP2P keeps trade data between the Routers in the trade and uses each chain\'s own privacy at settlement. See <a href="/privacy/#chains">privacy by chain</a> for what each network hides, what still shows, and what it costs.</div>'+k,1)

# ---------- sources page
PRIV_SRC='<h2>Privacy sources</h2><p>Documents behind the <a href="/privacy/">privacy page</a>.</p><div class="tbl stack"><table><thead><tr><th>Source</th><th>Publisher · date</th></tr></thead><tbody>'+''.join(f'<tr><td data-th="Source"><a href="{s["url"]}" target="_blank" rel="noopener">{html.escape(s["title"])}</a></td><td data-th="Publisher" style="white-space:nowrap;color:var(--muted);font-size:12.5px">{html.escape(s["pub"])}<br>{s["date"]}</td></tr>' for s in PS.values())+'</tbody></table></div>'

# ---------- FAQ
PRIVACY_FAQ=[('Privacy',[
 ('What is need-to-know privacy?','Only the parties to a trade can see the trade. Everyone else on the network, and anyone reading the chain, sees nothing about it. It is how traditional markets already work: a repo between two banks is known to the two banks, their custodians and, when required, their regulator.'),
 ('Does Ownera see my trades?','FinP2P has no central hub. Each institution runs its own Router, and Routers in a trade connect peer to peer. Ownera\'s white paper says Ownera supplies the Router as software, installed on-premises or run as a managed service, and is not a party to any trade: no Ownera system sits between the Routers, sees the data or holds the keys. See <a href="/privacy/#who">who sees what</a>.'),
 ('What still leaks?','It depends on the chain used for settlement. Some hide amounts but not addresses; some hide everything from outsiders; some are not live yet. Some chains now hide metadata too; on public networks some transaction metadata may remain visible, as Ownera\'s own paper notes. See <a href="/privacy/#chains">privacy by chain</a>.'),
 ('How does a regulator get access?','Each institution keeps a complete off-chain record of its own trades, with proofs signed by its counterparties, so it can hand a supervisor exactly the trades in scope. Need-to-know includes the supervisor.'),
 ('What happens if a chain fails or switches its privacy off?','It has happened: Solana paused confidential transfers for a year after a proof bug, and Besu removed built-in private transactions in 2025. On FinP2P each institution\'s signed record does not depend on any single chain, and adding or swapping a chain does not change who can see a trade.'),
 ('How does FinP2P relate to Canton?','Canton was the first network to build need-to-know privacy into its design, and it does it well, within one network. FinP2P applies the same model one layer above the chains and supports Canton as one of them, including delivery versus payment between Canton and other ledgers. See <a href="/privacy/#compare">one chain or many</a>.'),
])]

# ---------- changes, llms
PRIVACY_CHANGES=[{"date":"2026-11-06","kind":"site","title":"New: need-to-know privacy on FinP2P","body":"A new privacy page: how FinP2P keeps trades visible only to the parties in them, who sees what, privacy by chain with sources, transaction costs by chain, and six questions to ask any privacy vendor. Plus a who-sees-what section on How it works and a privacy section in the FAQ.","link":"/privacy/"}]
PRIV_LLMS=f'- {SITE}/privacy/why/ : explainer: why public blockchains are a problem for institutions (ESMA front-running data, SEC, BIS, J.P. Morgan)\n- {SITE}/privacy/ : need-to-know privacy on FinP2P: who sees what, privacy by chain (status, what is hidden and visible, fee, sources), transaction costs, one chain vs many, six questions to ask\n'
PRIV_LLMS_FULL='\n\n# Need-to-know privacy ('+SITE+'/privacy/)\n- Rule: only the parties to a trade see the trade.\n- FinP2P keeps business logic and trade data between the Routers in the trade (peer to peer, no central hub) and uses each chain\'s native privacy at settlement; each institution keeps its own off-chain record with counterparty-signed proofs.\n- Live: J.P. Morgan and HQLAx intraday repo since 2025, $5B first month.\n\n## Privacy by chain (status as of '+PJ['snapshot']+')\n'+'\n'.join(f"- {c['name']} [{c['status']}, {c['since']}]: {c['model']} Hidden: {c['hides']} Visible: {c['visible']} Fee: {c['fee'] or 'varies'}. Sources: "+'; '.join(PS[r]['url'] for r in c['refs']) for c in PJ['chains'])
