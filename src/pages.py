import pathlib
HOME_BODY = (pathlib.Path(__file__).parent / "home_body.html").read_text()

def phero(k, h1, sub, cta2=None):
    c2 = f'<a class="btn sec" href="{cta2[1]}">{cta2[0]}</a>' if cta2 else ''
    return f'''<section class="phero"><div class="wrap"><span class="k">{k}</span><h1>{h1}</h1><p>{sub}</p><div class="cta"><a class="btn" href="#contact">Get in touch →</a>{c2}</div></div></section>
'''
def section(title, sub, inner, id=""):
    i = f' id="{id}"' if id else ''
    return f'<section class="section"{i}><div class="wrap"><div class="section-head"><h2>{title}</h2><p>{sub}</p></div>{inner}</div></section>\n'
def cards(items, cls="grid3"):
    return f'<div class="{cls}">' + "".join(f'<div class="card" style="min-height:0"><span class="k">{k}</span><h3>{h}</h3><p>{p}</p></div>' for k, h, p in items) + '</div>'
def steps(items):
    return '<div class="steps">' + "".join(f'<div class="step"><div class="n">0{i+1}</div><h4>{h}</h4><p>{p}</p></div>' for i, (h, p) in enumerate(items)) + '</div>'
def spec(rows):
    return '<div class="spec"><table>' + "".join(f'<tr><th>{a}</th><td>{b}</td></tr>' for a, b in rows) + '</table></div>'
def ul(items):
    return '<ul class="list">' + "".join(f'<li><b>{h}</b>{p}</li>' for h, p in items) + '</ul>'

BODY = phero("Realset Body", "Structured real-world data for physical policy models",
  "Expert human demonstrations captured in real homes, kitchens, warehouses and assembly lines, then structured into training data for VLA and manipulation research.", ("See the benchmark", "/research/")) + \
section("Our approach", "Three ways to get physical-world data, run as one pipeline with QC on every episode.", cards([
  ("Capture network", "Egocentric demonstrations at work", "Skilled workers wear head-mounted rigs while doing their actual job. Synchronized stereo video, IMU and audio, task-labeled at the shift level and segmented after."),
  ("Studio", "Teleoperation in controlled environments", "Bimanual teleop stations in a controlled studio with kitchen, shelf and bench scenes. Action logs, multi-camera video and depth per episode, with retake rules agreed up front."),
  ("Structuring", "Annotation built for policy learning", "Temporal segmentation, hand-object interaction, 2D/3D tracking and step-by-step natural language labels. Delivered in LeRobot, RLDS or your schema."),
])) + \
section("Use cases", "What robotics teams buy from us today.", ul([
  ("Household manipulation", "Folding, loading, sorting and wiping tasks across many real kitchens and laundry rooms, not one lab apartment."),
  ("Light assembly and packaging", "Two-handed assembly, kitting and boxing from production lines, with the workers who do it daily."),
  ("Warehouse picking and placing", "Shelf-to-tote picking with varied SKUs, lighting and clutter, captured at operating speed."),
  ("Evaluation episodes", "Held-out real-world task sets scored by trial for policy comparison, feeding our public benchmark."),
])) + \
section("What you get", "Every delivery ships with the same spec sheet, so your training pipeline never changes between batches.", spec([
  ("Modalities", "Stereo RGB, IMU, audio; teleop adds joint states, gripper commands and depth"),
  ("Frame rate", "30 fps video, 50 Hz action logs on teleop episodes"),
  ("Labels", "Task, sub-task segments, language instructions, success flag per episode"),
  ("Formats", "LeRobot v2, RLDS, or a schema you provide"),
  ("QC", "Two-pass review, resample rate published per batch on a live dashboard"),
  ("Privacy", "Faces, plates and text de-identified before the data leaves the capture site"),
  ("Hosting", "Delivered to a US-region bucket of your choice; nothing stored elsewhere after delivery"),
])) + \
section("How a project runs", "From scoping call to first batch in about three weeks.", steps([
  ("Scope", "Task family, embodiment, environments, volume and the success criteria your model is judged on."),
  ("Pilot batch", "A small paid batch in one environment so you can validate format and quality before scaling."),
  ("Scale", "Capture network and studio run in parallel; pipeline dashboard shows velocity, QC pass rate and cost per episode."),
  ("Iterate", "Your eval results steer the next batch toward the failure modes that matter."),
]))

