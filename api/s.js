// Expiring, signed private sample links.  GET /api/s?p=<slug>&e=<unix_exp>&t=<hmac>
// Page HTML lives in private-pages/<slug>.html (never served statically). Link is valid until `e`; after that: 410.
// Sign with: node -e "const c=require('crypto');const p='meta-coding-sessions',e=Math.floor(Date.now()/1e3)+7*86400;console.log(`/api/s?p=${p}&e=${e}&t=${c.createHmac('sha256',process.env.PRIVATE_LINK_SECRET).update(p+'.'+e).digest('hex').slice(0,32)}`)"
const crypto = require('crypto'); const fs = require('fs'); const path = require('path');
module.exports = (req, res) => {
  const { p = '', e = '', t = '' } = req.query || {};
  const secret = process.env.PRIVATE_LINK_SECRET;
  res.setHeader('X-Robots-Tag', 'noindex, nofollow, noarchive'); res.setHeader('Cache-Control', 'private, no-store'); res.setHeader('Referrer-Policy', 'no-referrer');
  if (!secret || !/^[a-z0-9-]{3,64}$/.test(p) || !/^\d{10}$/.test(e) || !/^[0-9a-f]{32}$/.test(t)) return res.status(404).send('Not found');
  const want = crypto.createHmac('sha256', secret).update(p + '.' + e).digest('hex').slice(0, 32);
  if (t.length !== want.length || !crypto.timingSafeEqual(Buffer.from(t), Buffer.from(want))) return res.status(404).send('Not found');
  if (Math.floor(Date.now() / 1000) > Number(e)) return res.status(410).send('This sample link has expired. Ask your Realset contact for a new one.');
  const f = path.join(process.cwd(), 'private-pages', p + '.html');
  if (!fs.existsSync(f)) return res.status(404).send('Not found');
  res.setHeader('Content-Type', 'text/html; charset=utf-8'); res.status(200).send(fs.readFileSync(f, 'utf8'));
};
