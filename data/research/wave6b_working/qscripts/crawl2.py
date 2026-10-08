import json,re,html,subprocess,os
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin,urlparse
Q="/tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/quality"
OUT=Q+"/crawl2"; os.makedirs(OUT,exist_ok=True)
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
def get(u):
    try:
        r=subprocess.run(["curl","-sL","--max-time","20","-A",UA,"-w","\n__EFF__%{url_effective}",u],capture_output=True,timeout=30)
        t=r.stdout.decode("utf-8","ignore"); i=t.rfind("\n__EFF__"); return t[:i],t[i+8:]
    except Exception: return "",u
def text(h):
    h=re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>"," ",h); h=re.sub(r"<[^>]+>"," ",h); return re.sub(r"\s+"," ",html.unescape(h))
STRONG=re.compile(r"(deal|transaction|credential|track|case-stud|corporate-finance|mergers|m-a\b|m-and-a|sell|exit|about|who-we|criteria|clients|our-work|completed|news)",re.I)
def links(h,eff,host):
    out=[]
    for m in re.finditer(r'href="([^"#]+)"',h):
        u=urljoin(eff,m.group(1)); p=urlparse(u)
        if p.netloc.replace("www.","")!=host or re.search(r"\.(pdf|jpg|png|css|js|svg|xml|webp)$|wp-json|feed|mailto|tel:|\?",u,re.I): continue
        if STRONG.search(p.path) and u not in out: out.append(u.split('#')[0])
    return out
def crawl(id_site):
    id,site=id_site; fn=os.path.join(OUT,id+".json")
    if os.path.exists(fn): return
    old=json.load(open(Q+"/crawl/"+id+".json")); done=set(u.rstrip('/') for u in old)
    h,eff=get(site); host=urlparse(eff).netloc.replace("www.","")
    L=links(h,eff,host); pages={}
    # second level from CF/deal pages
    lvl1=[u for u in L if u.rstrip('/') not in done][:10]
    for u in lvl1:
        h2,e2=get(u); pages[e2]=text(h2)
        if re.search(r"corporate-finance|deal|transaction|mergers",u,re.I):
            for v in links(h2,e2,host):
                if v.rstrip('/') not in done and v not in pages and len(pages)<16:
                    h3,e3=get(v); pages[e3]=text(h3)
    json.dump(pages,open(fn,"w"))
R=[json.loads(l) for l in open("/home/user/cfadvisers/data/advisers.jsonl")]
todo=[(r["id"],r["website"]) for r in R if r.get("deal_size_basis")=="estimate" and r["firm_type"] not in ("big4",)]
with ThreadPoolExecutor(28) as ex: list(ex.map(crawl,todo))
print("done",len(todo))
