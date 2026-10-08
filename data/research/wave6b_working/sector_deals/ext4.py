import re,collections,sys
exec(open('/tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/sector_deals/chk.py').read().split('for q in sys.argv')[0])
kn=set(norm(k[0].split(' [')[0]) for k in known); kn={k for k in kn if len(k)>2}
p=re.compile(r"((?:[A-Z][\w&'\.-]*\s+){1,3}(?:Corporate Finance|Corporate|Advisory|Advisers|Advisors|M&A|Mergers & Acquisitions|Capital|Partners|Transactions|Associates|Business Sales|Consulting|Accountants|Chartered Accountants|LLP))\b")
c=collections.Counter(); ex={}
for f in sys.argv[1:]:
  for l in open(f):
    if '\t' not in l: continue
    fn,b=l.split('\t',1)
    for s in re.split(r'(?<=[\.!?])\s',b):
        if not re.search(r'advis|acted|lead|support|led by|sale',s,re.I): continue
        for m in p.finditer(s):
            n=m.group(1).strip(); 
            w=n.split()
            while w and w[0] in ('The','A','By','And','With','From','At','Of','Its','Both','While','Leading','Sheffield-based','Manchester-based'): w=w[1:]
            n=' '.join(w); nn=norm(n)
            if len(w)<2 or not nn or nn in kn or any(len(k)>5 and k in nn for k in kn): continue
            c[n]+=1; ex.setdefault(n,(fn[:60],s[:220]))
for n,k in c.most_common(): print(k,n,'|',ex[n][0],'|',ex[n][1])
