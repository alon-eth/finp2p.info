# Developers, For AI agents and FAQ pages. exec'd by build.py after the other pages, so it shares build.py's
# globals (chrome, write, APPS, insts, PUBLIC, SITE, DATA_DATE...). Everything here summarizes Ownera's PUBLIC
# documentation and links to it; nothing here comes from private material. Re-check links when docs move.
DOCS='https://finp2p-docs.ownera.io'
CHECKED='2026-10-13'   # when the Ownera links and facts on these pages were last checked by hand
def d(p): return f'{DOCS}/{p}'
def a(url,label): return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
def code(txt,copy=True,wrap=False): return f'<pre{" data-copy" if copy else ""}{" style=\"white-space:pre-wrap\"" if wrap else ""}><code>{html.escape(txt.strip())}</code></pre>'
OFFICIAL=f'''<div class="note"><strong>Community guide, not official documentation.</strong> finp2p.info is an independent community resource. It is not run, reviewed or endorsed by Ownera. This page summarizes Ownera's public documentation so more builders can find their way onto the network; where it and {a(DOCS+'/','the official docs')} disagree, the official docs win. Sandbox access, credentials and listing decisions come from Ownera, not from us. Links checked {CHECKED}.</div>'''
CHAINS=next(l for l in json.load(open(DATA/'layers.json'))['layers'] if l['id']=='chains')['items']

