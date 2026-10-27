"""Prepara a foto para virar ASCII: escala de cinza, CLAHE, normalização e gama.
Uso: python scripts/prep_photo.py [entrada] [saida]
Sem baixar nada além do avatar público (rembg é opcional e não é usado)."""
import sys
from pathlib import Path

import cv2
import numpy as np
import requests

ROOT = Path(__file__).resolve().parent.parent
AVATAR_URL = "https://github.com/felipeJJD.png?size=460"


def prep(src: Path, dst: Path, gamma: float = 0.8):
    if not src.exists():
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_bytes(requests.get(AVATAR_URL, timeout=30).content)
    img = cv2.imread(str(src), cv2.IMREAD_COLOR)
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    g = cv2.GaussianBlur(g, (0, 0), 2.0)                      # tira o grão do metal
    g = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4)).apply(g)
    lo, hi = np.percentile(g, (3, 99.5))                       # estica o contraste
    g = np.clip((g.astype(np.float32) - lo) / max(hi - lo, 1), 0, 1) ** (1 / gamma)
    # fundo quase preto vira vazio (sem "poeira" de caracteres)
    g = np.clip((g - 0.35) / 0.4, 0, 1)                        # corta fundo/grão, realça o relevo
    ys, xs = np.where(g > 0.05)                                # recorta a margem vazia
    m = 14
    y0, y1, x0, x1 = max(ys.min() - m, 0), ys.max() + m, max(xs.min() - m, 0), xs.max() + m
    g = g[y0:y1, x0:x1]
    cv2.imwrite(str(dst), (g * 255).astype(np.uint8))
    return dst


if __name__ == "__main__":
    s = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets" / "avatar.png"
    d = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "assets" / "avatar_prepped.png"
    print("ok:", prep(s, d))
