import json,sys
ALL=["London","South East","South West","East of England","East Midlands","West Midlands","Yorkshire and the Humber","North West","North East","Scotland","Wales","Northern Ireland"]
OUT='/home/user/cfadvisers/data/research/wave6b_directories.jsonl'
KEYS=["name","website","firm_type","parent","hq","hq_region","offices","coverage","regions_covered","cf_professionals","cf_professionals_basis","deal_ebitda_min_m","deal_ebitda_max_m","deal_ev_min_m","deal_ev_max_m","deal_size_basis","deal_size_note","services","sectors","sector_note","contact_email","contact_phone","team_url","contact_url","linkedin_url","description","sources"]
def rec(**k):
    r={x:None for x in KEYS}
    for x in ["offices","regions_covered","services","sectors","sources"]: r[x]=[]
    if k.get('coverage')=='national' and 'regions_covered' not in k: k['regions_covered']=ALL
    r.update(k)
    if r['cf_professionals'] is None: r['cf_professionals_basis']=None
    return r
def write(recs):
    try: have={json.loads(l)['website'] for l in open(OUT) if l.strip()}
    except FileNotFoundError: have=set()
    with open(OUT,'a') as f:
        for r in recs:
            if r['website'] in have: continue
            f.write(json.dumps(r,ensure_ascii=False)+'\n')
