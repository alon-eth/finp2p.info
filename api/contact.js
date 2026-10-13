// finp2p.info contact relay (Vercel function). The browser cannot post to DGB's lead endpoint
// cross-origin, so the form posts here and this forwards server-side. On any failure the page
// falls back to a mailto link, so this only ever answers ok:true or an error status.
export default async function handler(req, res) {
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'POST only' });
  let inp = req.body;
  if (typeof inp === 'string') { try { inp = JSON.parse(inp); } catch { inp = {}; } }
  if (!inp || typeof inp !== 'object') inp = {};
  const t = (v) => (typeof v === 'string' ? v.trim() : '');
  const name = t(inp.name), email = t(inp.email), org = t(inp.organization);
  const interest = t(inp.interest) || 'FinP2P: general', message = t(inp.message);
  if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return res.status(400).json({ ok: false, error: 'Name and a valid email are required.' });
  }
  if (t(inp.website)) return res.status(200).json({ ok: true }); // honeypot
  const payload = {
    type: 'contact', source: 'https://finp2p.info/build/', name, email, organization: org,
    interest: 'finp2p.info · ' + interest, message,
  };
  try {
    const ctl = new AbortController(); const timer = setTimeout(() => ctl.abort(), 15000);
    const r = await fetch('https://dgb.vc/api/lead', {
      method: 'POST', redirect: 'follow', signal: ctl.signal,
      headers: { 'Content-Type': 'application/json', 'User-Agent': 'finp2p.info relay' },
      body: JSON.stringify(payload),
    });
    clearTimeout(timer);
    if (!r.ok) return res.status(502).json({ ok: false, error: 'lead endpoint ' + r.status });
    return res.status(200).json({ ok: true });
  } catch (e) {
    return res.status(502).json({ ok: false, error: 'relay failed' });
  }
}
