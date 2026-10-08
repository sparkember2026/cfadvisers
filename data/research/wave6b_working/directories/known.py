import json,re,glob
from urllib.parse import urlparse
def dom(u):
    u=u.strip().lower()
    if not u.startswith('http'): u='http://'+u
    d=urlparse(u).netloc.split(':')[0]
    return d[4:] if d.startswith('www.') else d
def norm(n): return re.sub(r'[^a-z0-9]','',re.sub(r'\b(ltd|limited|llp|plc|the|and|co|uk)\b','',n.lower()))
doms=set();names=set()
for l in open('/home/user/cfadvisers/data/existing_firms.txt'):
    p=[x.strip() for x in l.split('|')]
    if len(p)>1: doms.add(dom(p[1])); names.add(norm(p[0].replace('(excluded)','')))
for f in glob.glob('/home/user/cfadvisers/data/research/*.jsonl'):
    for l in open(f):
        if l.strip():
            r=json.loads(l); doms.add(dom(r.get('website') or 'x')); names.add(norm(r.get('name') or 'x'))
for l in open('/home/user/cfadvisers/data/excluded.txt'):
    l=l.strip()
    if l and not l.startswith('#'): doms.add(dom(l.split()[0])); 
