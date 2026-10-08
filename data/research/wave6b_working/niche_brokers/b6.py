from add import *
D="https://www.daltonsbusiness.com/agent/"
write([
rec(name="Harrison Spence",website="https://harrisonspence.co.uk",firm_type="business_broker",coverage="national",
 deal_ev_min_m=0.2,deal_ev_max_m=10,deal_size_basis="estimate",services=["sell_side","buy_side","valuations"],sectors=["Financial Services"],
 sector_note="Buying and selling IFA and financial planning practices, plus valuations, consultancy and executive search for retail financial services firms.",contact_email="enquiries@harrisonspence.com",contact_phone="0207 60 20 500",team_url="https://harrisonspence.co.uk/about-us/meet-the-team/",
 description="IFA practice broker and consultancy established in 2007, headed by Alan Marks, handling the purchase and sale of IFA practices and valuations. HQ not confirmed on site (London 020 number).",
 sources=["https://harrisonspence.co.uk/","https://www.gannons.co.uk/insights/selling-an-ifa-business"]),
rec(name="Sprosen",website="https://www.sprosen.com",firm_type="business_broker",hq="Weston-super-Mare",hq_region="South West",offices=["Weston-super-Mare","London"],coverage="national",
 deal_ev_min_m=0.1,deal_ev_max_m=5,deal_size_basis="estimate",services=["sell_side","buy_side","valuations","restructuring"],sectors=["Leisure & Hospitality"],
 sector_note="Sales, lettings and valuations of pubs, restaurants, hotels, bars and other hospitality businesses, plus business restructuring/consultancy.",contact_email="info@sprosen.com",contact_phone="0333 414 9999",contact_url="https://sprosen.com/#contact-us",
 description="Hospitality-focused business and commercial property agent (head office 44 Boulevard, Weston-super-Mare, with offices in central London and South Wales) selling pubs, restaurants, hotels and bars across the UK.",
 sources=["https://www.sprosen.com/",D+"sprosen/"]),
rec(name="ASG Commercial",website="https://www.asgcommercial.co.uk",firm_type="business_broker",hq="Inverness",hq_region="Scotland",offices=["Inverness"],coverage="regional",regions_covered=["Scotland"],
 deal_ev_min_m=0.1,deal_ev_max_m=3,deal_size_basis="estimate",services=["sell_side","valuations"],sectors=["Leisure & Hospitality"],
 sector_note="Highlands commercial agent marketing guest houses, B&Bs, hotels and other hospitality businesses.",contact_phone="01463 714757",
 description="Inverness-based commercial property and business agent marketing Highland hospitality businesses such as guest houses (e.g. Atholdene Guest House, Inverness; Dunallan House, Grantown-on-Spey).",
 sources=["https://www.asgcommercial.co.uk/",D+"asg-commercial/","https://www.rightmove.co.uk/properties/175043240"]),
])
