import glob,re,html
import sys; out=open(sys.argv[2],'w')
for f in glob.glob(sys.argv[1]+'/*.html'):
    t=open(f,errors='ignore').read()
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
    i=t.find('<h1'); t=t[i:] if i>=0 else t
    b=html.unescape(re.sub(r'<[^>]+>',' ',t)); b=re.sub(r'\s+',' ',b)
    for cut in ('You may also','Related news','Sign up'):
        j=b.find(cut); 
        if j>2000: b=b[:j]
    out.write(f[4:]+'\t'+b[:8000]+'\n')
