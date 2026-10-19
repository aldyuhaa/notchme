#!/usr/bin/env python3
"""Generate the NotchMe agents-status mascot frames.

Original artwork drawn in code with PIL (no third-party assets).
Outputs a single `var BUDDY_ART = {...};` JS line with base64 data-URL PNGs,
ready to splice into Extensions/agents-status/index.js (line `var BUDDY_ART`).

Usage:
    python3 generate_buddy_art.py [SIZE] > buddy_art.js.inc
    # then replace the BUDDY_ART line in index.js with the file contents.
    # SIZE defaults to 192. Hero renders at ~88pt, so keep SIZE >= 176
    # to avoid upscaling blur.
"""
import base64
import io
import json
import sys

from PIL import Image, ImageDraw

SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 192
SS = 2  # supersample factor for smooth edges

AGENTS = {
    "Claude": (235, 140, 89),
    "Codex": (102, 204, 140),
    "CodeBuddy": (89, 166, 255),
    "Muse": (191, 140, 255),
    "OpenCode": (255, 204, 77),
    "T3 Code": (140, 217, 255),
    "Mausbot": (255, 115, 153),
}

DARK = (25, 25, 30)
BLUSH = (255, 150, 160, 220)
WHITE = (255, 255, 255, 255)
RED = (200, 40, 40, 255)
GREEN = (46, 200, 110, 255)


def _shade(color, factor):
    return tuple(max(0, min(255, int(v * factor))) for v in color[:3])


def _draw_blob(d, cx, cy, r, body, bob=0):
    cy += bob
    # soft drop shadow
    d.ellipse([cx - r, cy + r * 0.82, cx + r, cy + r * 1.12], fill=(0, 0, 0, 60))
    # body
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=body + (255,))
    # belly highlight (top-left sheen)
    d.ellipse(
        [cx - r * 0.55, cy - r * 0.10, cx + r * 0.15, cy + r * 0.75],
        fill=_shade(body, 1.12) + (255,),
    )
    # blush cheeks
    d.ellipse([cx - r * 0.85, cy + r * 0.05, cx - r * 0.45, cy + r * 0.35], fill=BLUSH)
    d.ellipse([cx + r * 0.45, cy + r * 0.05, cx + r * 0.85, cy + r * 0.35], fill=BLUSH)
    return cy


def _glossy_eyes(d, cx, cy, r, blink=False):
    ex, ey, er = r * 0.38, -r * 0.15, r * 0.20
    for sx in (-1, 1):
        x0 = cx + sx * ex
        if blink:
            d.line(
                [x0 - er, cy + ey, x0 + er, cy + ey],
                fill=DARK + (255,),
                width=max(1, int(r * 0.12)),
            )
        else:
            d.ellipse([x0 - er, cy + ey - er, x0 + er, cy + ey + er], fill=DARK + (255,))
            d.ellipse(
                [x0 - er * 0.35, cy + ey - er * 0.45, x0 + er * 0.05, cy + ey - er * 0.05],
                fill=WHITE,
            )


def _smile(d, cx, cy, r):
    er = r * 0.20
    d.arc(
        [cx - er * 0.6, cy + r * 0.15 - er * 0.5, cx + er * 0.6, cy + r * 0.15 + er * 0.5],
        15,
        165,
        fill=DARK + (255,),
        width=max(1, int(r * 0.11)),
    )


def buddy(body, state, bob=0, blink=False):
    W = SIZE * SS
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy0, r = W // 2, W // 2, int(W * 0.36)
    cy = _draw_blob(d, cx, cy0, r, body, bob * SS)
    ex = r * 0.38
    if state == "idle":
        w = max(1, int(W * 0.03))
        for sx in (-1, 1):
            x0 = cx + sx * ex
            d.arc([x0 - 20, cy - 20, x0 + 20, cy + 20], 200, 340, fill=DARK + (255,), width=w)
        er = r * 0.20
        d.arc(
            [cx - er * 0.5, cy + r * 0.35 - er * 0.5, cx + er * 0.5, cy + r * 0.35 + er * 0.5],
            20,
            160,
            fill=DARK + (255,),
            width=max(1, int(W * 0.025)),
        )
    elif state == "error":
        er = r * 0.20
        o, w = er * 0.8, max(1, int(W * 0.03))
        for sx in (-1, 1):
            x0 = cx + sx * ex
            ey = cy - r * 0.15
            d.line([x0 - o, ey - o, x0 + o, ey + o], fill=RED, width=w)
            d.line([x0 - o, ey + o, x0 + o, ey - o], fill=RED, width=w)
        d.arc(
            [cx - er * 0.6, cy + r * 0.45 - er * 0.4, cx + er * 0.6, cy + r * 0.45 + er * 0.4],
            200,
            340,
            fill=DARK + (255,),
            width=max(1, int(W * 0.025)),
        )
    else:
        _glossy_eyes(d, cx, cy, r, blink=blink)
        if state == "waiting":
            er = r * 0.20
            d.ellipse(
                [cx - er * 0.45, cy + r * 0.30, cx + er * 0.45, cy + r * 0.62],
                fill=(120, 50, 55, 255),
            )
        else:
            _smile(d, cx, cy, r)
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def check_badge():
    W = SIZE * SS
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = W // 2, W // 2, int(W * 0.36)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    w = max(1, int(W * 0.09))
    d.line([cx - r * 0.45, cy + r * 0.02, cx - r * 0.08, cy + r * 0.38], fill=WHITE, width=w, joint="curve")
    d.line([cx - r * 0.08, cy + r * 0.38, cx + r * 0.5, cy - r * 0.35], fill=WHITE, width=w, joint="curve")
    return img.resize((SIZE, SIZE), Image.LANCZOS)


def data_url(img):
    # Flat cartoon art quantizes cleanly; keeps the inline JS small.
    img = img.quantize(colors=64, method=Image.FASTOCTREE).convert("RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def main():
    art = {}
    for name, color in AGENTS.items():
        art[name] = {
            "workingA": data_url(buddy(color, "working", 0, False)),
            "workingB": data_url(buddy(color, "working", -6, False)),
            "blink": data_url(buddy(color, "working", 0, True)),
            "waiting": data_url(buddy(color, "waiting")),
            "idle": data_url(buddy(color, "idle")),
            "error": data_url(buddy(color, "error")),
        }
    art["__done"] = data_url(check_badge())
    art["__offline"] = data_url(buddy((90, 90, 96), "idle"))
    sys.stdout.write("var BUDDY_ART = " + json.dumps(art, separators=(",", ":")) + ";")


if __name__ == "__main__":
    main()
