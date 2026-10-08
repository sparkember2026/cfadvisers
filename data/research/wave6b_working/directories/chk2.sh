d=$1
r=$(curl -sL --max-time 20 -A 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120' -o /tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/directories/pg_$d.html -w '%{http_code} %{url_effective}' "http://www.$d" 2>/dev/null)
t=$(tr '\n' ' ' < /tmp/claude-0/-home-user-cfadvisers/550d5a78-fe4d-5c88-a64b-fde45d1a4d7c/scratchpad/directories/pg_$d.html 2>/dev/null| grep -aoiE '<title[^>]*>[^<]*' | head -1 | sed 's/<title[^>]*>//')
echo "$d | $r | $t"
