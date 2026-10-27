"""Cartão estilo neofetch (SVG): as linhas entram com fade + slide uma vez e ficam.
Edite o dict CARD abaixo. STATIC=1 gera o quadro final (sem animação)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = os.environ.get("STATIC") == "1"
OUT = ROOT / "assets" / ("info-card.static.svg" if STATIC else "info-card.svg")

# ---- CONTEÚDO (edite aqui) -------------------------------------------------
CARD = {
    "user": "felipeJJD",
    "host": "lipenation",
    "lines": [  # (rótulo, valor)
        ("Role", "Programador Full Stack"),
        ("Formação", "Engenharia de Software"),
        ("Especialidade", "Inteligência Artificial"),
        ("Foco", "IA · agentes"),
        ("Stack", "TypeScript · JavaScript · Python · Swift"),
        ("IA", "Claude Code · agentes · MCP"),
        ("Vídeo", "Remotion · ffmpeg · motion"),
        ("Instagram", "@astro_lipenation"),
        ("GitHub", "github.com/felipeJJD"),
        ("Mood", "Fanático pelo desconhecido"),
    ],
}
# ----------------------------------------------------------------------------
BG, BAR, INK, DIM = "#0d1117", "#161b22", "#c9d1d9", "#8b949e"
BLUE, RED = "#4C7BF4", "#D7262B"
W, LH, TOP, PAD = 640, 26, 78, 24
LABEL_W = 150


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def anim(begin):
    if STATIC:
        return ""
    return (f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-14 0" to="0 0" '
            f'begin="{begin:.2f}s" dur="0.35s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/>')


def build():
    n = len(CARD["lines"])
    H = TOP + (n + 1) * LH + 50
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Cartão de apresentação de {esc(CARD["user"])}">',
         f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>',
         f'<path d="M0 10a10 10 0 0 1 10-10h{W-20}a10 10 0 0 1 10 10v26H0z" fill="{BAR}"/>',
         f'<circle cx="22" cy="18" r="6" fill="{RED}"/><circle cx="42" cy="18" r="6" fill="#d29922"/>'
         f'<circle cx="62" cy="18" r="6" fill="{BLUE}"/>',
         f'<g font-family="Consolas,\'DejaVu Sans Mono\',\'Courier New\',monospace" font-size="15" xml:space="preserve">',
         f'<text x="{W/2}" y="23" text-anchor="middle" fill="{DIM}" font-size="12">{esc(CARD["user"])}@{esc(CARD["host"])}: ~</text>']
    t = 0.3
    # prompt
    o.append(f'<g opacity="{1 if STATIC else 0}">{anim(t)}<text x="{PAD}" y="{TOP-22}" fill="{DIM}">$ </text>'
             f'<text x="{PAD+20}" y="{TOP-22}" fill="{INK}">neofetch</text></g>')
    t += 0.5
    # cabeçalho user@host + régua
    o.append(f'<g opacity="{1 if STATIC else 0}">{anim(t)}<text x="{PAD}" y="{TOP+8}" font-weight="bold">'
             f'<tspan fill="{BLUE}">{esc(CARD["user"])}</tspan><tspan fill="{DIM}">@</tspan>'
             f'<tspan fill="{RED}">{esc(CARD["host"])}</tspan></text></g>')
    o.append(f'<rect x="{PAD}" y="{TOP+14}" width="{len(CARD["user"])*9+9+len(CARD["host"])*9}" height="1" '
             f'fill="{DIM}" opacity="0.5"/>')
    for i, (k, v) in enumerate(CARD["lines"]):
        y = TOP + 8 + (i + 1) * LH + 6
        t += 0.22
        todo = v.startswith("TODO")
        o.append(f'<g opacity="{1 if STATIC else 0}">{anim(t)}'
                 f'<text x="{PAD}" y="{y}" fill="{BLUE}" font-weight="bold">{esc(k)}</text>'
                 f'<text x="{PAD+LABEL_W}" y="{y}" fill="{RED if todo else INK}">{esc(v)}</text></g>')
    # paleta de cores + cursor piscando
    y = TOP + 8 + (n + 1) * LH + 22
    t += 0.3
    sw = "".join(f'<rect x="{PAD + j*26}" y="{y-14}" width="22" height="14" fill="{c}"/>'
                 for j, c in enumerate([RED, "#d29922", "#3fb950", BLUE, "#a371f7", INK]))
    o.append(f'<g opacity="{1 if STATIC else 0}">{anim(t)}{sw}</g>')
    if not STATIC:
        o.append(f'<rect x="{PAD+176}" y="{y-14}" width="9" height="14" fill="{BLUE}" opacity="0">'
                 f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.01;0.5;0.51;1" '
                 f'begin="{t+0.4:.2f}s" dur="1s" repeatCount="indefinite"/></rect>')
    o.append("</g></svg>")
    return "\n".join(o)


if __name__ == "__main__":
    OUT.write_text(build(), encoding="utf-8")
    print("ok:", OUT)
