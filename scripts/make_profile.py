"""Generate the profile banners from assets/portrait-source.png.

Run: python scripts/make_profile.py (requires Pillow and NumPy).
Use --static --output-dir PATH for a still preview. Update the rows below
when skills change; replace the source PNG to update the portrait.
"""
import argparse
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PARTICLES = 900
ROWS = [
    ("Name", "Akash S"),
    ("Role", "AI Engineer"),
    ("Based", "Bengaluru, India"),
    ("Focus", "RAG · AI agents · Speech"),
    ("Models", "Whisper · LoRA · Transformers"),
    ("AI stack", "LangChain · LangGraph · ChromaDB"),
    ("Backend", "Python · FastAPI · PostgreSQL"),
    ("Frontend", "TypeScript · React · Next.js"),
    ("Delivery", "Docker · Azure · Vercel"),
]
THEMES = {
    "dark": ("#0b1220", "#111c2e", "#17253a", "#2b3d55", "#91a5bf", "#e4edf8", "#7ec9ed", "#b7a8e8"),
    "light": ("#f5f7fb", "#ffffff", "#edf2f8", "#d5dfeb", "#526780", "#1c304b", "#176488", "#6e549d"),
}


def points(image, count, rng):
    pixels = np.asarray(image.convert("L")) < 128
    y, x = np.where(pixels)
    if len(x) < count:
        raise ValueError("Portrait or symbol has too few visible points")
    chosen = rng.choice(len(x), count, replace=False)
    return np.column_stack((x[chosen], y[chosen])).astype(float)


def match(source, target):
    """Assign each particle a nearby, unique destination without new libraries."""
    available = target.copy()
    assigned = np.empty_like(source)
    for i, origin in enumerate(source):
        nearest = np.argmin(np.sum((available - origin) ** 2, axis=1))
        assigned[i] = available[nearest]
        available[nearest] = np.inf
    return assigned


def dot_path(coords):
    return "".join(f"M{int(x) + 56},{int(y) + 164}h.1" for x, y in coords)


def symbol(kind):
    image = Image.new("L", (320, 320), 255)
    draw = ImageDraw.Draw(image)
    if kind == "network":
        columns = [[(65, y) for y in (80, 160, 240)], [(160, y) for y in (55, 125, 195, 265)], [(255, y) for y in (100, 220)]]
        for left, right in zip(columns, columns[1:]):
            for a in left:
                for b in right:
                    draw.line((a, b), fill=0, width=3)
        for column in columns:
            for x, y in column:
                draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=0)
    elif kind == "document":
        draw.rounded_rectangle((80, 38, 238, 278), radius=14, outline=0, width=8)
        for y, end in ((90, 205), (122, 205), (154, 175)):
            draw.line((110, y, end, y), fill=0, width=7)
        draw.ellipse((139, 180, 200, 241), outline=0, width=7)
        draw.line((194, 235, 224, 265), fill=0, width=8)
    else:
        draw.line(((112, 90), (42, 160), (112, 230)), fill=0, width=10)
        draw.line(((208, 90), (278, 160), (208, 230)), fill=0, width=10)
        draw.line((184, 65, 138, 255), fill=0, width=10)
    return image


