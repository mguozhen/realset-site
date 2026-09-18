#!/usr/bin/env python3
"""Single source of truth: head/nav/footer/contact form live here; pages are content dicts in src/pages.py.
Run: python3 build.py  ->  writes index.html + <slug>/index.html, CSS versioned by content hash."""
import hashlib, os, pathlib, sys
ROOT = pathlib.Path(__file__).parent
PUB = ROOT / "public"
sys.path.insert(0, str(ROOT / "src"))
from pages import PAGES  # noqa

SITE = "https://realset.ai"
css_hash = hashlib.sha1((PUB / "assets/site.css").read_bytes()).hexdigest()[:8]

NAV_LINKS = [("Body", "/body/"), ("Field", "/field/"), ("Judge", "/judge/"), ("Workspace", "/workspace/"), ("Samples", "/samples/"), ("Research", "/research/")]

def head(p):
    title = p["title"]; desc = p["description"]; url = SITE + p["path"]
    ld = p.get("jsonld") or ('{"@context":"https://schema.org","@type":"Organization","name":"Realset","url":"%s/","description":"Real-world data lab: expert human demonstrations, RL environments from real workflows, and expert agent evaluation for frontier AI labs and robotics companies.","address":{"@type":"PostalAddress","streetAddress":"160 E Tasman Dr, Suite 215","addressLocality":"San Jose","addressRegion":"CA","postalCode":"95134","addressCountry":"US"},"parentOrganization":{"@type":"Organization","name":"VOC AI INC"}}' % SITE)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Realset">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/og.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={css_hash}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
'''

def nav(p):
    links = "".join(f'<a href="{h}">{t}</a>' for t, h in NAV_LINKS)
    solid = "" if p.get("image_hero") else " solid"
    return f'''<header class="nav{solid}"><div class="wrap">
  <nav class="links" aria-label="Primary">{links}</nav>
  <a class="logo" href="/" aria-label="Realset home">realset<span>.</span></a>
  <div class="navr"><a class="signin" href="https://data.unifyai.us/app">Sign in</a><a class="btn sm" href="#contact">Get in touch <b>›</b></a></div>
</div></header>
'''

FORM = '''<section class="contact" id="contact"><div class="wrap">
  <div class="section-head"><h2>{form_title}</h2><p>{form_sub}</p></div>
  <form class="form" id="f" data-subject="{subject}" novalidate>
    <div class="prog"><i class="on"></i><i></i><i></i></div>
    <div class="fs on" data-step="1">
      <label for="email">What are your contact details?</label>
      <div class="row"><input id="name" name="name" placeholder="Name" required><input id="email" name="email" type="email" placeholder="Work email" required></div>
      <input id="company" name="company" placeholder="{company_ph}" required>
      <p class="hint">{hint}</p>
      <button class="btn" type="button" data-next>Next →</button>
    </div>
    <div class="fs" data-step="2">
      <label for="project">{q2}</label>
      <textarea id="project" name="project" rows="5" placeholder="{q2_ph}" required></textarea>
      <div class="row"><button class="btn sec" type="button" data-back>← Back</button><button class="btn" type="button" data-next>Next →</button></div>
    </div>
    <div class="fs" data-step="3">
      <label for="source">Where did you find us?</label>
      <select id="source" name="source" required><option value="">Select one</option><option>X</option><option>LinkedIn</option><option>Google</option><option>Benchmark</option><option>Event</option><option>Referral</option><option>Other</option></select>
      <div class="row"><button class="btn sec" type="button" data-back>← Back</button><button class="btn" type="submit">Submit →</button></div>
    </div>
    <div class="done"><h3>Thanks, you're all set.</h3><p class="mut" style="margin-top:12px">Your mail client opened with the request pre-filled. Send it and we'll reply within one business day.</p></div>
  </form>
</div></section>
'''
FORM_CLIENT = dict(form_title="Tell us what your model needs", form_sub="Three questions. We reply within one business day with a sample set and a quote.",
    subject="Realset inquiry", company_ph="Company or lab", q2="Can you tell us a bit about your project?", q2_ph="Task family, embodiment, modalities, volume, timeline",
    hint='Looking for capture or annotation work? Go to the <a href="/experts/" style="text-decoration:underline">Experts page</a> instead.')
FORM_EXPERT = dict(form_title="Apply to join the capture network", form_sub="Three questions. We reply within three business days if there is a fit.",
    subject="Demonstrator application", company_ph="City and country", q2="What do you do, and what tasks can you demonstrate?", q2_ph="Your trade or role, years of experience, tools and environments you work in",
    hint='Are you a company or lab looking for data? Use the <a href="/#contact" style="text-decoration:underline">client form</a> instead.')

FOOTER = '''<footer><div class="wrap">
  <div class="fcols">
    <div><div class="fbrand">realset<span>.</span></div><p class="mut" style="font-size:14px;margin-top:8px">Real-world data for frontier models and embodied agents.</p></div>
    <div><h5>Product</h5><a href="/body/">Body</a><a href="/field/">Field</a><a href="/judge/">Judge</a><a href="/workspace/">Workspace</a><a href="/samples/">Samples</a><a href="/research/">Research</a><a href="https://data.unifyai.us/app">Sign in ↗</a></div>
    <div><h5>Company</h5><a href="/experts/">Experts</a><a href="#contact">Contact</a><a href="/terms/">Terms of Service</a><a href="/privacy/">Privacy Policy</a></div>
    <div><h5>Reach us</h5><a href="mailto:hello@realset.ai">hello@realset.ai</a><span class="mut">160 E Tasman Dr, Suite 215<br>San Jose, CA 95134</span></div>
  </div>
  <div class="trust"><span class="tlabel">Trusted &amp; verified by</span>
    <a class="badge" href="https://www.cert-assure.com/serchresult.php?type=Management+System+Certification&amp;certificate=USA-SOC2-220513" target="_blank" rel="noopener noreferrer nofollow">SOC 2 Type II</a>
    <a class="badge" href="https://www.cert-assure.com/serchresult.php?type=Management+System+Certification&amp;certificate=USA-I-270513" target="_blank" rel="noopener noreferrer nofollow">ISO 27001</a>
    <span class="badge">GDPR compliant</span>
    <a class="badge" href="https://www.vanta.com/integrations?built-by=Partner" target="_blank" rel="noopener noreferrer nofollow">Vanta monitored</a>
    <span class="badge">De-identified at capture</span>
    <span class="badge">US-hosted delivery</span>
  </div>
  <div class="fbottom"><div>© 2026 realset.ai · VOC AI INC, San Jose, CA. All rights reserved. <a href="/terms/">Terms</a> · <a href="/privacy/">Privacy</a></div><div class="fmark">realset<span>.</span></div></div>
</div></footer>
<script src="/assets/form.js?v=''' + css_hash + '''"></script>
</body>
</html>
'''

def build():
    for p in PAGES:
        form = FORM.format(**(FORM_EXPERT if p.get("expert_form") else FORM_CLIENT))
        html = head(p) + nav(p) + p["body"] + form + FOOTER
        out = PUB / ("index.html" if p["path"] == "/" else p["path"].strip("/") + "/index.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
        print("wrote", out.relative_to(PUB), len(html))

if __name__ == "__main__":
    build()