# ---------- /developers/
dev=f"""<main class="page"><div class="eyebrow">Developers</div><h1>Build on FinP2P: a field guide.</h1>
<p class="lede">How to connect an app, a ledger, a custody service or a data feed to Ownera's FinP2P network, written by people who have done it, with every step linked into Ownera's own documentation.</p>
{OFFICIAL}
<nav class="toc" aria-label="On this page"><a href="#paths">Pick your path</a><a href="#model">The model</a><a href="#flow">How a call flows</a><a href="#auth">Authentication</a><a href="#hello">Hello world</a><a href="#adapters">Adapters</a><a href="#listing">Getting listed</a><a href="#code">Code and endpoints</a><a href="/agents/">For AI agents</a><a href="/faq/">FAQ</a></nav>

<h2 id="paths">Pick your path</h2>
<p>Ownera's docs split builders into two kinds, plus the institutions that run the network and the people who only need to read it. Find yourself below.</p>
<div class="cards">
<div class="card"><h3>Business application</h3><p>A trading venue, issuance platform, wallet, investor portal, treasury or lending tool. You keep your product and add a small integration service that talks to a Router: REST under <code>/finapi</code> for actions, GraphQL for reads. Your users, accounts and orders map to investor profiles, asset profiles and intents.</p><p>{a(d('docs/hello-world-sample'),'Start with Hello World ↗')}</p></div>
<div class="card"><h3>Utility or connector</h3><p>A ledger, custody or signing service, payment rail, data feed, compliance check. Other apps consume you, so you implement an adapter API that the Router calls. Ledger, custody and data provider specs are public, with event-driven "proxy" variants if you cannot expose a REST server.</p><p><a href="#adapters">See the adapters</a></p></div>
<div class="card"><h3>Institution</h3><p>A bank, market infrastructure or asset manager. You run your own Router (one per organisation) inside your own environment, keep your keys and data, and choose apps from the {a('https://superapps.ownera.io/','SuperApps store')}. Deployment is arranged with Ownera directly.</p><p>{a(d('docs/superapp-architecture'),'Router integration architecture ↗')}</p></div>
<div class="card"><h3>Researcher, analyst or AI agent</h3><p>No credentials needed. The store has a public JSON API, Ownera's docs publish an llms.txt and an MCP server, and this site's whole dataset is one CC BY file.</p><p><a href="/agents/">The agent guide</a></p></div>
</div>

<h2 id="model">The model in seven terms</h2>
<dl class="terms">
<dt>Router</dt><dd>The FinP2P node each institution runs. Routers talk to each other peer to peer; there is no shared ledger in the middle. ISVs usually connect to their clients' Routers rather than running one. {a(d('docs/the-router-fundamentals'),'Router fundamentals ↗')}</dd>
<dt>SuperApp</dt><dd>Any application or service connected to a Router. Ownera's store lists {len(APPS)} of them today. {a(d('docs/what-is-a-superapp'),'Integration paths ↗')}</dd>
<dt>Profile</dt><dd>A global identity for an owner (investor) or an asset. Owner identities are secp256k1 keys. Profiles are shared explicitly with other organisations.</dd>
<dt>Intent</dt><dd>A declarative statement of what should happen: a primary sale, a buying or selling intent, a loan, a transfer, a redemption. It says what, never how on any particular chain. {a(d('docs/orchestration-plan-capabilities'),'Intent-based orchestration ↗')}</dd>
<dt>Orchestration plan</dt><dd>The step-by-step workflow the Router generates from an intent and proposes to the other participants' Routers, who approve and execute it together. You submit intents and watch plans; you rarely write plans.</dd>
<dt>Adapter</dt><dd>The bridge between a Router and a ledger, custody provider or data source. Adapters are where chain-specific code lives.</dd>
<dt>Certificate</dt><dd>A signed attribute attached to a profile: KYC, AML, accreditation, company info, NAV. Schemas are public in {a('https://github.com/owneraio/finp2p-certificates-spec','finp2p-certificates-spec')}.</dd>
</dl>
<p>Resource IDs look like <code>organization:resource-type:uuid</code>, so an ID tells you which organisation's Router owns it.</p>

<h2 id="flow">How a call flows</h2>
<ol class="steps">
<li><strong>Something happens in your app</strong>: an investor clicks buy, a desk books a repo, a rebalancer fires.</li>
<li><strong>Your integration creates an intent</strong> and submits it to your local Router over REST.</li>
<li><strong>The Router builds an orchestration plan</strong> and proposes it to every participating Router.</li>
<li><strong>The Routers execute it peer to peer</strong>, step by step, with full consensus; adapters move the asset and the cash on whatever ledgers they live on.</li>
<li><strong>Results and proofs come back</strong>. Most calls are asynchronous: you get a correlation id (<code>cid</code>) and poll the operation, or read the plan over GraphQL.</li>
</ol>
<p>The <a href="/how-it-works/">How it works</a> page draws this end to end with a repo trade.</p>

<h2 id="auth">Authentication</h2>
<p>Every request to a Router carries a fresh, single-use JWT signed RS256 with your own private key. Onboarding: generate an RSA key pair, send Ownera the public key, receive an API key and your organisation ID, then sign a new token for every call (it expires 30 seconds after issue, and the nonce cannot be reused).</p>
{code('''openssl genrsa -out prv.key 4096
openssl rsa -in prv.key -RSAPublicKey_out -out pub.key   # send pub.key to Ownera''')}
{code('''// JWT payload, one per request, signed RS256
{
  "aud": "<ORGANIZATION_ID>",
  "apiKey": "<API_KEY>",
  "nonce": "<24 random bytes + 8-byte epoch, hex>",
  "iat": 1760380800,
  "exp": 1760380830
}''',False)}
<p class="note" style="max-width:none">Heads-up: the {a(d('docs/hello-world-sample'),'Hello World')} sample puts the API key in an <code>apiKey</code> claim. The {a(d('reference/authorization'),'Authorization reference')} calls it <code>sub</code> in its prose but uses <code>apiKey</code> in its own code sample. In our own testing with Ownera's engineers (Sep 2026) the auth service read <code>apiKey</code>; setting both <code>sub</code> and <code>apiKey</code> to the API key works. The same reference sets a 5-second default clock-skew tolerance for the nonce, so keep server clocks in sync.</p>

<h2 id="hello">Hello world, in order</h2>
<p>Ownera's sandbox comes with a simulated custody service, a simulated payment service and at least one test asset shared with you. The {a(d('docs/hello-world-sample'),'Hello World sample')} walks through it with full request and response bodies:</p>
<div class="tbl stack"><table><thead><tr><th>#</th><th>Call</th><th>What it does</th></tr></thead><tbody>
<tr><td>1</td><td data-th="Call"><code>POST /finapi/profiles/owner</code></td><td data-th="What it does">Create an investor (owner) profile</td></tr>
<tr><td>2</td><td data-th="Call"><code>POST /finapi/profiles/owner/{{id}}/account</code></td><td data-th="What it does">Link the investor to a custody service; async, poll <code>GET /finapi/operations/status/{{cid}}</code></td></tr>
<tr><td>3</td><td data-th="Call"><code>POST /finapi/profiles/{{id}}/certificates</code></td><td data-th="What it does">Attach KYC, AML or accreditation certificates</td></tr>
<tr><td>4</td><td data-th="Call"><code>POST /finapi/profiles/{{id}}/share</code></td><td data-th="What it does">Share the investor profile with the issuer's organisation</td></tr>
<tr><td>5</td><td data-th="Call"><code>POST /graphql</code></td><td data-th="What it does">Find assets shared with you and their open intents</td></tr>
<tr><td>6</td><td data-th="Call"><code>POST /finapi/tokens/execute</code></td><td data-th="What it does">Execute against an intent, for example buy into a primary sale</td></tr>
<tr><td>7</td><td data-th="Call"><code>POST /graphql</code></td><td data-th="What it does">Watch the execution plan until it completes</td></tr>
</tbody></table></div>
<p>There is also a {a(d('reference/dryrunexecutetoken'),'dry-run endpoint')} that predicts the plan for an intent without executing it. Use it while you build.</p>

<h2 id="adapters">Adapters: plugging in a ledger, custody or data</h2>
<p>If other apps will consume what you build, you implement one of these APIs and the Router calls you. The official skeletons are the fastest start.</p>
<div class="tbl stack"><table><thead><tr><th>Adapter</th><th>You implement</th><th>Spec</th><th>Starter code</th></tr></thead><tbody>
<tr><td><b>Ledger adapter</b><br><span style="font-size:12.5px;color:var(--muted)">tokenization platforms, chains, legacy registers</span></td><td data-th="You implement">Create asset, issue, transfer, redeem, move, hold, release, rollback, balances, receipts, investor accounts, execution-plan approval</td><td data-th="Spec">{a(d('reference/ledger-adapter-spec'),'Ledger Adapter ↗')}</td><td data-th="Starter code">{a('https://github.com/owneraio/finp2p-nodejs-skeleton-adapter','Node.js skeleton')}<br>{a('https://github.com/owneraio/finp2p-java-skeleton-adapter','Java skeleton')}<br>{a('https://github.com/owneraio/finp2p-ethereum-adapter','EVM adapter')}</td></tr>
<tr><td><b>Custody adapter</b><br><span style="font-size:12.5px;color:var(--muted)">key management and signing</span></td><td data-th="You implement">Create accounts (key pairs), signature requests over payload hashes, plan approval</td><td data-th="Spec">{a(d('reference/custody-adapter-api-introduction'),'Custody Adapter ↗')}<br>{a(d('reference/signature-schemes'),'Signature schemes ↗')}</td><td data-th="Starter code"></td></tr>
<tr><td><b>Data provider adapter</b><br><span style="font-size:12.5px;color:var(--muted)">pricing, risk, reference and market data</span></td><td data-th="You implement">Fetch or subscribe asset data; the Router maps identifiers (an ISIN, say) to providers with data rules and ingests what you return</td><td data-th="Spec">{a(d('reference/data-provider-adapter-api-introduction'),'Data Provider Adapter ↗')}<br>{a(d('reference/ingestassetdata'),'Ingest asset data ↗')}</td><td data-th="Starter code">{a('https://github.com/alon-eth/lunarcrush-finp2p-adapter','LunarCrush data adapter')} <span style="font-size:12px;color:var(--faint)">(ours, see disclosure)</span></td></tr>
<tr><td><b>Proxy variants</b><br><span style="font-size:12.5px;color:var(--muted)">event-driven, no inbound REST</span></td><td data-th="You implement">Pull commands over a Server-Sent Events stream, acknowledge them, post the result back with the command's <code>cid</code></td><td data-th="Spec">{a(d('reference/proxy-ledger-adapter-api-introduction'),'Proxy Ledger ↗')}<br>{a(d('reference/proxy-custody-adapter-api-introduction'),'Proxy Custody ↗')}</td><td data-th="Starter code"></td></tr>
</tbody></table></div>
<p>Chains already reached by adapters, per public sources: {html.escape(', '.join(i['name'] for i in CHAINS))}. Full list with sources on the <a href="/network/">network page</a>.</p>

<h2 id="listing">Getting listed on the SuperApps store</h2>
<p>Ownera publishes the process at {a('https://superapps.ownera.io/onboarding-howto','superapps.ownera.io/onboarding-howto')}. In short:</p>
<ol class="steps">
<li><strong>Sign up</strong> to the SuperApp Portal.</li>
<li><strong>Create your company profile</strong>: legal entity, registration, jurisdiction.</li>
<li><strong>Submit a draft SuperApp</strong>: name, description, use case, asset classes, optional demo.</li>
<li><strong>Review and agreements</strong>: Ownera due diligence (KYC), then NDA, Platform Terms, Partnership and Commercial agreements. You are listed in development status.</li>
<li><strong>Connect to the sandbox Router</strong> and validate connectivity.</li>
<li><strong>Go to production</strong> once testing and agreements are done.</li>
</ol>
<p>Ownera publishes no fees for listing. Once you are listed, <a href="/build/">tell us</a> and you will show up on this site's map with the next data refresh.</p>

<h2 id="code">Open code and public endpoints</h2>
<div class="tbl stack"><table><thead><tr><th>What</th><th>Where</th><th>Auth</th></tr></thead><tbody>
<tr><td>Official docs, guides and API reference</td><td data-th="Where">{a(DOCS+'/','finp2p-docs.ownera.io')}</td><td data-th="Auth">none</td></tr>
<tr><td>Docs index for LLMs</td><td data-th="Where">{a(DOCS+'/llms.txt','finp2p-docs.ownera.io/llms.txt')}</td><td data-th="Auth">none</td></tr>
<tr><td>Docs MCP server (search and read the OpenAPI specs from an agent)</td><td data-th="Where"><code>{DOCS}/mcp</code></td><td data-th="Auth">none to read</td></tr>
<tr><td>SuperApps store API: apps, participant types, categories</td><td data-th="Where">{a('https://superapps.ownera.io/api/apps','/api/apps')} · {a('https://superapps.ownera.io/api/types','/api/types')} · {a('https://superapps.ownera.io/api/categories','/api/categories')}</td><td data-th="Auth">none</td></tr>
<tr><td>Ownera on GitHub: adapters, certificate schemas, samples</td><td data-th="Where">{a('https://github.com/owneraio','github.com/owneraio')}</td><td data-th="Auth">public</td></tr>
<tr><td>This site's dataset (apps, derived connections, institutions, sources)</td><td data-th="Where"><a href="/data/graph.json">/data/graph.json</a> · <a href="/data/index.json">/data/index.json</a></td><td data-th="Auth">none, CC BY 4.0</td></tr>
<tr><td>A Router (sandbox or production)</td><td data-th="Where">URL issued by Ownera or your institution</td><td data-th="Auth">RS256 JWT per call</td></tr>
</tbody></table></div>
<p class="note" style="max-width:none">Recent changes in Ownera's open code (checked 6 Nov 2026): the {a('https://github.com/owneraio/finp2p-ethereum-adapter/releases/tag/v0.29.0','EVM adapter v0.29.0')} shipped on 12 Oct; the {a('https://github.com/owneraio/finp2p-nodejs-skeleton-adapter','Node.js skeleton')} now maps swap and move execution-plan instructions and keeps the Router's EIP-712 type definitions on signing templates (20 to 22 Oct); the {a('https://github.com/owneraio/finp2p-certificates-spec','certificates spec')} added collateral-terms v3, with the haircut method set on the agreement (18 to 20 Oct); and the {a('https://github.com/owneraio/finp2p-tezos-adapter','Tezos adapter')} was archived on 1 Nov.</p>

<h2>Shipped something, or found a mistake here?</h2>
<p>If you built on FinP2P, <a href="/build/">tell us</a>: we will add it to the map, and if you are a founder, Draper Goren Blockchain may want to back it. If this guide has drifted from the official docs, email <a href="mailto:alon@dgb.vc">alon@dgb.vc</a> and we will fix it the same week.</p>
</main>"""
write('/developers/',chrome('/developers/','Build on FinP2P: developer guide','A community field guide to building on Ownera\'s FinP2P network: integration paths, the Router model, authentication, hello world, ledger, custody and data adapters, and how to get a SuperApp listed. Independent of Ownera.',dev,
    extra_ld=[{"@type":"TechArticle","headline":"Build on FinP2P: a field guide","url":SITE+"/developers/","dateModified":TODAY,"author":{"@id":SITE+"/#publisher"},"about":["FinP2P","Ownera Router","SuperApps"],"isBasedOn":DOCS+"/"}]))