FIELD = phero("Realset Field", "RL environments built from real workflows",
  "Environments that mirror how work actually happens, with domain experts generating trajectories, preferences and verifiable rewards inside them. Agentic models learn the job, not the benchmark.") + \
section("Our approach", "Real workflows from operating businesses, turned into environments a model can act in.", cards([
  ("Environments", "Workflow replicas, not toy tasks", "E-commerce operations, customer support, logistics dispatch and manufacturing SOPs rebuilt as interactive environments with the real tools, data shapes and edge cases."),
  ("Expert data", "Trajectories from people who do the work", "Operators, support leads and planners generate demonstrations, preference pairs and rubrics inside the environment. Bilingual English and Chinese expert pools."),
  ("Rewards", "Verifiable outcomes", "Where the business has a ground-truth outcome, such as a resolved ticket or a correct listing, the environment scores it. Where it does not, expert rubrics do."),
])) + \
section("Domains", "Starting with the workflows we have run ourselves for years.", ul([
  ("E-commerce operations", "Listing edits, ad bid changes, inventory and returns across marketplace seller tools."),
  ("Customer support", "Multi-turn resolution with policy lookups, escalation decisions and refunds."),
  ("Logistics and dispatch", "Order routing, exception handling and carrier communication."),
  ("Manufacturing SOPs", "Procedure following, checklists and deviation reporting on the shop floor."),
  ("Finance", "Variance analysis, financial interpretation and evidence-backed business questions, answered by analysts with their working shown."),
  ("Business operations", "Exception handling, supplier decisions and operational tradeoffs, captured against your team's rubric."),
])) + \
section("Produced in the Realset Workspace", "Expert contributions, screen-recorded provenance, independent review and payout ledger all run in one workspace.", '''<div class="cta" style="justify-content:flex-start"><a class="btn sec" href="/workspace/">See the workspace →</a></div>''') + \
section("What you get", "", spec([
  ("Deliverables", "Environment code and fixtures, expert trajectories, preference pairs, rubrics, reward functions"),
  ("Volume", "Pilot from 500 trajectories; production runs in the tens of thousands"),
  ("Formats", "OpenAI-style message logs, tool-call traces, or your schema"),
  ("Experts", "Vetted by task interview; every trajectory tagged with the expert's role and tenure"),
  ("Hosting", "Environments run in your cloud or ours; data delivered to a US-region bucket"),
])) + \
section("How a project runs", "", steps([
  ("Scope", "Pick the workflow, the tools the agent will touch and what counts as done."),
  ("Build", "We replicate the workflow as an environment and validate it with the experts who will work in it."),
  ("Generate", "Experts produce trajectories and preferences; verifiable rewards are wired where they exist."),
  ("Iterate", "Your model's rollouts are reviewed by the same experts, feeding the next batch."),
]))

JUDGE = phero("Realset Judge", "Expert evaluation for agents in production",
  "Evaluation design, failure diagnosis and continuous monitoring by people who do the job your agent is replacing. Human review beyond LLM-as-judge.") + \
