import json,sys
OUT='/home/user/cfadvisers/data/research/wave6b_sector_deals.jsonl'
D=dict(parent=None,hq=None,hq_region=None,offices=[],coverage=None,regions_covered=[],cf_professionals=None,cf_professionals_basis=None,
 deal_ebitda_min_m=None,deal_ebitda_max_m=None,deal_ev_min_m=None,deal_ev_max_m=None,deal_size_basis=None,deal_size_note=None,
 services=[],sectors=[],sector_note=None,contact_email=None,contact_phone=None,team_url=None,contact_url=None,linkedin_url=None,description=None,sources=[])
ALL=["London","South East","South West","East of England","East Midlands","West Midlands","Yorkshire and the Humber","North West","North East","Scotland","Wales","Northern Ireland"]
recs=json.load(open(sys.argv[1]))
with open(OUT,'a') as f:
    for r in recs:
        o=dict(name=r['name'],website=r['website'],firm_type=r['firm_type']); 
        for k,v in D.items(): o[k]=r.get(k,v)
        if o['regions_covered']=='ALL': o['regions_covered']=ALL
        f.write(json.dumps(o,ensure_ascii=False)+'\n')
print('appended',len(recs))
