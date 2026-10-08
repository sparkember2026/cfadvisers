import sys,re,json
from urllib.parse import urlparse
def dom(u):
    u=u.strip()
    if not u.startswith('http'): u='http://'+u
    d=urlparse(u).netloc.lower()
    return d[4:] if d.startswith('www.') else d
ex=open('/home/user/cfadvisers/data/existing_firms.txt').read().lower()
doms=set()
for l in ex.splitlines():
    p=[x.strip() for x in l.split('|')]
    if len(p)>1 and p[1]: doms.add(dom(p[1]))
ch=open('/home/user/cfadvisers/data/companies_house/bulk_candidates.jsonl').read().lower()
try: mine=open('/home/user/cfadvisers/data/research/wave6b_niche_brokers.jsonl').read().lower()
except: mine=''
for a in sys.argv[1:]:
    if '.' in a and ' ' not in a:
        d=dom(a); print(a,'EXISTS' if d in doms else ('MINE' if d in mine else 'new'))
    else:
        k=a.lower(); print(a,'NAME-HIT' if k in ex else ('CH' if k in ch else ('MINE' if k in mine else 'new')))
