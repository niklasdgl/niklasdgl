"""Generate the animated terminal header (dark + light) for the GitHub profile README.

Mirrors the `niklas@portfolio` terminal on niklasdgl.github.io: three screens
(about / skills / now): command typed out, output, then a HOLD_SECONDS pause.
Pure SVG + SMIL, so it animates inside GitHub's <img> sandbox (no JS, no web fonts).

Run:  python3 scripts/make_header.py   (writes assets/header-dark.svg, assets/header-light.svg)
"""
from pathlib import Path
from xml.sax.saxutils import escape

SCREENS = [
    ("cat ~/about.txt", ["Into maths, physics and machine learning.",
                         "Simulation-based inference for chaotic systems."]),
    ("cat ~/skills.txt", ["Python, C++, C#, C, Java, Julia, SQL, R.",
                          "Git, Docker, Linux."]),
    ("cat ~/now.txt", ["Based in London.",
                       "Research assistant at Goethe University.",
                       "Olympiad trainer and mentor."]),
]

THEMES = {
    "dark": dict(bg="#0a0a0a", panel="#0f0f0f", line="#2a2a2a", ink="#e5e5e5",
                 dim="#7a7a7a", ok="#34d399", tilde="#a0a0a0",
                 dot="#5a5a5a"),
    "light": dict(bg="#ffffff", panel="#fafafa", line="#e5e5e5", ink="#171717",
                  dim="#8a8a8a", ok="#059669", tilde="#6b6b6b",
                  dot="#b5b5b5"),
}

WIDTH, HEIGHT = 760, 236
FOOT_H = 36
BAR_H = 38
PAD_X = 28
FONT = 17
CHAR_W = FONT * 0.602          # monospace advance width
LINE_H = 29
TYPE_SECONDS = 1.1
HOLD_SECONDS = 4          # same pause as the portfolio site (HOLD_MS = 4000)
SCREEN_SECONDS = TYPE_SECONDS + 0.9 + HOLD_SECONDS
MONO = "ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def frac(seconds: float, total: float) -> str:
    return f"{seconds / total:.4f}"


def screen_group(i: int, cmd: str, lines: list[str], t: dict) -> str:
    total = SCREEN_SECONDS * len(SCREENS)
    start, end = i * SCREEN_SECONDS, (i + 1) * SCREEN_SECONDS
    y0 = BAR_H + 38

    # visibility of the whole screen (discrete on/off inside the 30 s cycle)
    if i == 0:
        vis = f'values="1;0" keyTimes="0;{frac(end, total)}"'
    else:
        vis = f'values="0;1;0" keyTimes="0;{frac(start, total)};{frac(end, total)}"'
    if end == total and i != 0:
        vis = f'values="0;1" keyTimes="0;{frac(start, total)}"'

    prompt_x = PAD_X + 2 * CHAR_W * 2       # after "→ ~ "
    cmd_w = len(cmd) * CHAR_W + 4
    typed = start + TYPE_SECONDS
    shown = typed + 0.25
    clip_id = f"type{i}"
    type_anim = (f'values="0;0;{cmd_w:.1f};{cmd_w:.1f}" '
                 f'keyTimes="0;{frac(start, total)};{frac(typed, total)};1"')
    out_anim = f'values="0;1" keyTimes="0;{frac(shown, total)}"'

    out = [f'<g opacity="0"><animate attributeName="opacity" dur="{total}s" '
           f'repeatCount="indefinite" calcMode="discrete" {vis}/>',
           f'<clipPath id="{clip_id}"><rect x="{prompt_x - 2:.1f}" y="{y0 - 18}" width="0" height="26">'
           f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" {type_anim}/>'
           f'</rect></clipPath>',
           f'<text x="{PAD_X}" y="{y0}" fill="{t["ok"]}">→</text>',
           f'<text x="{PAD_X + 2 * CHAR_W:.1f}" y="{y0}" fill="{t["tilde"]}">~</text>',
           f'<text x="{prompt_x:.1f}" y="{y0}" fill="{t["ink"]}" clip-path="url(#{clip_id})">{escape(cmd)}</text>',
           f'<g opacity="0"><animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" '
           f'calcMode="discrete" {out_anim}/>']
    for k, line in enumerate(lines):
        out.append(f'<text x="{PAD_X}" y="{y0 + (k + 1) * LINE_H + 4}" fill="{t["ink"]}">{escape(line)}</text>')
    cy = y0 + len(lines) * LINE_H + 4
    cx = PAD_X + len(lines[-1]) * CHAR_W + 3
    out.append(f'<rect x="{cx:.1f}" y="{cy - 14}" width="{CHAR_W * 0.55:.1f}" height="18" fill="{t["ink"]}">'
               '<animate attributeName="opacity" values="1;0" dur="1.1s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    out.append('</g></g>')
    return "\n".join(out)


def build(t: dict) -> str:
    y_bar = BAR_H / 2
    dots = "".join(f'<circle cx="{PAD_X + 6 + k * 20}" cy="{y_bar}" r="6" fill="none" stroke="{t["dot"]}" stroke-width="1.3"/>'
                   for k in range(3))
    foot_top = HEIGHT - FOOT_H
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="niklas@portfolio terminal: maths, physics and machine learning; simulation-based inference for chaotic systems">
<style>text {{ font-family: {MONO}; font-size: {FONT}px; white-space: pre; }}
.small {{ font-size: 12px; }}</style>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" fill="{t["panel"]}" stroke="{t["line"]}"/>
<path d="M0.5 {BAR_H} H{WIDTH - 0.5} M0.5 {foot_top} H{WIDTH - 0.5}" stroke="{t["line"]}"/>
{dots}
<text x="{WIDTH / 2}" y="{y_bar + 4.5}" text-anchor="middle" class="small" fill="{t["dim"]}">niklas@portfolio: ~</text>
<text x="{WIDTH - PAD_X}" y="{y_bar + 4.5}" text-anchor="end" class="small" fill="{t["dim"]}">v1.0</text>
{"".join(screen_group(i, c, ls, t) for i, (c, ls) in enumerate(SCREENS))}
<text x="{PAD_X}" y="{foot_top + FOOT_H / 2 + 4.5}" class="small" fill="{t["dim"]}">// exit code 0 · ttys000 · zsh</text>
</svg>
"""


def main() -> None:
    out_dir = Path(__file__).resolve().parent.parent / "assets"
    out_dir.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        (out_dir / f"header-{name}.svg").write_text(build(theme), encoding="utf-8")
        print("wrote", out_dir / f"header-{name}.svg")


if __name__ == "__main__":
    main()