section("How it works", "Judge turns agent reliability into a measured, repeatable process.", steps([
  ("Evaluation design", "Success criteria, rubrics and scoring defined with domain experts against your real workflow."),
  ("Failure diagnosis", "Experts review agent outputs and tag where, why and how the agent fails, by failure mode."),
  ("Targeted training data", "We produce fix-data for the highest-priority failure modes, in the format your training team uses."),
  ("Monitor", "Re-score as models, prompts, tools and rules change; a dashboard tracks drift over time."),
])) + \
section("What Judge covers", "", ul([
  ("Customer-facing agents", "Support, sales and onboarding agents where tone, policy and escalation judgment matter."),
  ("Computer-use agents", "Agents operating real software; scored on task completion and on the side effects they cause."),
  ("Embodied policies", "Real-world task trials scored by success rate, feeding our public benchmarks."),
  ("Safety and over-refusal", "Competence under constraint: does the agent help within the rules without refusing what it should do."),
])) + \
section("Impact", "", cards([
  ("Time to production", "Find failure modes earlier", "Shorter iteration cycles because failures are named and counted, not anecdotal."),
  ("Visibility", "Know why the agent fails", "Every score comes with an expert's explanation you can hand to the team fixing it."),
  ("Trust", "Consistent behavior in critical flows", "Monitoring catches regressions when a model or prompt changes."),
]))

RESEARCH = phero("Research", "Benchmarks on real-world tasks",
  "We publish open benchmarks so the field can measure the thing that matters: whether a policy or agent works outside the lab. Results are posted as they are produced, never before.") + \
section("Featured benchmarks", "Status is shown honestly. A benchmark gets a leaderboard only after trials are run.", '''<div class="bench">
    <div class="card"><span class="status"><i></i>In progress · results Q4 2026</span><h3>Realset Household Manipulation Bench</h3><p>Open-source VLA policies evaluated on household tasks captured in real kitchens and laundry rooms, not simulation.</p>
      <table class="tbl"><tr><td>Tasks</td><td>Folding, loading, sorting, wiping</td></tr><tr><td>Policies under test</td><td>π0, OpenVLA, GR00T, Octo</td></tr><tr><td>Metric</td><td>Success rate, 3 trials per task</td></tr></table><a class="more" href="#contact">Request early access →</a></div>
    <div class="card"><span class="status"><i></i>Planned</span><h3>Light Assembly Bench</h3><p>Bimanual assembly and packaging tasks from real production lines, scored by the line workers who trained on them.</p><a class="more" href="#contact">Join as a partner lab →</a></div>
    <div class="card"><span class="status"><i></i>Planned</span><h3>Commerce Ops Agent Bench</h3><p>Computer-use agents on real e-commerce seller operations: listing edits, ad bids, returns and review handling.</p><a class="more" href="#contact">Join as a partner lab →</a></div>
  </div>''') + \
section("Research notes", "Short write-ups from the capture floor and the eval bench. First notes publish with the first benchmark results.", '''<div>
    <div class="paper"><time>Q4 2026</time><h4>What 200 hours of egocentric kitchen video taught us about task segmentation</h4><span class="status"><i></i>Drafting</span></div>
    <div class="paper"><time>Q4 2026</time><h4>De-identification at capture: what it costs and what it does to policy performance</h4><span class="status"><i></i>Drafting</span></div>
    <div class="paper"><time>Q1 2027</time><h4>Sim-to-real gap on household tasks: benchmark results, first release</h4><span class="status"><i></i>Planned</span></div>
  </div>''')

EXPERTS = phero("Experts", "Join the capture network",
  "We pay skilled people to do their real work while wearing a camera, to teleoperate robots in our studio, and to review AI agents in their field. No annotation-farm work.") + \
