import json,glob,re,sys
from urllib.parse import urlparse
def dom(u):
    u=u.strip()
    if '://' not in u: u='https://'+u
    d=urlparse(u).netloc.lower()
    return d[4:] if d.startswith('www.') else d
names=[];doms=set()
for l in open('/home/user/cfadvisers/data/existing_firms.txt'):
    p=[x.strip() for x in l.split('|')]
    if len(p)>1: names.append(p[0].lower()); doms.add(dom(p[1]))
for f in glob.glob('/home/user/cfadvisers/data/research/wave6b_*.jsonl'):
    for l in open(f):
        if l.strip():
            r=json.loads(l); names.append((r.get('name') or r.get('firm') or '').lower()); doms.add(dom(r.get('website') or r.get('url') or 'x'))
for q in sys.argv[1:]:
    d=dom(q) if '.' in q else None
    hits=[n for n in names if q.lower() in n] if not d else []
    print(q, 'DOMAIN-KNOWN' if d and d in doms else '', hits[:5])
