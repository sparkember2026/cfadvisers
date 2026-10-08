import sys,re,subprocess,html
url=sys.argv[1]
h=subprocess.run(['curl','-sL','--max-time','25','-A','Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120',url],capture_output=True).stdout.decode('utf8','ignore')
t=re.sub(r'(?s)<(script|style|noscript)[^>]*>.*?</\1>',' ',h); t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t); t=re.sub(r'\s+',' ',t)
pc=set(m.group(0) for m in re.finditer(r'.{0,90}\b[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}\b',t))
print('URL',url); print('ADDR',list(pc)[:6]); print('EMAILS',sorted(set(e for e in re.findall(r'[\w.+-]+@[\w-]+\.[a-z.]{2,}',h) if not re.search(r'png|jpg|webp|sentry|wix|example|@\d',e)))[:5])
print('TEXT',t[:int(sys.argv[2]) if len(sys.argv)>2 else 1500])
