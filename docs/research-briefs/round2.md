LATER RESEARCH ROUNDS: we already have a few hundred firms. The list of firms already found is in
/home/user/cfadvisers/data/existing_firms.txt (regenerated each round with `python -m cfadvisers known --out data/existing_firms.txt`; lines starting "(excluded)" are firms we removed on purpose: don't re-add them) (name | website | type | hq).
Only add firms that are NOT in that list (match on website domain and on name; a firm is the same if it's the same website).
WebSearch is a scarce budget shared by five agents: use at most the number of searches your segment gives you (default ~45), and prefer searches that return
pages LISTING MANY firms (award shortlists, league tables, network member directories, "top corporate finance advisers in X" articles,
Companies House name searches via https://find-and-update.company-information.service.gov.uk/search/companies?q=...).
Then verify each firm by fetching its own website directly (curl / WebFetch do not count against the search budget).
Skip firms with no working website, dormant firms, and one-person shells with no evidence of deals.