def render(theme, portrait, frames, static):
    bg, panel, inset, line, muted, text, cyan, violet = THEMES[theme]
    output = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="640" viewBox="0 0 1200 640" role="img" aria-labelledby="title desc">',
        '<title id="title">Akash S | AI Engineer</title>',
        '<desc id="desc">Akash\'s portrait transforms into a neural network, a document search symbol, and code. Skills include RAG, AI agents, speech models, Python, FastAPI, React, and Next.js.</desc>',
        '<style>.still{display:none}@media(prefers-reduced-motion:reduce){.motion{display:none}.still{display:inline}}</style>',
        f'<rect x="1" y="1" width="1198" height="638" rx="18" fill="{bg}" stroke="{line}"/>',
        f'<rect x="16" y="16" width="1168" height="608" rx="12" fill="{panel}"/>',
        f'<path d="M16 62h1168" stroke="{line}"/>',
    ]
    for i, color in enumerate(("#ee8e87", "#e7be78", "#7cb9a3")):
        output.append(f'<circle cx="{38 + i * 18}" cy="39" r="5" fill="{color}"/>')
    output.append(f'<text x="600" y="44" text-anchor="middle" fill="{muted}" font-family="Menlo,Consolas,monospace" font-size="15">akash@github:~$ profile --ai</text>')
    output.append(f'<rect x="32" y="84" width="368" height="478" rx="9" fill="{inset}" stroke="{line}"/>')
    output.append(f'<rect x="420" y="84" width="748" height="478" rx="9" fill="{inset}" stroke="{line}"/>')
    output.append(f'<g font-family="Menlo,Consolas,monospace" font-size="13" letter-spacing="1.2" fill="{cyan}"><text x="52" y="112">PORTRAIT / AI IN MOTION</text><text x="442" y="112">PROFILE / ENGINEERING</text></g>')
    output.append(f'<text x="1146" y="112" text-anchor="end" fill="{violet}" font-family="Menlo,Consolas,monospace" font-size="13">@Akash-62</text>')
    path = dot_path(portrait)
    output.append(f'<defs><path id="portrait" d="{path}" fill="none" stroke="{cyan}" stroke-width="1.1" stroke-linecap="round"/></defs>')
    still = '<use href="#portrait"/>'
    output.append(still if static else f'<g class="still">{still}</g>')
    if not static:
        times = "0;.25;.32;.44;.51;.63;.70;.82;.89;1"
        output.append(f'<g class="motion"><g opacity="1">{still}<animate attributeName="opacity" values="1;1;0;0;0;0;0;0;1;1" keyTimes="{times}" dur="18s" repeatCount="indefinite"/></g>')
        for i in range(len(frames[0])):
            coords = [frame[i] for frame in frames]
            positions = [coords[0], coords[0], coords[1], coords[1], coords[2], coords[2], coords[3], coords[3], coords[0], coords[0]]
            values = ";".join(f"{x + 56:.1f} {y + 164:.1f}" for x, y in positions)
            output.append(f'<circle r=".9" fill="{violet}" opacity="0"><animateTransform attributeName="transform" type="translate" values="{values}" keyTimes="{times}" dur="18s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0;1;1;1;1;1;1;0;0" keyTimes="{times}" dur="18s" repeatCount="indefinite"/></circle>')
        output.append('</g>')
    output.append(f'<path d="M52 140h328M442 140h704M442 521h704" stroke="{line}"/>')
    for i, (key, value) in enumerate(ROWS):
        y = 178 + i * 38
        output.append(f'<g font-family="Menlo,Consolas,monospace"><text x="444" y="{y}" fill="{muted}" font-size="17">{escape(key)}</text><text x="1144" y="{y}" text-anchor="end" fill="{text}" font-size="20">{escape(value)}</text></g>')
    output.append(f'<text x="216" y="542" text-anchor="middle" fill="{muted}" font-family="Menlo,Consolas,monospace" font-size="12">PORTRAIT → MODELS → PRODUCTS</text>')
    output.append(f'<circle cx="448" cy="542" r="3" fill="{cyan}"/><text x="460" y="546" fill="{muted}" font-family="Menlo,Consolas,monospace" font-size="12">DOCUMENT INTELLIGENCE · SPEECH · AI PRODUCTS</text>')
    output.append(f'<text x="48" y="604" fill="{text}" font-family="Arial,sans-serif" font-size="24">Building AI that works for people.</text><text x="1150" y="604" text-anchor="end" fill="{muted}" font-family="Menlo,Consolas,monospace" font-size="14">Learning fast, building faster.</text></svg>')
    svg = "\n".join(output) + "\n"
    root = ET.fromstring(svg)
    ns = {"s": "http://www.w3.org/2000/svg"}
    assert not root.findall(".//s:script", ns)
    assert not root.findall(".//s:image", ns)
    for animation in root.findall(".//s:animate", ns) + root.findall(".//s:animateTransform", ns):
        assert len(animation.attrib["values"].split(";")) == len(animation.attrib["keyTimes"].split(";"))
    return svg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets")
    args = parser.parse_args()
    image = Image.open(ROOT / "assets/portrait-source.png").convert("L")
    image = ImageOps.contain(image, (300, 300), Image.Resampling.LANCZOS)
    canvas = Image.new("L", (320, 320), 255)
    canvas.paste(image, ((320 - image.width) // 2, (320 - image.height) // 2))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        rng = np.random.default_rng(62)
        sample = canvas
        if theme == "dark":
            luminance = np.asarray(canvas)
            sample = Image.fromarray(np.where(luminance < 250, 255 - luminance, 255).astype("uint8"))
        dither = sample.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
        y, x = np.where(np.asarray(dither) == 0)
        portrait = np.column_stack((x, y)).astype(float)
        frames = [points(dither, PARTICLES, rng)]
        for kind in ("network", "document", "code"):
            frames.append(match(frames[-1], points(symbol(kind), PARTICLES, rng)))
        target = args.output_dir / f"profile-{theme}.svg"
        target.write_text(render(theme, portrait, frames, args.static), encoding="utf-8")
        print(f"Generated {target}: {target.stat().st_size:,} bytes")
