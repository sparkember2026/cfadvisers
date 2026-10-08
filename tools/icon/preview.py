import asyncio, sys
from playwright.async_api import async_playwright
svg = open(sys.argv[1]).read().replace("\n", " ")
import urllib.parse
u = "data:image/svg+xml," + urllib.parse.quote(svg)
html = f"""<body style="margin:0;font:12px sans-serif">
<div style="display:flex;gap:18px;align-items:end;padding:14px;background:#fff">
<img src="{u}" width="256"><img src="{u}" width="64"><img src="{u}" width="32"><img src="{u}" width="16"></div>
<div style="display:flex;gap:18px;align-items:end;padding:14px;background:#202124">
<img src="{u}" width="64"><img src="{u}" width="32"><img src="{u}" width="16"></div></body>"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        for scheme in ("light", "dark"):
            pg = await b.new_page(viewport={"width": 480, "height": 400}, color_scheme=scheme, device_scale_factor=1)
            await pg.set_content(html); await pg.wait_for_timeout(200)
            await pg.screenshot(path=f"{sys.argv[2]}_{scheme}.png", full_page=True)
        await b.close()
asyncio.run(main())
