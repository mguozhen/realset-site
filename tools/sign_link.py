#!/usr/bin/env python3
"""Make an expiring private link. Usage: python3 tools/sign_link.py <slug> [days=7]  (reads PRIVATE_LINK_SECRET from ~/.secrets/realset-links.env)"""
import hmac, hashlib, os, sys, time, re
slug = sys.argv[1]; days = float(sys.argv[2]) if len(sys.argv) > 2 else 7
sec = [l.split('=',1)[1].strip() for l in open(os.path.expanduser('~/.secrets/realset-links.env')) if l.startswith('PRIVATE_LINK_SECRET=')][0]
e = int(time.time() + days * 86400); t = hmac.new(sec.encode(), f"{slug}.{e}".encode(), hashlib.sha256).hexdigest()[:32]
print(f"https://realset.ai/api/s?p={slug}&e={e}&t={t}   (expires {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(e))})")
