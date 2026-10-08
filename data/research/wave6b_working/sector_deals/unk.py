import re,sys
exec(open('/tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/sector_deals/chk.py').read().split('for q in sys.argv')[0])
names=set()
for k in known:
    n=k[0].split(' [')[0].split(' (')[0]
    n=re.sub(r'\b(Corporate Finance|LLP|Ltd|Limited|Group|Advisory|Partners|UK)\b','',n).strip()
    if len(n)>=3: names.add(n.lower())
extra=['kpmg','deloitte','pwc','ey','bdo','rsm','grant thornton','azets','frp','mha','cooper parry','evelyn','smith & williamson','dow schofield','dsw','interpath','begbies','btg','teneo','kroll','alvarez','leonard curtis','quantuma','moorfields','menzies','dains','shoosmiths','gateley','dwf','addleshaw','pinsent','freeths','brabners','knights','irwin mitchell','squire','eversheds','dla','womble','ward hadaway','muckle','sintons','hill dickinson','browne jacobson','mills & reeve','birketts','tlt','osborne clarke','burges salmon','blake morgan','geldards','capital law','hugh james','acuity law','harrison clark','wright hassall','shakespeare martineau','higgs','slater heelis','napthens','schofield sweeney','lupton fawcett','clarion','walker morris','howes percival','ashfords','stephens scown','foot anstey','clarke willmott','thrings','michelmores','bevan brittan','swinburne','hay & kilner','mincoffs','fieldfisher','harper macleod','burness paull','brodies','shepherd','lindsays','thorntons','wilkes','gowling','mishcon','fladgate','taylor wessing','lewis silkin','trowers','weightmans','hcr','ellisons','tees','buckles','weightmans','kuits','gunnercooke','aaron & partners','jmw','fbc manby','anthony collins','enterprise','bgf','ldc','yfm','maven','mercia','foresight','development bank','fw capital','nvm','northedge','palatine','ldc','santander','hsbc','lloyds','natwest','barclays','virgin money','thincats','shawbrook','close brothers','allica','oaknorth','british business bank']
names.update(extra)
out=[]
for f in sys.argv[1:]:
  for l in open(f):
    if '\t' not in l: continue
    a,b=l.split('\t',1)
    for s in re.split(r'(?<=[\.!?”"])\s',b):
        if not re.search(r'corporate finance|lead advis|financial advis|acted as advis|M&A advis',s,re.I): continue
        sl=s.lower()
        if any(n in sl for n in names): continue
        out.append(a[:55]+' :: '+s[:260])
for o in sorted(set(out)): print(o)
