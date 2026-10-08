#!/bin/bash
# usage: f.sh URL [grep-pattern]  -> prints text
url="$1"; out=/tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/quality/pages/$(echo "$url" | md5sum | cut -c1-12).html
curl -sL --max-time 20 -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36" -o "$out" -w "HTTP %{http_code} %{url_effective}\n" "$url"
python3 -I -c '
import sys,re,html
t=open(sys.argv[1],errors="ignore").read()
t=re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>"," ",t)
t=re.sub(r"<[^>]+>"," ",t); t=html.unescape(t); t=re.sub(r"\s+"," ",t)
p=sys.argv[2] if len(sys.argv)>2 else ""
if p:
  for m in re.finditer(p,t,re.I): print("..."+t[max(0,m.start()-200):m.end()+200]+"...")
else: print(t[:3000])
' "$out" "$2"
