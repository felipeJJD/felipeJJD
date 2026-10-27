"""data/contributions.json -> SVG do "skyline" 3D: cada dia vira um prédio isométrico (altura = raiz das
contribuições, para um dia grande não achatar o resto) que sobe numa onda diagonal, uma vez só.
Técnica do avivashishta.com/blog/animate-github-contribution-graph-portfolio, refeita em SVG puro (README
não roda JS). STATIC=1 gera o quadro final."""
import json
import math
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "assets" / ("skyline.static.svg" if STATIC else "skyline.svg")

BG, INK, DIM = "#0d1117", "#c9d1d9", "#8b949e"
BLUE, RED = "#4C7BF4", "#D7262B"
TOPS = ["#1b2230", "#1F3FA0", "#2E58D0", "#4C7BF4", "#9DB8FF"]
WV = (11.0, 3.4)    # eixo das semanas na tela
DV = (-7.0, 5.6)    # eixo dos dias
S = 0.78            # lado do prédio em unidades de célula
K = 14.0            # px de altura por raiz de contribuição
DELAY = 0.03


def shade(hexc, f):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))


def build(data):
    days = data["days"]
    off = (date.fromisoformat(days[0]["date"]).weekday() + 1) % 7
    weeks = (off + len(days) + 6) // 7
    peak = max((d["count"] for d in days), default=0)
    hmax = math.sqrt(peak) * K
    ox, oy = 7 * -DV[0] + 30, hmax + 48
    W = int(ox + weeks * WV[0] + 24)
    H = int(oy + weeks * WV[1] + 7 * DV[1] + 56)

    def p(w, d, h=0.0):
        return (ox + w * WV[0] + d * DV[0], oy + w * WV[1] + d * DV[1] - h)

    def poly(pts, fill):
        return '<polygon points="%s" fill="%s"/>' % (" ".join(f"{x:.1f},{y:.1f}" for x, y in pts), fill)

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Skyline 3D das contribuições de {data["user"]}: {data["total"]} no último ano">',
         f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>',
         f'<g font-family="Consolas,\'DejaVu Sans Mono\',\'Courier New\',monospace" font-size="13" fill="{DIM}">',
         f'<text x="16" y="28" fill="{INK}"><tspan fill="{BLUE}">$</tspan> gh skyline --user={data["user"]} --year</text>']
    cells = []
    for i, d in enumerate(days):
        wk, dow = divmod(i + off, 7)
        cells.append((wk * WV[1] + dow * DV[1], wk, dow, d, i == len(days) - 1))
    cells.sort(key=lambda c: c[0])                         # de trás para a frente (pintor)
    for _, wk, dow, d, today in cells:
        lvl = max(0, min(4, d["level"]))
        h = math.sqrt(d["count"]) * K if d["count"] else 0.0
        a, b, c, e = p(wk, dow), p(wk + S, dow), p(wk + S, dow + S), p(wk, dow + S)
        top = TOPS[lvl] if not today else RED
        tip = f'<title>{d["count"]} contribuições em {d["date"]}</title>'
        if h == 0:
            o.append(f'<g opacity="{1 if STATIC else 0}">{tip}{poly([a, b, c, e], top)}' +
                     ("" if STATIC else f'<animate attributeName="opacity" to="1" begin="{0.3 + (wk + dow) * DELAY:.2f}s" dur="0.3s" fill="freeze"/>') +
                     "</g>")
            continue
        up = lambda q: (q[0], q[1] - h)
        right = poly([b, c, up(c), up(b)], shade(top, 0.55))   # face do eixo das semanas
        front = poly([e, c, up(c), up(e)], shade(top, 0.75))   # face do eixo dos dias
        roof = poly([up(a), up(b), up(c), up(e)], top)
        body = right + front + roof
        if STATIC:
            o.append(f"<g>{tip}{body}</g>")
        else:
            # cresce a partir do chão: escala vertical em torno da base do prédio
            bx, by = c
            beg = 0.3 + (wk + dow) * DELAY
            o.append(f'<g>{tip}<g transform="translate({bx:.1f} {by:.1f})"><g transform="scale(1 0)">'
                     f'<animateTransform attributeName="transform" type="scale" values="1 0;1 1.12;1 1" keyTimes="0;0.7;1" '
                     f'begin="{beg:.2f}s" dur="0.7s" fill="freeze"/>'
                     f'<g transform="translate({-bx:.1f} {-by:.1f})">{body}</g></g></g></g>')
    fy = H - 26
    o.append(f'<text x="16" y="{fy}"><tspan fill="{BLUE}" font-size="18">{data["total"]}</tspan> contribuições  '
             f'<tspan fill="{RED}" font-size="18">{peak}</tspan> no dia mais forte  '
             f'<tspan fill="{INK}" font-size="18">{data["longest_streak"]}d</tspan> maior sequência</text>')
    o.append("</g></svg>")
    return "\n".join(o)


if __name__ == "__main__":
    OUT.write_text(build(json.loads(SRC.read_text(encoding="utf-8"))), encoding="utf-8")
    print("ok:", OUT)
