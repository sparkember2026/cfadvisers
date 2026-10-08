d=$1
h=$(curl -sL --max-time 20 -A 'Mozilla/5.0' -o /dev/null -w '%{http_code} %{url_effective}' "https://$d" 2>/dev/null || true)
t=$(curl -sL --max-time 20 -A 'Mozilla/5.0' "https://$d" 2>/dev/null | tr '\n' ' ' | grep -oiE '<title[^>]*>[^<]*' | head -1 | sed 's/<title[^>]*>//')
echo "$d | $h | $t"
