import sys,re
L=open('/tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/sector_deals/'+(sys.argv[2] if len(sys.argv)>2 and sys.argv[1]=='-c' else 'corpus.txt')).read().split('\n')
for n in sys.argv[1:]:
    print('==',n); k=0
    for l in L:
        m=re.search(re.escape(n),l)
        if m:
            print('  ',l.split('\t')[0][:60],'::',l[max(0,m.start()-200):m.end()+100]); k+=1
        if k>=2: break
