import glob,re,html,sys
out=open(sys.argv[2],'w')
for f in glob.glob(sys.argv[1]+'/*.html'):
    t=open(f,errors='ignore').read()
    ps=re.findall(r'<p[^>]*>(.*?)</p>',t,re.S)
    b=' '.join(html.unescape(re.sub(r'<[^>]+>','',p)) for p in ps); b=re.sub(r'\s+',' ',b)
    d=re.search(r'"datePublished":"([0-9-]{10})',t)
    out.write(f.split('/')[-1]+'\t'+(d.group(1) if d else '')+' '+b[:10000]+'\n')