section("Open roles", "Paid per shift or per task. Location and language requirements vary by project.", cards([
  ("Demonstrator", "Do your job, on camera", "Cooks, line workers, warehouse pickers, technicians. Wear a head-mounted rig during normal shifts. Faces and personal details are removed before anything leaves the site."),
  ("Teleoperator", "Drive robots in the studio", "Operate bimanual teleop stations through household and bench tasks. Training provided; hand-eye coordination and patience required."),
  ("Domain reviewer", "Judge AI agents in your field", "Support leads, e-commerce operators, planners. Score agent outputs against rubrics you help write. Remote, part-time."),
])) + \
section("Work in your language, paid your way", "The workspace is built for experts outside our head office.", ul([
  ("Six languages", "English · 简体中文 · 日本語 · 한국어 · Español · العربية, with full right-to-left layout for Arabic."),
  ("Paid the way you want", "USDT · USDC · BTC · IBAN · PayPal · Wise · Alipay. Every approved task accrues to your ledger; you can see what is owed and what has been paid."),
  ("Your work, on record", "Optional screen recording stored with a SHA-256 digest, so reviewers judge what you actually did and disputes are settled by evidence."),
  ("A quality score you can see", "Independent reviewers score against a rubric you can read before you start."),
])) + \
section("How it works", "", steps([
  ("Apply", "Three questions below. Tell us what you do and where you are."),
  ("Task interview", "A short practical screen for the role, run by our AI recruiter and reviewed by a person."),
  ("Onboard", "Consent, equipment and a paid trial shift or task set."),
  ("Work", "Scheduled shifts or task batches, paid on delivery, with a quality score you can see."),
]))


APP = "https://data.unifyai.us/app"
WORKSPACE = phero("Realset Workspace", "Expert judgment, captured as training data",
  "The workspace where domain experts answer real tasks, record how they got there, pass independent review, and get paid. Every approved record exports as JSONL with provenance you can verify.", ("Open workspace ↗", "https://data.unifyai.us/app")) + \
section("The anatomy of a good record", "Illustrative example from finance. Each record carries the task, the expert's reasoning, and a reviewer's decision.", '''<div class="grid3">
    <div class="card" style="min-height:0"><span class="k">01 / Real-world task</span><h3>Revenue grew. Did performance improve?</h3><p>A fictional distributor reports 20% revenue growth while gross margin falls from 30% to 23%.</p><p style="margin-top:8px"><span class="badge">Financial analysis</span> <span class="badge">Evidence required</span></p></div>
    <div class="card" style="min-height:0"><span class="k">02 / Expert contribution</span><h3>"Growth alone is not enough."</h3><p>"Gross profit fell from 30 to 27.6 on a revenue index of 100 → 120. Investigate pricing, product mix and input costs before attributing the change." Answer, supporting evidence, and a screen recording of the work.</p></div>
    <div class="card" style="min-height:0"><span class="k">03 / Independent review</span><h3>Correctness · Evidence · Completeness</h3><p>A separate reviewer checks the answer against the rubric, watches the recording when present, and records a decision. Only approved records are exported.</p><p style="margin-top:8px"><span class="badge">Quality gate</span></p></div>
  </div>''') + \
