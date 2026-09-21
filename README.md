# finp2p.info

Independent, sourced reference site for Ownera's FinP2P network: every SuperApp on the store, the
banks, market infrastructures and partners attached to each, how a transaction moves, and a public
source for every claim. Live at https://finp2p.info.

Maintained by [Alon Goren](https://www.alongoren.com) and the [Draper Goren Blockchain](https://dgb.vc)
venture studio. Alon is on the board of Ownera and a fund he manages is an Ownera investor; Ownera does
not operate, review or endorse this site. Full disclosure on [/about/](https://finp2p.info/about/).

## How it is built

Static HTML from a stdlib-only Python build. No framework, no npm.

- `build.py` writes `dist/` from `src/` (the explainer and map page bodies) and `data/`.
- `data/graph.json` is the model: apps, derived app-to-app edges with reasons, institutions with
  public references, and the source list. `data/layers.json` holds the chains, standards, cash rails,
  custody, platforms and industry bodies shown on the Network page. `apps.json`, `types.json` and
  `categories.json` are raw snapshots of the store's public API (`https://superapps.ownera.io/api/…`).
- `src/map.body.html` is the interactive D3 map (value chain, network and institution views).
- `src/og/*.png` are the per-page share images, regenerated with `python3 tools/make-og.py` (needs
  Chrome, run locally after a headline or data change) and committed, so the deploy build stays pure Python.
- `api/contact.js` relays the Build-with-us form to DGB's lead endpoint (Vercel function).
- Anything with no public source lives in `data/private.json`, which is gitignored and never shipped.
  `build.py` merges it locally when present, keeps it out of every page, and asserts that
  `data/graph.json` contains no unsourced records.
- Pages: `/`, `/how-it-works/`, `/network/`, `/map/`, `/apps/`, `/institutions/`, `/sources/`,
  `/build/`, `/about/`, plus `robots.txt`, `sitemap.xml`, `llms.txt` and `data/graph.json`.

Run locally:

```
python3 build.py
cd dist && python3 -m http.server 4190   # http://localhost:4190/
```

## Deploy

Vercel project `finp2p-info` serves finp2p.info (`vercel.json` sets the build command and output
directory). DNS: GoDaddy, `A @ 76.76.21.21` and `CNAME www cname.vercel-dns.com`; www redirects to
the apex. The repository is connected to Vercel, so every push to `main` deploys on its own.

## Corrections and contributions

If you represent an institution or app on the site and something is wrong or out of date, open an
issue or a pull request against `data/graph.json` with the correction and a public source, or email
alon@dgb.vc. Institutions without a public source are not shown. Corrections ship the same week.

## Licence

The data (`data/graph.json`, also published at https://finp2p.info/data/graph.json) is CC BY 4.0:
reuse it anywhere with attribution to finp2p.info. Site copy and code are (c) Draper Goren Blockchain.

Ownera, FinP2P and SuperApps are trademarks of XCap Ecosystem Ltd; all other names belong to their owners.
