#!/usr/bin/env python3
"""Build colour tokens from one brand hue, a scene and a colour strategy, and check contrast (rule:palette-script).

  python3 palette.py --brand "#2F6B4F" --scene light --strategy restrained
  python3 palette.py --brand "#C2410C" --scene dark  --strategy committed
  python3 palette.py --brand "#1D6B8F" --scene light --strategy full          # adds --role-2 .. --role-4
  python3 palette.py --brand "#B4236B" --scene light --strategy drenched --ground "#E5487F"
  python3 palette.py --check "#6B665C" "#F7F4EE"                              # contrast of fg on bg

Rules it enforces (OKLCH):
  ink >= 7:1 and muted >= 4.5:1 on --bg and --surface; primary chroma <= 0.23 (<= 0.18 when L > 0.78);
  no muddy fills (L 0.45-0.72 with C < 0.10, rule:no-muddy); light grounds always carry a hue cast;
  committed and drenched colour is frame-only (rule:frame-ground): body text, cards, forms and charts sit on --surface.
It warns when a choice lands in a measured attractor (rule:attractor-warnings). Pick another hue from the direction.
"""
import argparse, math, sys

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
def rgb_to_hex(rgb): return "#" + "".join(f"{round(max(0, min(1, c)) * 255):02X}" for c in rgb)
def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def delin(c): return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
def rgb_to_oklch(rgb):
    r, g, b = (lin(c) for c in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360
def oklch_to_rgb(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
def in_gamut(rgb): return all(-0.0005 <= c <= 1.0005 for c in rgb)
def ok(L, C, H):
    while C > 0 and not in_gamut(oklch_to_rgb(L, C, H)): C -= 0.002
    return rgb_to_hex(tuple(delin(max(0, min(1, c))) for c in oklch_to_rgb(L, max(C, 0), H)))
def lch(hexc): return rgb_to_oklch(hex_to_rgb(hexc))
def lum(hexc):
    r, g, b = (lin(c) for c in hex_to_rgb(hexc)); return 0.2126 * r + 0.7152 * g + 0.0722 * b
def contrast(a, b):
    x, y = lum(a), lum(b); return (max(x, y) + 0.05) / (min(x, y) + 0.05)
def on(c): return "#FFFFFF" if contrast("#FFFFFF", c) >= contrast("#111111", c) else "#111111"
def demud(L, C, H=None):
    """rule:no-muddy - a mid-lightness fill needs real chroma; yellows only read as yellow when light (else olive)."""
    if H is not None and 70 <= H <= 115 and L < 0.80: return 0.86, min(max(C, 0.14), 0.18)
    return (L, max(C, 0.12)) if 0.45 <= L <= 0.72 and C < 0.10 else (L, C)
def cap(L, C): return min(C, 0.18 if L > 0.78 else 0.23)
def ink_for(grounds, H, dark_scene, target):
    """Darkest/lightest text in the ground's hue that reaches the target contrast."""
    # the lightest dark ink (or darkest light ink) that still reaches the target: tinted, not pure black
    seq = [i / 100 for i in range(42, 9, -1)] if not dark_scene else [i / 100 for i in range(72, 100)]
    for L in seq:
        c = ok(L, 0.025, H)
        if min(contrast(c, g) for g in grounds) >= target: return c
    return "#0B0B0B" if not dark_scene else "#FAFAFA"
def muted_for(grounds, H, dark_scene):
    seq = [i / 100 for i in range(55, 15, -1)] if not dark_scene else [i / 100 for i in range(55, 96)]
    for L in seq:
        c = ok(L, 0.03, H)
        if min(contrast(c, g) for g in grounds) >= 4.5: return c
    return ink_for(grounds, H, dark_scene, 4.5)

SCENE = {  # bg L, bg C, surface L, surface C
    "white": (0.995, 0.0, 0.975, 0.003),   # rule:neutral-grounds (V4.1): no hue cast, neutral hairline
    "light": (0.965, 0.022, 0.990, 0.008),
    "mid":   (0.80,  0.060, 0.975, 0.012),
    "dark":  (0.23,  0.035, 0.28,  0.035),
    "black": (0.16,  0.0,   0.21,  0.004),  # rule:neutral-grounds: near-black, near-white text
    "deep":  (0.27,  0.065, 0.32,  0.060),  # deep navy, forest or plum ground in the --ground (or brand) hue
}
NEUTRAL = ("white", "black")
DARKS = ("dark", "black", "deep")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand"); ap.add_argument("--scene", choices=list(SCENE), default="light")
    ap.add_argument("--strategy", choices=["restrained", "committed", "full", "drenched"], default="restrained")
    ap.add_argument("--ground", help="hex whose hue (and, for drenched, colour) sets the ground; default: brand")
    ap.add_argument("--check", nargs=2, metavar=("FG", "BG"))
    a = ap.parse_args()
    if a.check:
        r = contrast(*a.check); print(f"{a.check[0]} on {a.check[1]}: {r:.2f}:1  " + ("ok for body text" if r >= 4.5 else "large text / UI only" if r >= 3 else "FAIL")); return
    if not a.brand: sys.exit("need --brand or --check")
    L0, C0, H = lch(a.brand); gL0, gC0, gH = lch(a.ground) if a.ground else (L0, C0, H)
    bL, bC, sL, sC = SCENE[a.scene]; dark = a.scene in DARKS; neutral = a.scene in NEUTRAL
    notes, warns = [], []
    bg, surf = ok(bL, bC, gH), ok(sL, sC, gH)
    v = {}
    if a.strategy == "drenched":
        gl, gc = demud(*((gL0, max(gC0, 0.12)) if a.ground else (0.62, max(C0, 0.14))), gH)
        ground = ok(gl, cap(gl, gc), gH); v["--ground"] = ground; v["--on-ground"] = on(ground)
        bg = ground; surf = ok(0.985, 0.010, gH); notes.append("drenched: --bg is the coloured ground for header, hero, bands and footer; body text, cards, forms and charts sit on --surface.")
    text_bg = surf if a.strategy == "drenched" else bg
    v["--bg"], v["--surface"] = bg, surf
    grounds = [surf] if a.strategy == "drenched" else [bg, surf]
    v["--text"] = ink_for(grounds, gH, dark, 7.0)          # rule:ink-7
    v["--text-muted"] = muted_for(grounds, gH, dark)
    v["--border"] = ok((sL - 0.12) if not dark else (sL + 0.10), 0.03, gH)
    if neutral:   # near-black / near-white text and a neutral hairline: no hue cast at all
        v["--text"] = "#111111" if not dark else "#F5F5F4"; v["--text-muted"] = "#55554F" if not dark else "#B4B4AE"
        v["--border"] = "#E4E4E1" if not dark else "#34342F"
    # primary: brand hue at the lightness closest to the brand that reads >= 4.5 on the text ground
    cands = []
    for L in [i / 100 for i in range(18, 94, 3)]:
        Lc, Cc = demud(L, cap(L, max(C0, 0.06))); c = ok(Lc, Cc, H)
        if min(contrast(c, g) for g in grounds) >= 4.5: cands.append((abs(Lc - L0), c))
    primary = min(cands)[1] if cands else ok(0.4 if not dark else 0.8, cap(0.5, C0), H)
    v["--primary"], v["--on-primary"] = primary, on(primary)
    if a.strategy in ("committed", "full"):
        fL = 0.46 if not dark else 0.66; fL, fC = demud(fL, cap(fL, max(C0, 0.14)), H)
        v["--field"] = ok(fL, fC, H); v["--on-field"] = on(v["--field"])
        notes.append("committed: --field carries 30-60% of the first screen (a rail, header band or hero block); content still sits on --surface.")
    if a.strategy == "full":
        for i, dh in enumerate((95, 185, 275), 2):
            rh = (H + dh) % 360; rl, rc = demud(0.55 if not dark else 0.72, 0.13, rh); c = ok(rl, rc, rh)
            v[f"--role-{i}"] = c; v[f"--on-role-{i}"] = on(c)
        notes.append("full: give each --role-N one job (a category, a state or a section) and name it in a comment.")
    v["--danger"] = ok(0.52 if not dark else 0.72, 0.17, 27); v["--success"] = ok(0.52 if not dark else 0.74, 0.14, 150)
    # attractor warnings (rule:attractor-warnings)
    pL, pC, pH = lch(primary); bgL, bgC, bgH = lch(bg)
    if a.scene == "mid" and 55 <= bgH <= 115 and a.strategy != "drenched": warns.append("khaki / mustard mid-tone ground reads murky (round 6-7 judges). Use a light or dark scene, or a ground hue from elsewhere in the direction.")
    if not dark and not neutral and bgL > 0.9 and 50 <= bgH <= 110: warns.append("cream / warm-paper ground (default look 1). Take the ground hue from elsewhere in the direction (--ground), unless the brief asks for paper.")
    if not dark and not neutral and bgL > 0.9 and 195 <= bgH <= 265 and a.strategy == "restrained": warns.append("pale blue-grey ground with one accent is the neutral app shell (default look 4). Use committed colour, a different ground hue, or a dark scene.")
    if 250 <= pH <= 278 and pC >= 0.09 and a.strategy == "restrained" and not dark: warns.append("cobalt / navy primary is the third-generation default (poster headline era). Take the hue from the direction's own inks or materials.")
    if 280 <= pH <= 320 and pC >= 0.12: warns.append("violet primary is the classic AI palette. Use it only if the direction's material is violet.")
    if not dark and not neutral and 135 <= pH <= 175 and 50 <= bgH <= 110 and bgL > 0.9: warns.append("forest green on cream is a known attractor. Move the ground or the primary.")
    print(":root{"); [print(f"  {k}: {c};") for k, c in v.items()]; print("}")
    pairs = [("--text", "--surface"), ("--text-muted", "--surface"), ("--on-primary", "--primary"), ("--primary", "--surface")]
    if a.strategy != "drenched": pairs = [("--text", "--bg")] + pairs + [("--text-muted", "--bg"), ("--primary", "--bg")]
    for k in ("--ground", "--field", "--role-2", "--role-3", "--role-4"):
        if k in v: pairs.append(("--on-" + k[2:], k))
    print("/* contrast:")
    for f, b in pairs:
        r = contrast(v[f], v[b]); print(f"   {f} on {b}: {r:.2f}  " + ("ok" if r >= 4.5 else "large text / UI only" if r >= 3 else "FAIL"))
    print("*/")
    if a.strategy != "drenched" and not neutral: notes.insert(0, "page background = --bg (tinted). --surface is only for cards, panels and inputs; never use it as the page background.")
    if neutral: notes.insert(0, "page background = --bg (pure white or near-black). Colour lives in content, the primary action and at most one field.")
    for n in notes: print(f"/* {n} */")
    for w in warns: print(f"/* WARNING: {w} */")

if __name__ == "__main__":
    main()