section("The method", "From domain knowledge to dependable datasets. Start with a real task, keep the expertise, the evidence and the working session together.", steps([
  ("Define the work", "Set the question, source material, language and region, reward, intended data use, and an explicit evaluation rubric."),
  ("Capture expertise", "Experts contribute an answer, supporting evidence, and, when the task calls for it, a screen recording of how they got there."),
  ("Review independently", "A separate reviewer checks quality against the rubric, watches the recording when present, and records a decision."),
  ("Deliver and settle", "Export approved records as JSONL with provenance and review metadata, while approved work accrues to the contributor's payout ledger."),
])) + \
section("Built around the work", "For knowledge that doesn't fit a checkbox. First workflows cover finance and business operations; use synthetic examples to explore before introducing authorized enterprise data.", ul([
  ("Finance", "Make the numbers explain themselves. Variance analysis, financial interpretation, evidence-backed business questions. Variance explanations / source checks / assumptions."),
  ("Business operations", "Capture the judgment behind the process. Exception handling, supplier decisions and operational tradeoffs against your team's rubric. Process exceptions / decision criteria / escalations."),
  ("Customer support and e-commerce", "The workflows we run ourselves: ticket resolution, escalation calls, listing and ad decisions, scored by the people who do them."),
  ("Embodied task review", "Reviewers score real-world robot trials from video, feeding the Body line and our public benchmarks."),
])) + \
section("Global by default", "Expert networks are global. Three things decide whether an expert outside your head office can actually work with you: language, payment, and trust without a meeting.", cards([
  ("文", "Localised, not just translated", "Six interface languages including full right-to-left layout for Arabic. Every task carries an ISO 639-1 language and ISO 3166-1 region, so a dataset's coverage is a fact you can query. English · 简体中文 · 日本語 · 한국어 · Español · العربية"),
  ("₮", "Paid the way they want to be paid", "USDT on TRON, Ethereum or BNB Smart Chain, USDC, BTC, IBAN and local bank transfer, PayPal, Wise, Alipay. Destinations are format-checked before they are stored, and every approved task accrues to a ledger with its own reconciliation export."),
  ("⏺", "Provenance you can watch", "Experts can record their screen while they work, directly in the browser. The recording is stored with a SHA-256 digest, shown to the reviewer alongside the answer, and referenced by hash in the export. WebM · SHA-256 · Reviewer playback"),
])) + \
section("What the workspace covers today", "A focused workspace. A complete data workflow.", spec([
  ("In scope", "Task creation, expert contributions with optional screen recording, independent review, approved JSONL export, payout ledger"),
  ("Isolation", "Each workspace is separate: its tasks, recordings and ledger are visible only to the people invited into it"),
  ("Ledger", "Records what is owed and what an operator has settled; it does not move money, hold funds, or connect to an exchange"),
  ("Not included", "Automated model evaluation, fine-tuning, enterprise SSO"),
  ("Access", "Sign in with your operator-provided account, or ask us for a workspace"),
  ("Built on", "Label Studio Community Edition (Apache-2.0) for annotation storage"),
])) + \
'''<section class="section"><div class="wrap"><div class="cta"><a class="btn" href="https://data.unifyai.us/app">Open workspace ↗</a><a class="btn sec" href="#contact">Ask for a workspace</a></div></div></section>
'''


import json as _json
from samples import PACKS, REQUEST_ONLY, MIRRORS, DRIVE_ROOT, BUCKET_PACKS
SCEN = _json.load(open(pathlib.Path(__file__).parent / "scenarios.json"))
_nscen = sum(len(v) for m in SCEN.values() for v in m.values())

def _pack_card(pk):
    return f'''<a class="card" href="/samples/{pk["slug"]}/"><span class="k">{pk["k"]}</span><h3>{pk["name"]}</h3><p>{pk["summary"]}</p><span class="status"><i></i>{pk["n"]} examples · preview online</span><span class="more">Open sample →</span></a>'''
def _bucket_card(pk):
    return f'''<a class="card" href="/samples/{pk["slug"]}/"><span class="k">{pk["k"]}</span><h3>{pk["name"]}</h3><p>{pk["summary"]}</p><span class="status"><i></i>{pk["n"]} · video preview online · bucket access on request</span><span class="more">Open sample →</span></a>'''
