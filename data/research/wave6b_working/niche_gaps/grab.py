import sys,re,html,subprocess
for u in sys.argv[1:]:
    t=subprocess.run(['curl','-sL','--max-time','20','-A','Mozilla/5.0',u],capture_output=True,text=True,errors='ignore').stdout
    em=set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+',t)); 
    t2=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S);t2=re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',t2)))
    ph=set(re.findall(r'(?:\+44\s?\(?0?\)?\s?|0)\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4}',t2))
    pc=set(re.findall(r'[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}\b',t2))
    co=set(re.findall(r'[A-Z][\w&\' ]{2,40} (?:Limited|Ltd|LLP)\b[^.]{0,80}',t2))
    li=set(re.findall(r'https://(?:www\.|uk\.)?linkedin\.com/company/[\w-]+',t))
    print('==',u,'\n emails',[e for e in em if not e.endswith(('.png','.jpg','.webp'))][:6],'\n phones',list(ph)[:4],'\n postcodes',list(pc)[:6],'\n co',list(co)[:4],'\n li',list(li)[:2])
