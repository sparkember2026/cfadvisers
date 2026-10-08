import json,sys
o=json.loads(sys.stdin.read())
assert o["action"] in ("override","exclude") and o["id"] and o["reason"] and o["sources"]
with open("/home/user/cfadvisers/data/research/wave6b_proposals.jsonl","a") as f: f.write(json.dumps(o,ensure_ascii=False)+"\n")
print("ok",o["id"])