def _bucket_page(pk):
    import json as _j
    d=_j.load(open(pathlib.Path(__file__).parent / pk["json"]))
    vids="".join(f'<div><video controls preload="metadata" playsinline style="width:100%;border-radius:8px;border:1px solid var(--line);background:#000" src="/media/{pk["slug"]}/{f}"></video><p class="mut" style="font-size:14px;margin-top:8px">{c}</p></div>' for f,c in pk["previews"])
    feat="".join(f"<tr><th>{a}</th><td><span class=\"mono\" style=\"color:var(--mut)\">{b}</span><br>{c}</td></tr>" for a,b,c in pk["features"])
    fams=", ".join(f"{k} ({v})" for k,v in list(d["families"].items())[:8])
    top="".join(f"<li><b>{t}</b>{n} episodes</li>" for t,n in list(d["episode_counts"].items())[:8])
    alltasks="".join(f"<li>{t}</li>" for t in d["tasks"])
    guide="".join(f"<li>{g}</li>" for g in pk["guide"])
    return phero(pk["k"], pk["name"], pk["summary"], ("All samples", "/samples/")) + \
    section("Preview", "Visualization renders: the delivered 3D hand data projected back onto the ego video. If the overlay tracks the hands, the data is right.", f'<div class="grid2">{vids}</div>') + \
    section("At a glance", "", spec(pk["stats"])) + \
    section("Tasks", f"{len(d['tasks'])} task strings across the 390 episodes. Verb families: {fams}.", f'<ul class="list">{top}</ul><details style="margin-top:var(--sp-sm)"><summary class="mut" style="cursor:pointer">Show all {len(d["tasks"])} task strings</summary><ul class="list" style="grid-template-columns:1fr 1fr;margin-top:var(--sp-sm);font-size:14px">{alltasks}</ul></details>') + \
    section("Features", "Per-frame columns in data/*.parquet. Lengths in metres, angles in radians, matrices row-major. Full semantics and coordinate frames are in ACTION_DATA_DESCRIPTION.md inside the dataset.", f'<div class="spec"><table>{feat}</table></div>') + \
    section("Access", "Delivered from an S3-compatible bucket. Credentials are issued per client, sent separately, and expire; one command pulls everything and resumes if interrupted.", f'<pre class="code">{pk["access_cmd"]}</pre><ul class="list" style="grid-template-columns:1fr;margin-top:var(--sp-sm)">{guide}</ul><div class="cta" style="justify-content:flex-start;margin-top:var(--sp-md)"><a class="btn" href="#contact">Request bucket credentials →</a><a class="btn sec" href="/samples/ego-pose-retargeting/">See the processed-ego sample pack</a></div>') + \
    section("Next step", "This is a 5-hour sample. Formal batches follow the same LeRobot layout at the task mix, environment and volume you specify.", '<div class="cta" style="justify-content:flex-start"><a class="btn" href="#contact">Request a scoped batch →</a></div>')
def _req_card(r):
    return f'''<div class="card" style="min-height:0"><span class="k">{r["k"]}</span><h3>{r["name"]}</h3><p>{r["summary"]}</p><span class="status"><i></i>{r["status"]}</span><a class="more" href="#contact">Request sample →</a></div>'''

SAMPLES_INDEX = phero("Samples", "See the data before you talk to anyone",
  "Every dataset family has a sample you can open right now. Judge format and quality first; delivery terms come after you have seen it.", ("Scenario list", "/samples/scenarios/")) + \
section("Embodied data · Body", "Ten capture modalities with hosted previews, plus a five-hour LeRobot-format sample. Every pack is delivered from Realset's own bucket with expiring credentials. Formal batches are produced to your spec after a sample review.", '<div class="grid3">' + "".join(_bucket_card(pk) for pk in BUCKET_PACKS) + "".join(_pack_card(pk) for pk in PACKS) + '</div>') + \
section("Agent, coding and expert data · Field / Judge", "Samples for these lines are sent under a click-through sample agreement. Ask and we reply within one business day.", '<div class="grid3">' + "".join(_req_card(r) for r in REQUEST_ONLY) + '</div>') + \
section("Scenario coverage", f"{_nscen} real-world sub-scenarios across manufacturing, logistics, laundry and care services, and commercial services, where capture is set up or can be set up.", '''<div class="cta" style="justify-content:flex-start"><a class="btn sec" href="/samples/scenarios/">Browse all scenarios →</a></div>''')

