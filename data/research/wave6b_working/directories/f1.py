import json,sys,re
sys.path.insert(0,sys.argv[1])
from known import *
a=json.load(open(sys.argv[1]+'/dalt_all.json'))
print(len(a))
seen=set();out=[]
for x in a:
    w=x.get('web') or ''
    if not w or 'daltons' in w: continue
    d=dom(w)
    if d in seen or d in doms or norm(x['co'] or '') in names: continue
    seen.add(d)
    tel=re.sub(r'\D','',x.get('tel') or '')
    if not (tel.startswith('0') or tel.startswith('44')): continue
    out.append((x['mod'],d,x['co'],x['tel'],x['email']))
out.sort(reverse=True)
for o in out: print(' | '.join(map(str,o)))
