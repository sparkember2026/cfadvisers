import json,re,os,glob
D="/tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/quality/crawl"
M=r"£\s?\d[\d.,]*\s?(?:m\b|mn\b|million|bn|billion|k\b)"
CTX=re.compile(r"(enterprise value|deal value|deal size|transaction value|transactions? (?:of|from|between|ranging|valued)|deals? (?:of|from|between|ranging|valued|up to|typically|worth)|EBITDA|turnover|revenue|valued|values? (?:of|from|between|ranging)|typically|range)",re.I)
R={json.loads(l)["id"]:json.loads(l) for l in open("/home/user/cfadvisers/data/advisers.jsonl")}
out={}
for fn in glob.glob(D+"/*.json"):
    id=os.path.basename(fn)[:-5]; pages=json.load(open(fn)); hits=[]
    for u,t in pages.items():
        for m in re.finditer(M+r".{0,40}?(?:to|-|–|and|up to)\s?"+M+"|"+M,t,re.I):
            s=t[max(0,m.start()-160):m.end()+120]
            if CTX.search(s) and not re.search(r"(fund size|raised a|£\s?\d[\d.,]*\s?(?:bn|billion) (?:of|in) (?:assets|AUM))",s,re.I):
                hits.append((u,s))
    seen=set(); h2=[]
    for u,s in hits:
        k=s[150:200]
        if k in seen: continue
        seen.add(k); h2.append((u,s))
    if h2: out[id]=h2
json.dump(out,open(D+"/../hits.json","w"),indent=0)
print(len(out))
