"""data/contributions.json -> SVG do heatmap (53 semanas) com revelação diagonal única e rodapé de stats.
STATIC=1 gera o quadro final (sem animação)."""
import json
import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "assets" / ("heatmap.static.svg" if STATIC else "heatmap.svg")

BG, INK, DIM = "#0d1117", "#c9d1d9", "#8b949e"
BLUE, RED = "#4C7BF4", "#D7262B"
LEVELS = ["#161b22", "#1F3FA0", "#2E58D0", "#4C7BF4", "#9DB8FF"]
CELL, GAP, LEFT, TOP = 12, 3, 40, 56
STEP = CELL + GAP
DELAY = 0.028   # s por diagonal (semana + dia da semana)
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
DIAS = {1: "seg", 3: "qua", 5: "sex"}


def build(data):
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    off = (first.weekday() + 1) % 7                       # domingo = 0
    weeks = (off + len(days) + 6) // 7
    W = LEFT + weeks * STEP + 20
    H = TOP + 7 * STEP + 78
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Contribuições de {data["user"]} no último ano: {data["total"]}">',
         f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>',
         f'<g font-family="Consolas,\'DejaVu Sans Mono\',\'Courier New\',monospace" font-size="11" fill="{DIM}">',
         f'<text x="16" y="26" fill="{INK}" font-size="13"><tspan fill="{BLUE}">$</tspan> git log --since=1.year --author={data["user"]}</text>']
    last_m = -1
    cells = []
    for i, d in enumerate(days):
        dt = date.fromisoformat(d["date"])
        idx = i + off
        wk, dow = divmod(idx, 7)
        x, y = LEFT + wk * STEP, TOP + dow * STEP
        if dow == 0 and dt.month != last_m:
            if last_m != -1 or dt.day <= 14:
                o.append(f'<text x="{x}" y="{TOP-8}">{MESES[dt.month-1]}</text>')
            last_m = dt.month
        lvl = max(0, min(4, d["level"]))
        today = i == len(days) - 1
        stroke = f' stroke="{RED}" stroke-width="1.5"' if today else ""
        tip = f'<title>{d["count"]} contribuições em {d["date"]}</title>'
        if STATIC:
            cells.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{LEVELS[lvl]}"{stroke}>{tip}</rect>')
        else:
            b = 0.3 + (wk + dow) * DELAY
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{LEVELS[lvl]}"{stroke} opacity="0">{tip}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{b:.2f}s" dur="0.25s" fill="freeze"/></rect>')
    for r, name in DIAS.items():
        o.append(f'<text x="8" y="{TOP + r*STEP + 10}">{name}</text>')
    o += cells
    fy = TOP + 7 * STEP + 26
    stats = [("total", data["total"], BLUE), ("sequência atual", f'{data["current_streak"]}d', INK),
             ("maior sequência", f'{data["longest_streak"]}d', RED)]
    x = 16
    t0 = 0.3 + (weeks + 7) * DELAY
    for k, (label, val, col) in enumerate(stats):
        anim = "" if STATIC else (f' opacity="0"><animate attributeName="opacity" from="0" to="1" '
                                  f'begin="{t0 + k*0.2:.2f}s" dur="0.4s" fill="freeze"/')
        o.append(f'<g{anim}>' + (f'<text x="{x}" y="{fy+16}" font-size="20" font-weight="bold" fill="{col}">{val}</text>'
                 f'<text x="{x}" y="{fy+34}">{label}</text>') + '</g>')
        x += 170
    # legenda
    lx = W - 20 - (5 * STEP + 70)
    o.append(f'<text x="{lx}" y="{fy+30}">menos</text>')
    for j, c in enumerate(LEVELS):
        o.append(f'<rect x="{lx + 38 + j*STEP}" y="{fy+20}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
    o.append(f'<text x="{lx + 42 + 5*STEP}" y="{fy+30}">mais</text>')
    o.append("</g></svg>")
    return "\n".join(o)


if __name__ == "__main__":
    OUT.write_text(build(json.loads(SRC.read_text(encoding="utf-8"))), encoding="utf-8")
    print("ok:", OUT)
