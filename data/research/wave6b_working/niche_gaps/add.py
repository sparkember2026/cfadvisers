import json,sys
ALL=["London","South East","South West","East of England","East Midlands","West Midlands","Yorkshire and the Humber","North West","North East","Scotland","Wales","Northern Ireland"]
OUT='/home/user/cfadvisers/data/research/wave6b_niche_gaps.jsonl'
def rec(**k):
    base=dict(parent=None,offices=[],coverage="national",regions_covered=ALL,cf_professionals=None,cf_professionals_basis=None,
      deal_ebitda_min_m=None,deal_ebitda_max_m=None,deal_ev_min_m=None,deal_ev_max_m=None,deal_size_basis=None,deal_size_note=None,
      services=["sell_side"],sectors=["Generalist"],sector_note=None,contact_email=None,contact_phone=None,team_url=None,contact_url=None,linkedin_url=None)
    base.update(k); return base
recs=[]
exec(open(sys.argv[1]).read())
with open(OUT,'a') as f:
    for r in recs: f.write(json.dumps(r,ensure_ascii=False)+'\n')
print(len(recs),'appended')
