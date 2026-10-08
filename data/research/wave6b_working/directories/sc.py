import sys,re,subprocess,html
d=sys.argv[1]
r=subprocess.run(['curl','-sL','--max-time','15','-A','Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120','-w','\n%{http_code} %{url_effective}','http://'+d],capture_output=True).stdout.decode('utf8','ignore')
h,_,meta=r.rpartition('\n')
t=re.sub(r'(?s)<(script|style)[^>]*>.*?</\1>',' ',h); t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t).lower()
k=sum(t.count(w) for w in ['sell your business','selling your business','business sales','business transfer','businesses for sale','sell a business','business broker','m&a','corporate finance','business valuation'])
p=sum(t.count(w) for w in ['to let','lettings','residential','house','apartment'])
m=re.search(r'<title[^>]*>([^<]*)',h,re.I)
print(f"{k}\t{p}\t{d}\t{meta}\t{(m.group(1).strip() if m else '')[:80]}")