# ---------- /agents/
MCP_CC=f'claude mcp add --transport http ownera-docs {DOCS}/mcp'
MCP_JSON=json.dumps({"mcpServers":{"ownera-docs":{"type":"http","url":f"{DOCS}/mcp"}}},indent=2)
RULES=f'''You are working with Ownera's FinP2P network. Ground rules:
- finp2p.info is an independent community resource, not Ownera. For APIs and behaviour, Ownera's docs ({DOCS}) are authoritative; use the ownera-docs MCP server or {DOCS}/llms.txt instead of guessing endpoints.
- For whether an app is listed and its status (production, sandbox, development), the live store API (https://superapps.ownera.io/api/apps) is authoritative. finp2p.info is a snapshot; check its date.
- On finp2p.info, app-to-app connections are derived by stated rules, not published by Ownera. Say "derived" when you use them.
- An institution named on finp2p.info is publicly connected to an app or the network in the cited source. That does not mean it transacts on FinP2P in production. Quote the source.
- Cite the URL behind every factual claim about the network.
- Router calls need Ownera-issued credentials (API key, organisation ID, Router URL) and a fresh RS256 JWT per request. Never ask a user to paste a private key into the conversation; have them keep it in a file or secret store your code reads.
- Nothing about FinP2P, Ownera or any listed company is investment advice.'''
CURL='''# every app on the store, live
curl -s https://superapps.ownera.io/api/apps | jq '.[] | {name, status, company: .companyName}'

# finp2p.info snapshot: which institutions attach to which apps, and why
curl -s https://finp2p.info/data/graph.json | jq '.instEdges[] | {inst, app, note}'

# the public documents behind one institution
curl -s https://finp2p.info/data/graph.json \\
  | jq --arg n "HQLAx" '. as $g | .institutions[] | select(.name==$n) | .refs[] | $g.sources[.]' '''
