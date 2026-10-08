import re,glob,html,collections,sys
sys.argv=['x']+['/home/user/cfadvisers']
exec(open('/tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/sector_deals/chk.py').read().split('for q in sys.argv')[0])
kn=set(norm(k[0].split(' [')[0]) for k in known)
p=re.compile(r"((?:[A-Z][\w&'\.-]*\s+){1,3}(?:Corporate Finance|Corporate|Advisory|Advisers|Advisors|M&A|Mergers|Capital|Partners|Transactions|Associates|Business Sales|Consulting))")
c=collections.Counter(); ex={}
for f in glob.glob('art/*.html'):
    t=open(f,errors='ignore').read()
    b=html.unescape(re.sub(r'<[^>]+>',' ',t)); b=re.sub(r'\s+',' ',b)
    for s in re.split(r'(?<=[\.!?])\s',b):
        if not re.search(r'advis|acted|lead|support',s,re.I): continue
        for m in p.finditer(s):
            n=m.group(1).strip(); nn=norm(n)
            if any(nn and (nn in k or k in nn) for k in kn if len(k)>3): continue
            c[n]+=1; ex.setdefault(n,(f[4:],s[:200]))
for n,k in c.most_common(400): print(k,n,'|',ex[n][0])