def _pack_page(pk):
    import glob as _g, os as _os
    media=sorted(_g.glob(str(pathlib.Path(__file__).parents[1] / "public" / "media" / pk["slug"] / "*")))
    vids=[_os.path.basename(m) for m in media if m.endswith(".mp4")]; imgs=[_os.path.basename(m) for m in media if m.endswith((".jpg",".png"))]
    prev="".join(f'<div><video controls muted loop preload="metadata" playsinline style="width:100%;border-radius:8px;border:1px solid var(--line);background:#000" src="/media/{pk["slug"]}/{v}"></video></div>' for v in vids)
    prev+="".join(f'<div><img src="/media/{pk["slug"]}/{i}" alt="{pk["name"]} preview" loading="lazy" style="width:100%;border-radius:8px;border:1px solid var(--line)"></div>' for i in imgs)
    contents = "".join(f"<li>{c}</li>" for c in pk["contents"])
    access = '<pre class="code">aws s3 sync s3://&lt;bucket&gt;/&lt;prefix&gt;/ ./sample/ --endpoint-url &lt;endpoint&gt; --profile realset</pre><div class="cta" style="justify-content:flex-start;margin-top:var(--sp-md)"><a class="btn" href="#contact">Request sample credentials →</a><a class="btn sec" href="/samples/scenarios/">Scenario list</a></div>'
    return phero(pk["k"], pk["name"], pk["summary"], ("All samples", "/samples/")) + \
    section("Preview", f"{pk['n']} examples in this sample pack. Short clips below are cut from the actual capture; the full pack is delivered from Realset's bucket with temporary credentials.", f'<div class="grid2">{prev}</div>' if prev else '<p class="mut">Preview being prepared.</p>') + \
    section("What is inside", "", f'<ul class="list" style="grid-template-columns:1fr">{contents}</ul>') + \
    section("Spec", "What a formal batch of this modality delivers.", spec(pk["spec"])) + \
    section("Access", "Delivered from an S3-compatible bucket. Credentials are issued per client, sent separately, and expire; one command pulls everything and resumes if interrupted.", access) + \
    section("Next step", "Liked what you saw? Tell us the task family, volume and format. We reply with a scoped batch and a quote; delivery terms are settled at order time.", '<div class="cta" style="justify-content:flex-start"><a class="btn" href="#contact">Request a scoped batch →</a></div>')

def _scen_page():
    out=[]
    for macro, scs in SCEN.items():
        n=sum(len(v) for v in scs.values())
        blocks="".join(f'<h3 style="margin-top:var(--sp-sm)">{sc} <span class="mut" style="font-size:14px">· {len(items)}</span></h3><ul class="list">' + "".join(f"<li><b>{a}</b>{b}</li>" for a,b in items) + "</ul>" for sc, items in scs.items())
        out.append(f'<section class="section"><div class="wrap"><div class="section-head"><h2>{macro}</h2><p>{n} sub-scenarios</p></div>{blocks}</div></section>')
    return "".join(out)

SCENARIOS = phero("Scenario coverage", f"{_nscen} real-world scenarios",
  "Workplaces where our capture network operates or can be set up: what people do there, listed as the atomic tasks a policy would need to learn. Use it to scope a batch.", ("All samples", "/samples/")) + _scen_page()

PRIVACY = phero("Privacy", "Privacy policy", "How Realset handles data from clients, demonstrators and website visitors. Last updated September 15, 2026.") + \
section("Summary", "", ul([
  ("Client data", "Project specifications and delivered datasets are stored in US-region cloud storage, encrypted at rest, and retained only for the term agreed in your contract."),
  ("Demonstrator data", "Captured video is de-identified (faces, license plates, on-screen text) before it leaves the capture site. Demonstrators sign informed consent that names the intended use and the right to withdraw future capture."),
  ("Website visitors", "This site sets no tracking cookies. The contact form opens your own mail client; we receive only what you send."),
  ("Requests", "Access, correction or deletion requests: hello@realset.ai. We respond within 30 days."),
  ("Controller", "VOC AI INC, 160 E Tasman Dr, Suite 215, San Jose, CA 95134, USA."),
  ("Certifications", "Our security program is audited to SOC 2 Type II and ISO 27001 and continuously monitored through Vanta."),
]))

