import json,re,subprocess
from concurrent.futures import ThreadPoolExecutor
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
R=[json.loads(l) for l in open("/home/user/cfadvisers/data/advisers.jsonl")]
SIG=re.compile(r"/lander|parking-lander|domain (?:is )?for sale|buy this domain|this domain (?:may be|is) for sale|sedoparking|parkingcrew|hugedomains|dan\.com|afternic|domain has expired|account suspended|website is (?:currently )?under construction|coming soon|Index of /|Default Web Site Page|Welcome to nginx|It works!",re.I)
def one(r):
    try:
        p=subprocess.run(["curl","-sL","--max-time","20","-A",UA,"-o","-","-w","\n__C__%{http_code} %{url_effective}",r['website']],capture_output=True,timeout=30)
        t=p.stdout.decode('utf-8','ignore'); i=t.rfind("\n__C__"); code=t[i+6:]; h=t[:i]
    except Exception as e: return (r['id'],'ERR','',0)
    m=SIG.search(h)
    return (r['id'],code,m.group(0) if m else '',len(h))
with ThreadPoolExecutor(32) as ex: out=list(ex.map(one,R))
for o in out:
    if o[2] or o[1].startswith(('000','404','410','5')) : print(o)
