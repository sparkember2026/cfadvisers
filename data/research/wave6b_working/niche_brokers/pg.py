import sys,re,subprocess,html
from urllib.parse import urljoin
url=sys.argv[1]; n=int(sys.argv[2]) if len(sys.argv)>2 else 2500
h=subprocess.run(['curl','-sL','--max-time','25','-A','Mozilla/5.0',url],capture_output=True).stdout.decode('utf8','ignore')
links=set()
for m in re.finditer(r'href=["\']([^"\'#]+)',h):
    l=urljoin(url,m.group(1))
    if re.search(r'team|people|about|contact|office|sold|deal|case|complet|linkedin|sector|who-we',l,re.I) and not re.search(r'\.(css|js|png|jpg|svg)',l): links.add(l)
emails=set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+',h)); 
t=re.sub(r'(?s)<(script|style|noscript)[^>]*>.*?</\1>',' ',h); t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t); t=re.sub(r'\s+',' ',t)
phones=set(re.findall(r'(?:\+44\s?|0)\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4}',t))
print('EMAILS',[e for e in emails if not e.endswith(('png','jpg','wixpress.com','sentry.io'))][:8]); print('PHONES',list(phones)[:5]); print('LINKS',sorted(links)[:30]); print('TEXT',t[:n])
