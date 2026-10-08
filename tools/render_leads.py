"""Re-score Companies House lead sites in headless Chromium (many small-firm sites render their text with JavaScript).

    python tools/render_leads.py [--min 0 --max 4]

Reads data/companies_house/lead_sites.jsonl, loads each site whose plain-fetch `ma_score` is in [min, max] in Chromium
(/opt/pw-browsers), and writes data/companies_house/lead_sites_rendered.jsonl with `rendered_ma_score` and the first
400 characters of visible text. No model calls, no web searches.
"""
import argparse, asyncio, json, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from ch_leads import MA_WORDS  # noqa: E402
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


async def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--min", type=int, default=0); ap.add_argument("--max", type=int, default=4)
    a = ap.parse_args()
    leads = [json.loads(l) for l in open(ROOT / "data/companies_house/lead_sites.jsonl")]
    todo = [r for r in leads if a.min <= r["ma_score"] <= a.max]
    out, sem = [], asyncio.Semaphore(6)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME)
        async def one(r):
            async with sem:
                pg = await b.new_page()
                try:
                    await pg.goto(r["website"], timeout=30000, wait_until="networkidle")
                    txt = " ".join((await pg.inner_text("body")).split())
                except Exception as e:
                    txt = ""; r["render_error"] = str(e)[:120]
                await pg.close()
                r["rendered_ma_score"] = len(MA_WORDS.findall(txt)); r["rendered_text"] = txt[:400]
                out.append(r)
        await asyncio.gather(*(one(r) for r in todo))
        await b.close()
    out.sort(key=lambda r: -r["rendered_ma_score"])
    with open(ROOT / "data/companies_house/lead_sites_rendered.jsonl", "w") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in out)
    print(f"{len(out)} rendered; {sum(r['rendered_ma_score'] >= 5 for r in out)} now with strong M&A wording")

asyncio.run(main())