TERMS = phero("Terms", "Terms of service", "Terms governing use of realset.ai and the services described on it. Last updated September 15, 2026.") + \
section("Summary", "", ul([
  ("Services", "Data capture, environment construction and evaluation services are provided under a separate master services agreement and statement of work. This website is informational."),
  ("Ownership", "Unless a statement of work says otherwise, delivered datasets are licensed to the client for model training and evaluation; de-identified derivatives may be reused by Realset."),
  ("Acceptable use", "Data may not be used to identify demonstrators or to train systems intended for surveillance or weapons."),
  ("Warranties", "Deliverables are warranted to meet the spec sheet in the statement of work; other warranties are disclaimed to the extent permitted by law."),
  ("Governing law", "State of California, USA."),
  ("Contact", "hello@realset.ai"),
]))

PAGES = [
  dict(path="/", title="Realset — Real-world data to train frontier models and embodied agents", description="Realset is a real-world data lab. We capture expert human demonstrations, build RL environments from real workflows, and evaluate AI agents with domain experts — for frontier labs and robotics companies.", image_hero=True, body=HOME_BODY),
  dict(path="/body/", title="Realset Body — Embodied data for physical policy models", description="Expert human demonstrations captured in real homes, kitchens, warehouses and assembly lines, structured into training data for VLA and manipulation research.", body=BODY),
  dict(path="/field/", title="Realset Field — RL environments built from real workflows", description="RL environments that mirror real e-commerce, support, logistics and manufacturing workflows, with domain experts generating trajectories, preferences and verifiable rewards.", body=FIELD),
  dict(path="/judge/", title="Realset Judge — Expert evaluation for AI agents in production", description="Evaluation design, failure diagnosis, targeted training data and continuous monitoring by domain experts. Human review beyond LLM-as-judge.", body=JUDGE),
  dict(path="/research/", title="Realset Research — Benchmarks on real-world tasks", description="Open benchmarks measuring whether robot policies and AI agents work outside the lab. Household manipulation, light assembly and commerce operations.", body=RESEARCH),
  dict(path="/samples/", title="Realset Samples — See the data before you talk to anyone", description="Open real samples of embodied, agent and expert data: ego-exo paired, dual-wrist ego, hand pose retargeting, UMI gripper, robot teleop in LeRobot and MCAP, 360 spatial. Judge quality first; delivery after.", body=SAMPLES_INDEX),
  dict(path="/samples/scenarios/", title="Realset — Real-world scenario coverage", description="Sub-scenarios across manufacturing, logistics, laundry and care services where Realset captures embodied data.", body=SCENARIOS),
] + [dict(path=f"/samples/{pk['slug']}/", title=f"Realset Sample — {pk['name']}", description=pk["summary"], body=_pack_page(pk)) for pk in PACKS] + [dict(path=f"/samples/{pk['slug']}/", title=f"Realset Sample — {pk['name']}", description=pk["summary"], body=_bucket_page(pk)) for pk in BUCKET_PACKS] + [
  dict(path="/workspace/", title="Realset Workspace — Expert judgment, captured as training data", description="The workspace where domain experts answer real tasks, record how they got there, pass independent review and get paid. Approved records export as JSONL with SHA-256 provenance. Six languages, crypto and fiat payouts.", body=WORKSPACE),
  dict(path="/experts/", title="Realset Experts — Join the capture network", description="Paid work for skilled demonstrators, teleoperators and domain reviewers. Do your real job on camera, drive robots in our studio, or judge AI agents in your field.", expert_form=True, body=EXPERTS),
  dict(path="/privacy/", title="Realset — Privacy policy", description="How Realset handles client data, demonstrator data and website visitor data.", body=PRIVACY),
  dict(path="/terms/", title="Realset — Terms of service", description="Terms governing use of realset.ai and the services described on it.", body=TERMS),
]
