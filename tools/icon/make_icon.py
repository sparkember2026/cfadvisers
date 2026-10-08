import math, sys
def cres(cx, cy, r, a0, a1, w):
    p = lambda a: (cx + r*math.cos(math.radians(a)), cy + r*math.sin(math.radians(a)))
    (x0, y0), (x1, y1) = p(a0), p(a1)
    chord = math.dist((x0, y0), (x1, y1)); sag = r - math.sqrt(max(r*r - chord*chord/4, 0)) if (a1-a0) < 180 else r
    s2 = max(sag - w, 0.3); r2 = (chord*chord/4 + s2*s2) / (2*s2)
    return f"M{x0:.2f} {y0:.2f}A{r} {r} 0 {1 if a1-a0 > 180 else 0} 1 {x1:.2f} {y1:.2f}A{r2:.2f} {r2:.2f} 0 0 0 {x0:.2f} {y0:.2f}Z"
# rosettes on the brow (between/right of the eyes) and the cheek, as in the photo
spots = [(27,13.5,1.9,160,400,1.0),(33,16,2.1,150,400,1.1),(38.5,21,2.2,150,390,1.1),(32,24,1.9,160,400,1.0),
         (40,29.5,2.3,140,390,1.2),(34.5,33.5,2.2,150,390,1.1),(41.5,38,2.1,150,390,1.1),(35,42,2,160,400,1.0),
         (29.5,48,1.8,160,400,0.9),(37,49.5,1.9,160,400,1.0)]
cuts = "".join(f'<path d="{cres(*s)}"/>' for s in spots)
eye = lambda cx, cy, s: (f'<path class="cut" d="M{cx-6*s:.1f} {cy:.1f} C{cx-4*s:.1f} {cy-5.4*s:.1f} {cx+4*s:.1f} {cy-5.6*s:.1f} {cx+6.2*s:.1f} {cy-0.4*s:.1f} '
                          f'C{cx+4*s:.1f} {cy+5.2*s:.1f} {cx-4*s:.1f} {cy+5.2*s:.1f} {cx-6*s:.1f} {cy:.1f} Z"/>'
                          f'<circle class="eye" cx="{cx:.1f}" cy="{cy:.1f}" r="{4.1*s:.1f}"/><circle class="pupil" cx="{cx-0.6*s:.1f}" cy="{cy-0.3*s:.1f}" r="{1.9*s:.1f}"/>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <title>Young leopard looking out from behind a tree</title>
  <style>
    .ink {{ fill: #17140f; }} .cut {{ fill: #fff; }} .eye {{ fill: #c9b03a; }} .pupil {{ fill: #17140f; }}
    .whisker {{ fill: none; stroke: #17140f; stroke-width: 1; stroke-linecap: round; }}
    @media (prefers-color-scheme: dark) {{ .ink {{ fill: #f2ede2; }} .cut {{ fill: #17140f; }} .whisker {{ stroke: #f2ede2; }} }}
  </style>
  <!-- head tilted on its side: crown and big ear top right, cheek down the middle, chin resting on the branch -->
  <path class="ink" d="M8 6 C14 4 20 3.5 25 4.5 C27 1.5 31 0.5 35 0.6 C42 0.8 47 4 48 9 C49 13 47.5 17 45 19.5
    C48 24 49.5 30 49 36 C48.5 43 46 49 42 53.5 C36 59.5 26 61 17 59 L9 58 Z"/>
  <!-- inner ear -->
  <path class="cut" d="M30.5 5.6 C33.5 3.4 38.5 3.4 42 5.6 C44.5 7.4 45 10.6 43.4 13.6 C42.6 10.6 40.6 8.6 37.6 7.6 C35.4 6.9 32.8 6.6 30.5 5.6 Z"/>
  <!-- brow ridge cut above the upper eye -->
  <path class="cut" d="M12 15.5 C15 13 19.5 12.6 23 14.2 C19.6 14 16 14.8 12 15.5 Z"/>
  {eye(16.5, 22, 1.0)}
  {eye(17.5, 47, 0.9)}
  <!-- tear lines from each eye towards the muzzle behind the tree -->
  <path class="cut" d="M10.5 26.5 C12.5 30 15.5 32.5 19.5 33.6 C15.4 34 12 31.8 10 28 Z"/>
  <path class="cut" d="M12.4 50.6 C14 53.2 16.6 54.8 20 55.4 C16.4 56.2 13.4 54.6 11.6 52 Z"/>
  <g class="cut">{cuts}</g>
  <!-- whiskers sweeping right, as in the photo -->
  <path class="whisker" d="M43 30 C49 28.5 55 27.5 62 27.6"/><path class="whisker" d="M44 33.5 C50 33 56 33.4 61.5 34.6"/>
  <path class="whisker" d="M43.5 44 C50 45 56 47 61 50"/>
  <!-- branch along the bottom -->
  <path class="ink" d="M8 57 C24 59.5 42 58 60 56.5 C61.5 58 61.5 61 60 62.5 C42 64 24 64 8 63.5 Z"/>
  <!-- thin trunk down the left edge, in front -->
  <path class="ink" d="M0.5 0 H9.5 C8.6 12 10.4 26 9.4 40 C8.8 50 10 57 9.6 64 H0.5 Z"/>
  <path class="cut" d="M5 4 C5.8 12 4.4 22 5.4 31 C4 22 4.4 12 5 4 Z"/>
  <path class="cut" d="M6.4 38 C7.2 45 5.8 52 6.6 59 C5.4 52 5.8 45 6.4 38 Z"/>
</svg>
'''
open(sys.argv[1], "w").write(svg)
