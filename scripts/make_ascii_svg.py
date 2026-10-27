"""Foto preparada -> SVG de arte ASCII que "imprime" linha a linha (SMIL, sem JS).
Cada linha é revelada da esquerda para a direita por um clip animado, com cursor em bloco,
escalonada de cima para baixo. Toca uma vez e fica. STATIC=1 gera só o quadro final."""
import os
from pathlib import Path

import cv2

from prep_photo import prep

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"
OUT = ROOT / "assets" / ("ascii-avatar.static.svg" if STATIC else "ascii-avatar.svg")

COLS, CW, CH, FS = 90, 6, 10, 10        # colunas, largura/altura da célula, fonte
RAMP = " .:-=+*#%@"                     # do vazio ao denso
INK, CURSOR, BG = "#c9d1d9", "#4C7BF4", "#0d1117"
ROW_STEP, ROW_DUR, START = 0.06, 0.5, 0.4   # segundos


def ascii_rows(img):
    h, w = img.shape
    rows = round(COLS * CW / CH * h / w)
    small = cv2.resize(img, (COLS, rows), interpolation=cv2.INTER_AREA)
    n = len(RAMP) - 1
    return ["".join(RAMP[int(v / 255 * n + 0.5)] for v in r) for r in small]


def build(rows):
    W, H = COLS * CW, len(rows) * CH
    pad = 12
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W + 2*pad}" height="{H + 2*pad}" '
           f'viewBox="{-pad} {-pad} {W + 2*pad} {H + 2*pad}" role="img" aria-label="Avatar lipenation em ASCII">',
           f'<rect x="{-pad}" y="{-pad}" width="{W + 2*pad}" height="{H + 2*pad}" rx="10" fill="{BG}"/>']
    clips, body = [], []
    t = START
    for i, line in enumerate(rows):
        if not line.strip():
            continue
        y = i * CH
        begin = START + i * ROW_STEP
        if STATIC:
            clips.append("")
            body.append(f'<text x="0" y="{y + FS}" textLength="{COLS*CW}" lengthAdjust="spacing">{esc(line)}</text>')
            continue
        clips.append(
            f'<clipPath id="c{i}"><rect x="0" y="{y}" width="0" height="{CH}">'
            f'<animate attributeName="width" from="0" to="{W}" begin="{begin:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'</rect></clipPath>')
        body.append(f'<text clip-path="url(#c{i})" x="0" y="{y + FS}" textLength="{COLS*CW}" lengthAdjust="spacing">{esc(line)}</text>')
        body.append(
            f'<rect y="{y + 1}" width="{CW}" height="{CH - 2}" x="0" fill="{CURSOR}" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{begin:.2f}s"/>'
            f'<animate attributeName="x" from="0" to="{W - CW}" begin="{begin:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0" begin="{begin + ROW_DUR:.2f}s"/></rect>')
    out.append("<defs>" + "".join(clips) + "</defs>")
    out.append(f'<g font-family="Consolas,\'DejaVu Sans Mono\',\'Courier New\',monospace" font-size="{FS}" font-weight="bold" '
               f'fill="{INK}">' + "".join(body) + "</g></svg>")
    return "\n".join(out)


def esc(s):
    # espaço comum colapsa em navegadores (xml:space é ignorado): usa NBSP
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", " ")


if __name__ == "__main__":
    src = ROOT / "assets" / "avatar.png"
    prepped = prep(src, ROOT / "assets" / "avatar_prepped.png")
    svg = build(ascii_rows(cv2.imread(str(prepped), cv2.IMREAD_GRAYSCALE)))
    OUT.write_text(svg, encoding="utf-8")
    print("ok:", OUT, f"({len(svg)//1024} KB, {'estático' if STATIC else 'animado'})")