RECIPES=[
 ('Scaffold a ledger adapter','A coding agent in an empty repo.',
  f'''Using the ownera-docs MCP server, read the Ledger Adapter specification (list-specs, then list-endpoints on it).
Clone https://github.com/owneraio/finp2p-nodejs-skeleton-adapter and map every spec endpoint to its handler in the skeleton.
Implement issue, transfer, redeem, hold, release and balance against <MY LEDGER>, keeping operations async with a cid.
Write a test for each operation. Do not invent endpoints or fields that are not in the spec; if something is unclear, list it as a question for Ownera.'''),
 ('Build a Router client','A coding agent adding FinP2P to an existing backend.',
  f'''Read {DOCS}/docs/hello-world-sample.md and {DOCS}/reference/authorization.md.
Write a small client module with: a signer that makes a fresh RS256 JWT per request (30 s expiry, 24 random bytes + 8-byte epoch nonce, hex), createOwnerProfile, addAccount, addCertificate, shareProfile, a GraphQL query for shared assets with open intents, executeIntent, and an operation poller.
Load the API key, organisation ID, Router URL and private key path from environment variables. Put the API key in both the sub and apiKey claims: the docs name it sub in prose but use apiKey in their code samples, and Routers have been seen to read apiKey.'''),
 ('Answer "who is on the network?"','A research assistant.',
  '''Fetch https://finp2p.info/data/graph.json and https://superapps.ownera.io/api/apps.
List institutions by kind with the app each attaches to, quoting the source title and URL for each.
Mark which apps are in production on the live store today, and flag any difference from the finp2p.info snapshot.
Do not describe any institution as live in production unless its cited source says so.'''),
]
recipes=''.join(f'<h3 style="margin-top:22px">{t}</h3><p style="margin:2px 0 0;font-size:14px">{w}</p>{code(p,wrap=True)}' for t,w,p in RECIPES)
agents=f"""<main class="page"><div class="eyebrow">For AI agents and LLMs</div><h1>Working with FinP2P from an agent.</h1>
<p class="lede">This page is for language models, coding agents, and the people who set them up. It lists what an agent can read without credentials, how to connect it to Ownera's official documentation, the ground rules that keep its answers accurate, and prompts that work.</p>
{OFFICIAL}
<h2>Machine-readable entry points</h2>
<div class="tbl stack"><table><thead><tr><th>Resource</th><th>URL</th><th>What it is</th></tr></thead><tbody>
<tr><td>finp2p.info llms.txt</td><td data-th="URL"><a href="/llms.txt">/llms.txt</a></td><td data-th="What it is">Short index of this site and the facts to quote correctly</td></tr>
<tr><td>finp2p.info llms-full.txt</td><td data-th="URL"><a href="/llms-full.txt">/llms-full.txt</a></td><td data-th="What it is">The whole site as plain text in one file: every app, institution, source, and this guide</td></tr>
<tr><td>Data catalog</td><td data-th="URL"><a href="/data/index.json">/data/index.json</a></td><td data-th="What it is">Every dataset and endpoint, with field descriptions and licence</td></tr>
<tr><td>Network graph</td><td data-th="URL"><a href="/data/graph.json">/data/graph.json</a></td><td data-th="What it is">Apps, derived connections, institutions, sources. CC BY 4.0</td></tr>
<tr><td>Ownera docs index</td><td data-th="URL">{a(DOCS+'/llms.txt',DOCS.replace('https://','')+'/llms.txt')}</td><td data-th="What it is">Every official guide and API page as Markdown (append <code>.md</code> to any docs URL)</td></tr>
<tr><td>Ownera docs MCP</td><td data-th="URL"><code>{DOCS}/mcp</code></td><td data-th="What it is">Streamable HTTP MCP server over the OpenAPI specs</td></tr>
<tr><td>SuperApps store API</td><td data-th="URL">{a('https://superapps.ownera.io/api/apps','superapps.ownera.io/api/apps')}</td><td data-th="What it is">Live list of apps with status, company, categories, partners</td></tr>
</tbody></table></div>

<h2>Connect your agent to Ownera's docs</h2>
<p>Ownera runs an MCP server over its OpenAPI specs. It is public to read and exposes five tools: <code>list-specs</code>, <code>list-endpoints</code>, <code>search-endpoints</code>, <code>get-endpoint</code> and <code>execute-request</code>. The first four are read-only and are what you want while building. <code>execute-request</code> sends real HTTP calls, so it only does anything with Router credentials, and you should keep it switched off unless a human is watching.</p>
<p><strong>Claude Code:</strong></p>{code(MCP_CC)}
<p><strong>Claude Desktop, Cursor and other clients</strong> (<code>mcpServers</code> config):</p>{code(MCP_JSON)}
<p>Without MCP, point the agent at {a(DOCS+'/llms.txt','the docs llms.txt')} and let it fetch the <code>.md</code> pages it needs.</p>

<h2>Ground rules to give your agent</h2>
<p>Paste this into a system prompt, a project instructions file (<code>CLAUDE.md</code>, <code>AGENTS.md</code>, <code>.cursorrules</code>) or a custom GPT. It stops the common mistakes: invented endpoints, treating a name on a partner list as a live deployment, and treating this site as official.</p>
{code(RULES,wrap=True)}

<h2>Read the network without credentials</h2>
{code(CURL)}
<p><code>graph.json</code> fields: <code>nodes</code> (one per SuperApp: id, name, status, company, role, categories, participant types, store URL), <code>edges</code> (derived app-to-app connections with a kind and a reason), <code>institutions</code> (name, kind, source ids), <code>instEdges</code> (institution to app, with a note), <code>sources</code> (id to title, publisher, date, URL). Full descriptions are in <a href="/data/index.json">/data/index.json</a>.</p>

<h2>Prompts that work</h2>{recipes}

<h2>Citing this site</h2>
<p>finp2p.info, "page title", Draper Goren Blockchain, data snapshot {DATA_DATE}. https://finp2p.info/</p>
<p>The data is CC BY 4.0: reuse it anywhere, including in training data and retrieval indexes, with attribution. Crawlers are welcome; <a href="/robots.txt">robots.txt</a> allows everything. Please link the page you used so readers can check the source behind each claim.</p>
</main>"""
agents=re.sub(r'<h2>([^<]+)</h2>',lambda m:f'<h2 id="{re.sub("[^a-z]+","-",m.group(1).lower()).strip("-")}">{m.group(1)}</h2>',agents)
write('/agents/',chrome('/agents/','FinP2P for AI agents and LLMs','How AI agents and LLMs can work with Ownera\'s FinP2P network: llms.txt, the official docs MCP server, public data endpoints, ground rules for accurate answers and tested prompts. Independent of Ownera.',agents,
    extra_ld=[{"@type":"TechArticle","headline":"Working with FinP2P from an agent","url":SITE+"/agents/","dateModified":TODAY,"author":{"@id":SITE+"/#publisher"},"about":["FinP2P","Model Context Protocol","llms.txt"]}]))

