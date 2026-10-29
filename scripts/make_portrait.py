"""Render a photo as a cyan ASCII scan. Requires Pillow.

Usage: python scripts/make_portrait.py photo.png assets/portrait.svg
Pass --static to inspect the completed portrait without animation.
"""
import argparse
from html import escape
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("photo", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--static", action="store_true")
args = parser.parse_args()

cols, rows = 144, 90
width, cell_h, padding, top = 576, 6.4, 20, 50
duration = 5.4
image = Image.open(args.photo).convert("L").resize((cols, rows), Image.Resampling.LANCZOS)
image = ImageEnhance.Contrast(ImageOps.autocontrast(image, cutoff=1)).enhance(1.1)
ramp = " .:-=+*#%@"
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="616" height="672" viewBox="0 0 616 672" role="img" aria-labelledby="title desc">',
    '<title id="title">Akash S, cyan ASCII portrait</title>',
    '<desc id="desc">Akash\'s GitHub photo reveals row by row in cyan, then stays visible.</desc>',
    '<style>@media(prefers-reduced-motion:reduce){.row-clip{width:576px!important}.scan{display:none}}</style>',
    '<rect x=".5" y=".5" width="615" height="671" rx="12" fill="#0d1117" stroke="#30363d"/>',
    '<path d="M0 34h616M0 636h616" stroke="#30363d"/>',
    '<g fill="#7ec9ed"><circle cx="20" cy="17" r="4"/><circle cx="36" cy="17" r="4" opacity=".6"/><circle cx="52" cy="17" r="4" opacity=".3"/></g>',
    '<g font-family="ui-monospace, Menlo, Consolas, monospace" fill="#8b949e" font-size="12">',
    '<text x="80" y="21">akash@github:~$ ./portrait</text>',
    '<text x="20" y="658">whoami <tspan fill="#7ec9ed">Akash S</tspan></text></g>',
]
for row in range(rows):
    line = "".join(ramp[round((1 - (image.getpixel((col, row)) / 255) ** 0.8) * (len(ramp) - 1))] for col in range(cols))
    y = top + row * cell_h
    text = f'<text x="{padding}" y="{y + 5.5:.1f}" xml:space="preserve" font-family="Menlo,Consolas,monospace" font-size="6.4" fill="#7ec9ed" textLength="{width}" lengthAdjust="spacingAndGlyphs">{escape(line)}</text>'
    if args.static:
        parts.append(text)
    else:
        begin = 0.5 + row * duration / rows
        parts.append(f'<clipPath id="row{row}"><rect class="row-clip" x="{padding}" y="{y:.1f}" width="0" height="{cell_h}"><animate attributeName="width" from="0" to="{width}" begin="{begin:.2f}s" dur="{duration / rows:.2f}s" fill="freeze"/></rect></clipPath>')
        parts.append(f'<g clip-path="url(#row{row})">{text}</g>')
if not args.static:
    parts.append(f'<rect class="scan" x="20" y="{top}" width="{width}" height="1.5" fill="#a5edff" opacity="0"><set attributeName="opacity" to=".7" begin=".5s"/><animate attributeName="y" from="{top}" to="{top + rows * cell_h}" begin=".5s" dur="{duration}s" fill="freeze"/><set attributeName="opacity" to="0" begin="5.9s"/></rect>')
parts.append("</svg>")
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text("\n".join(parts) + "\n", encoding="utf-8")
print(f"Wrote {args.output} ({args.output.stat().st_size:,} bytes)")
