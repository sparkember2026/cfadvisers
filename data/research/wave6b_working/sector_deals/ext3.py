import re,collections,sys
src=open(sys.argv[1]).read().split('\n')
exec(open('chk.py').read().split('for q in sys.argv')[0].replace("R='/home/user/cfadvisers/'","R='/home/user/cfadvisers/'"))
kn=[norm(k[0].split(' [')[0]) for k in known]; kn=[k for k in kn if len(k)>3]
N=r"((?:[A-Z][\w&'\.\-]*|&|and|of)(?:\s+(?:[A-Z][\w&'\.\-]*|&|and|of)){0,4})"
pats=[re.compile(N+r"(?:'s|’s)?\s+(?:corporate finance|deal advisory|M&A|transaction|CF)?\s*(?:team|division|department)?\s*(?:,[^,]{0,60},\s*)?(?:advised|acted|provided (?:corporate finance|financial|lead|M&A|deal)|was (?:the )?(?:lead|sole|exclusive) (?:financial )?advis|led the (?:sale|deal|process)|ran the (?:sale|process))"),
      re.compile(r"(?:advised by|advice from|advice provided by|supported by|support from|guided by|facilitated by|brokered by|led by|appointed)\s+(?:the\s+)?(?:corporate finance (?:team|specialists|advisers?) (?:at|of|from)\s+)?"+N+r"(?:'s|’s)?\s*(?:corporate finance|Corporate Finance|,|\.|\s(?:on|who|which|with|and))")]
stop=set('The A An This It In On As He She They We Our Its Their Mr Ms Partner Director Managing Lead Corporate Finance Associate Senior Head'.split())
c=collections.Counter(); ex={}
for l in src:
    if '\t' not in l: continue
    f,b=l.split('\t',1)
    for p in pats:
        for m in p.finditer(b):
            n=m.group(1).strip(' &.')
            w=n.split()
            while w and w[0] in stop: w=w[1:]
            n=' '.join(w)
            if len(n)<3: continue
            nn=norm(n)
            if not nn or any(k in nn or nn in k for k in kn): continue
            c[n]+=1; ex.setdefault(n,f[:70])
for n,k in c.most_common(): print(k,n,'|',ex[n])
