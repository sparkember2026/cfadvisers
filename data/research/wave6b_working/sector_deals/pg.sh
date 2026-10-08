#!/bin/sh
# usage: pg.sh URL [maxchars]
curl -sL --max-time 20 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" "$1" | python3 -I -c "
import sys,re,html
t=sys.stdin.read()
links=sorted(set(re.findall(r'href=\"(https?://[^\"]+|/[^\"]*)\"',t)))
t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
b=html.unescape(re.sub(r'<[^>]+>',' ',t)); b=re.sub(r'\s+',' ',b)
print(b[:int(sys.argv[1])])
print('LINKS:',' '.join(l for l in links if not re.search(r'\.(css|js|png|jpg|svg|woff)',l))[:1500])
" ${2:-2500}
