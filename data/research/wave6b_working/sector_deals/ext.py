import sys,re,glob,html,collections
pat=re.compile(r"([A-Z][\w&'\.-]*(?:\s+(?:&\s+)?[A-Z][\w&'\.-]*){0,4})(?:'s)?\s+(?:corporate finance|M&A|mergers)?\s*(?:team\s+)?(?:advised|acted as|provided (?:corporate finance|financial|M&A) advice|was lead adviser|were lead advisers|led the sale)",re.S)
pat2=re.compile(r"(?:advised by|advice from|support from|with advice from|guided by)\s+(?:the\s+)?(?:corporate finance team (?:at|of)\s+)?([A-Z][\w&'\.-]*(?:\s+(?:&\s+)?[A-Z][\w&'\.-]*){0,4})")
cnt=collections.Counter(); ex={}
for f in glob.glob(sys.argv[1]+'/*.html'):
    t=open(f,errors='ignore').read()
    m=re.search(r'<article.*?</article>',t,re.S)
    body=m.group(0) if m else t
    body=html.unescape(re.sub(r'<[^>]+>',' ',body)); body=re.sub(r'\s+',' ',body)
    sect=bool(re.search(r'haul|logistic|transport|freight|motor|vehicle|dealership|construction|civil engineering|engineering|manufactur|facilities|cleaning|security|fire|waste|recycl|telecom|fibre|electrical|mechanical|plumbing|heating|building services|roofing|scaffold|steel|precision|garage|coach|courier|crane|plant hire|demolition|groundwork|lift|contractor',body,re.I))
    if not sect: continue
    for p in (pat,pat2):
        for mm in p.finditer(body):
            n=mm.group(1).strip()
            cnt[n]+=1; ex.setdefault(n,f.split('/')[-1])
for n,c in cnt.most_common():
    print(c,n,'|',ex[n])
