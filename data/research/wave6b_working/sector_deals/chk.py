import sys,re,json
from urllib.parse import urlparse
R='/home/user/cfadvisers/'
def dom(u):
    u=u.strip()
    if '://' not in u: u='http://'+u
    d=urlparse(u).netloc.lower()
    return d[4:] if d.startswith('www.') else d
def norm(n):
    n=n.lower()
    for w in ['corporate finance','corporate','limited','ltd','llp','advisory','advisers','advisors','group','partners','the ']: n=n.replace(w,'')
    return re.sub(r'[^a-z0-9]','',n)
known=[]
for l in open(R+'data/existing_firms.txt'):
    p=[x.strip() for x in l.split('|')]
    if len(p)>1: known.append((p[0],dom(p[1]) if p[1] else ''))
import glob
for f in glob.glob(R+'data/research/*.jsonl'):
    for l in open(f):
        try: r=json.loads(l); known.append((r['name']+' ['+f.split('/')[-1]+']',dom(r['website'])))
        except: pass
ch=[]
for l in open(R+'data/companies_house/bulk_candidates.jsonl'):
    try: ch.append(json.loads(l)['company_name'])
    except: pass
for q in sys.argv[1:]:
    hits=[k for k in known if (('.' in q and dom(q)==k[1]) or (norm(q) and len(norm(q))>3 and (norm(q)==norm(k[0].split(' [')[0]) or (len(norm(q))>5 and norm(q) in norm(k[0])))))]
    chh=[c for c in ch if norm(q.split('.')[0]) and norm(q.split('.')[0]) in norm(c)][:3]
    print(q,'=>',hits[:4],'| CH:',chh)
