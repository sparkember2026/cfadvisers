import json,re,html,subprocess,os
from concurrent.futures import ThreadPoolExecutor
Q="/tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/quality"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
R=[json.loads(l) for l in open("/home/user/cfadvisers/data/advisers.jsonl")]
norm=lambda u: re.sub(r'https?://(www\.)?','',u).strip('/').lower()
H=[r for r in R if all(norm(s)==norm(r['website']) for s in r['sources'])]
MA=re.compile(r"(mergers?|acquisitions?|M&A|corporate finance|sell(ing)? (your|a) (business|company)|business sale|exit|disposal|MBO|management buy|transaction|deal)",re.I)
def one(r):
    p=subprocess.run(["curl","-sL","--max-time","20","-A",UA,"-o","-","-w","\n__C__%{http_code} %{url_effective}",r['website']],capture_output=True,timeout=30)
    t=p.stdout.decode('utf-8','ignore'); i=t.rfind("\n__C__"); code=t[i+6:]; h=t[:i]
    tx=re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>"," ",h))))
    yr=re.findall(r"(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–]\s*)?(\d{4})",h,re.I)
    links=sorted(set(re.findall(r'href="([^"#]*(?:corporate-finance|mergers|acquisitions|m-a|deals|transactions|team|people|about)[^"#]*)"',h,re.I)))[:8]
    return dict(id=r['id'],type=r['firm_type'],code=code,len=len(tx),ma=len(MA.findall(tx)),yr=yr[-1] if yr else None,links=links)
with ThreadPoolExecutor(24) as ex: out=list(ex.map(one,H))
json.dump(out,open(Q+"/home.json","w"),indent=0)
print(len(out))