# ---------- /faq/
live=[n['name'] for n in nodes if n['status']=='production']
FAQ=[
 ('About this site',[
  ('Is finp2p.info an Ownera website?',f'No. finp2p.info is an independent community resource maintained by Alon Goren and the Draper Goren Blockchain venture studio. It is not operated, sponsored, reviewed or endorsed by Ownera or XCap Ecosystem Ltd, and Ownera has no editorial input. The official sources are {a("https://www.ownera.io/","ownera.io")}, {a(DOCS+"/","Ownera\'s developer docs")} and the {a("https://superapps.ownera.io/","SuperApps store")}.'),
  ('Why does it exist?','To help more people understand, connect to and build on the network. Ownera\'s store, docs and industry reports contain a lot of public information, spread across many places. This site puts it in one map with a source on every claim.'),
  ('Does the maintainer have a conflict of interest?','Yes, and it is disclosed on every page. Alon Goren is on the board of Ownera, and Draper Goren Holm, a fund he manages, is an Ownera investor. He is also on the board of LunarCrush, the data provider behind a proposed SuperApp. That is why every institution on the site needs a public source and anything without one is left off. See the <a href="/about/">about page</a>.'),
  ('How current is the data?',f'The app and institution data is a snapshot taken on {DATA_DATE}, from the store\'s public API and the documents on the <a href="/sources/">sources page</a>. For an app\'s current status, check the store itself.'),
  ('Something about my company is wrong. How do I fix it?','Email <a href="mailto:alon@dgb.vc">alon@dgb.vc</a>, or open a pull request against <code>data/graph.json</code> in the <a href="https://github.com/alon-eth/finp2p.info">public repository</a>, with the correction and a public source. Corrections ship the same week.'),
 ]),
 ('The network',[
  ('What is FinP2P?','FinP2P is Ownera\'s application-layer network for tokenized finance. Each institution runs its own Router; Routers coordinate transactions peer to peer, and assets and cash stay on whatever ledgers they already live on. Applications connected to Routers are called SuperApps. <a href="/how-it-works/">How it works</a> has the diagrams.'),
  ('Is FinP2P a blockchain? Is there a token?','No to the first: it is not a blockchain and has no shared ledger. It orchestrates transactions across existing blockchains and traditional ledgers. Ownera\'s public documentation describes no network token.'),
  ('Which blockchains does it reach?',f'Per public sources: {html.escape(", ".join(i["name"] for i in CHAINS))}. Each one, with its source, is on the <a href="/network/">network page</a>.'),
  ('What is live in production?',f'The flagship is intraday repo between J.P. Morgan and HQLAx, in production since 2025 with $5 billion traded in its first month ({a("https://www.hqla-x.com/post/j-p-morgan-hqlax-and-ownera-launch-intraday-repo-solution-with-5bn-traded-in-the-first-month","HQLAx")}). On the store, {len(live)+1} of {len(APPS)} listings carry production status: {html.escape(", ".join(live))}, plus the FinP2P Router License itself.'),
  ('Is Ownera security-certified?',f'Ownera states that it is ISO 27001 (information security management) and ISO 27017 (cloud services) certified on its {a("https://www.ownera.io/trust","Trust page")}. Its {a("https://143965173.fs1.hubspotusercontent-eu1.net/hubfs/143965173/External%20Share/Ownera_Multi-Chain_Need-to-Know_Privacy_White_Paper.pdf","October 2026 white paper")} adds SOC 2 Type II, and says the scope of each certificate is available from Ownera on request. We have not seen the certificates themselves.'),
  ('What does Ownera build on the network itself?',f'Besides the Router, Ownera publishes its own applications on the store, and the {a("https://ttm.ownera.io/","Tokenized Treasury Manager")}: inventory and funding, collateral management and a treasury hub for minute-precision intraday repo with atomic delivery versus payment across chains. See the <a href="/network/">network page</a>.'),
  ('If a bank is named on this site, does it use FinP2P?','Not necessarily. A name means the institution is publicly connected to an app or to the network in the cited document, which might be a production deployment, a sandbox report or a vendor\'s partner page. Read the citation on the <a href="/institutions/">institutions page</a>.'),
  ('Where do the app-to-app connections on the map come from?','Ownera does not publish them. We derive them from each app\'s category, participant types and stated orchestration using ten explicit rules, listed on the <a href="/map/">map page</a>. They are our reading, not an Ownera statement.'),
 ]),
 ('Building',[
  ('How do I start building on FinP2P?','Decide whether you are building a business application (your product talks to a Router) or a utility or connector (the Router calls your adapter). Then follow the <a href="/developers/">developer guide</a>, which links each step to Ownera\'s official docs.'),
  ('Do I need to run my own Router?','Usually not. Financial institutions run Routers, one per organisation. If you are a software vendor or fintech, your app connects to your clients\' Routers, either as SaaS or deployed inside the institution.'),
  ('How do I get sandbox access and credentials?',f'From Ownera. You generate an RSA key pair, send Ownera the public key, and receive an API key, an organisation ID and a sandbox Router URL. The process is in the {a(DOCS+"/reference/authorization","Authorization reference")}, and listing starts at {a("https://superapps.ownera.io/onboarding-howto","superapps.ownera.io/onboarding-howto")}.'),
  ('What languages and tools can I use?','Anything that speaks HTTPS, signs RS256 JWTs and does GraphQL. Ownera publishes adapter skeletons in Node.js and Java and a reference adapter for EVM chains on <a href="https://github.com/owneraio" target="_blank" rel="noopener">GitHub</a>.'),
  ('How do I get my app listed on the SuperApps store?','Six steps, run by Ownera: portal sign-up, company profile, draft submission, review and agreements (including KYC due diligence), sandbox integration, then promotion to production. Summary in the <a href="/developers/#listing">developer guide</a>.'),
  ('What does listing cost?','Ownera does not publish listing fees. Ask Ownera.'),
  ('Can I build a data, risk or analytics app?','Yes. Data providers implement the Data Provider adapter, and the Router routes asset identifiers to providers with data rules. Kaiko, Particula and ZeroBeta are examples on the store, and Draper Goren Blockchain open-sourced a <a href="https://github.com/alon-eth/lunarcrush-finp2p-adapter" target="_blank" rel="noopener">reference data adapter</a>.'),
 ]),
 ('AI agents and data',[
  ('Can I use this site\'s data?','Yes. <a href="/data/graph.json">/data/graph.json</a> is CC BY 4.0: reuse it anywhere with attribution to finp2p.info.'),
  ('Is there an API or an MCP server?',f'For FinP2P itself, Ownera runs a public docs MCP server at <code>{DOCS}/mcp</code> and the store has a public JSON API. This site is static: everything is in <a href="/llms.txt">/llms.txt</a>, <a href="/llms-full.txt">/llms-full.txt</a> and <a href="/data/index.json">/data/index.json</a>. Setup is on the <a href="/agents/">agents page</a>.'),
  ('Can an AI agent transact on FinP2P?','Ownera\'s docs list autonomous systems (automated trading, scheduled rebalancing, event-driven workflows) as a kind of business application. An agent goes through the same Router integration and credentials as any other app, and the institution\'s Router policies and approvals still apply.'),
 ]),
]
def strip_tags(s): return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>','',s))).strip()
def qid(q): return 'q-'+re.sub('[^a-z0-9]+','-',q.lower()).strip('-')[:60]
FAQ+=globals().get('PRIVACY_FAQ',[])
faq_html=''.join(f'<h2>{g}</h2>'+''.join(f'<details class="qa" id="{qid(q)}"><summary>{html.escape(q)}</summary><p>{ans}</p></details>' for q,ans in qs) for g,qs in FAQ)
faq_page=f"""<main class="page"><div class="eyebrow">FAQ</div><h1>Questions about FinP2P, answered with sources.</h1>
<p class="lede">What the network is, what is live, how to build on it, how agents can use it, and who runs this site. Every answer links to the page or public document behind it.</p>
<nav class="toc" aria-label="Sections">{''.join(f'<a href="#{re.sub("[^a-z]+","-",g.lower()).strip("-")}">{g}</a>' for g,_ in FAQ)}</nav>
{faq_html}
<script>(function(){{function o(){{var h=decodeURIComponent(location.hash.slice(1));var e=h&&document.getElementById(h);if(e&&e.tagName==='DETAILS'){{e.open=true;e.scrollIntoView()}}}}o();addEventListener('hashchange',o)}})();</script>
<p style="margin-top:28px">Not answered here? <a href="/developers/">Developer guide</a> · <a href="/agents/">For AI agents</a> · <a href="mailto:alon@dgb.vc">alon@dgb.vc</a></p></main>"""
faq_page=re.sub(r'<h2>([^<]+)</h2>',lambda m:f'<h2 id="{re.sub("[^a-z]+","-",m.group(1).lower()).strip("-")}">{m.group(1)}</h2>',faq_page)
write('/faq/',chrome('/faq/','FinP2P FAQ','Frequently asked questions about Ownera\'s FinP2P network: what it is, what is live, how to build and get listed, how AI agents can use it, and who runs finp2p.info.',faq_page,
    extra_ld=[{"@type":"FAQPage","@id":SITE+"/faq/#faq","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":strip_tags(ans)}} for _,qs in FAQ for q,ans in qs]}]))
DEV_TEXT={'/developers/':dev,'/agents/':agents,'/faq/':faq_page}   # for llms-full.txt
