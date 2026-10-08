import json,re,html,subprocess,sys,os,hashlib
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin,urlparse
OUT="/tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/quality/crawl"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
def get(u):
    try:
        r=subprocess.run(["curl","-sL","--max-time","20","-A",UA,"-w","\n__EFF__%{url_effective}",u],capture_output=True,timeout=30)
        t=r.stdout.decode("utf-8","ignore"); i=t.rfind("\n__EFF__"); return t[:i],t[i+8:]
    except Exception: return "",u
def text(h):
    h=re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>"," ",h); h=re.sub(r"<[^>]+>"," ",h); return re.sub(r"\s+"," ",html.unescape(h))
KEY=re.compile(r"(about|deal|transaction|credential|corporate-finance|corporate_finance|m-?and-?a|mergers|who-we|clients|services|sell|exit|track|case|portfolio|experience|criteria|approach|what-we-do)",re.I)
def crawl(r):
    fn=os.path.join(OUT,r["id"]+".json")
    if os.path.exists(fn): return
    pages={}
    h,eff=get(r["website"]); pages[eff]=text(h)
    host=urlparse(eff).netloc.replace("www.","")
    links=[]
    for m in re.finditer(r'href="([^"#]+)"',h):
        u=urljoin(eff,m.group(1))
        p=urlparse(u)
        if p.netloc.replace("www.","")!=host or re.search(r"\.(pdf|jpg|png|css|js|svg|xml)$|wp-json|feed|mailto|tel:",u,re.I): continue
        if KEY.search(p.path) and u not in links and u.rstrip('/')!=eff.rstrip('/'): links.append(u)
    for s in r.get("sources",[]):
        if urlparse(s).netloc.replace("www.","")==host and s not in links: links.insert(0,s)
    for u in links[:8]:
        h2,e2=get(u); pages[e2]=text(h2)
    json.dump(pages,open(fn,"w"))
R=[json.loads(l) for l in open("/home/user/cfadvisers/data/advisers.jsonl")]
R=[r for r in R if r.get("deal_size_basis")=="estimate"]
print(len(R))
with ThreadPoolExecutor(24) as ex: list(ex.map(crawl,R))
print("done")
