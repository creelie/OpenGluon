"""Generate Anaxia's original README artwork (Pillow; no network requests)."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'docs' / 'assets'
WIDTH, HEIGHT = 1400, 560
BG, PANEL = '#fffdf7', '#eff6ff'
TEAL, AMBER, WHITE, MUTED = '#087f6b', '#bc4b3e', '#15394a', '#536b79'


def font(size, bold=False, mono=False):
    names = ['consolab.ttf' if bold else 'consola.ttf'] if mono else ['segoeuib.ttf' if bold else 'segoeui.ttf']
    names += ['DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf']
    for name in names:
        for path in (Path('C:/Windows/Fonts') / name, Path('/usr/share/fonts/truetype/dejavu') / name):
            if path.exists():
                return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


def ellipse_point(cx, cy, rx, ry, angle, rotation=0):
    x, y = rx * math.cos(angle), ry * math.sin(angle)
    return (cx + x * math.cos(rotation) - y * math.sin(rotation),
            cy + x * math.sin(rotation) + y * math.cos(rotation))


def draw_frame(phase):
    im = Image.new('RGB', (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(im)
    # Quiet coordinate grid: visual context without competing with the type.
    for x in range(780, WIDTH, 36):
        for y in range(30, 420, 36):
            d.ellipse((x, y, x + 1, y + 1), fill='#cfdfe7')
    d.rounded_rectangle((1, 1, WIDTH - 2, HEIGHT - 2), 22, outline='#cbdedc', width=2)
    d.rounded_rectangle((56, 43, 90, 77), 9, fill=TEAL)
    d.line([(63, 68), (73, 51), (83, 68)], fill=BG, width=3)
    d.line([(68, 63), (78, 63)], fill=BG, width=2)
    d.text((106, 46), 'A LIVING MATHEMATICS LAB', fill=MUTED, font=font(18, bold=True))
    d.text((52, 93), 'ANAXIA', fill=WHITE, font=font(94, bold=True))
    d.text((57, 216), 'Explore boldly. Verify exactly.', fill=TEAL, font=font(33))
    d.text((58, 279), 'Open research. Local models. Exact certificates.', fill=WHITE, font=font(23))
    d.text((58, 314), 'A research loop built for checkable mathematics.', fill=MUTED, font=font(22))
    d.rounded_rectangle((58, 372, 257, 407), 17, fill='#e0f3e9', outline='#b0d8c4')
    d.text((73, 378), 'LOCAL + CLOUD MODELS', fill=TEAL, font=font(13, bold=True))
    d.text((278, 379), 'SOURCE-LINKED  /  OPEN RESEARCH', fill=MUTED, font=font(13, mono=True))

    cx, cy = 1098, 225
    for radius in (143, 169, 195):
        d.ellipse((cx-radius, cy-radius, cx+radius, cy+radius), outline='#d7e5ec', width=1)
    for i, rotation in enumerate((0, math.pi/3, -math.pi/3)):
        points = [ellipse_point(cx, cy, 183, 73, n * math.tau / 240, rotation) for n in range(241)]
        d.line(points, fill=('#6caaa0', '#9aaecf', '#cf9a8f')[i], width=2)
        pos = ellipse_point(cx, cy, 183, 73, phase * math.tau + i * 2.09, rotation)
        d.ellipse((pos[0]-12, pos[1]-12, pos[0]+12, pos[1]+12), fill='#d9eee7')
        d.ellipse((pos[0]-5, pos[1]-5, pos[0]+5, pos[1]+5), fill=TEAL if i != 1 else AMBER)
    d.ellipse((cx-56, cy-56, cx+56, cy+56), fill=PANEL, outline='#a3c8c0', width=2)
    d.text((cx-25, cy-43), 'A', fill=WHITE, font=font(59, bold=True))
    d.text((917, 413), 'HYPOTHESIS', fill=MUTED, font=font(12, mono=True))
    d.line((1010, 422, 1176, 422), fill='#9cb7c0', width=1)
    d.text((1194, 413), 'CERTIFICATE', fill=TEAL, font=font(12, mono=True))
    d.text((937, 28), 'p(x) = Σ wᵢ qᵢ(x)²', fill=MUTED, font=font(20, mono=True))
    d.text((1298, 266), 'wᵢ ≥ 0', fill=AMBER, font=font(15, mono=True))
    d.text((911, 356), 'A = L D Lᵀ', fill=MUTED, font=font(16, mono=True))

    d.line((56, 453, 1344, 453), fill='#cbdedc', width=1)
    labels = ['DISCOVER', 'FORMALIZE', 'PROPOSE', 'CRITIQUE', 'VERIFY']
    active = int(phase * len(labels)) % len(labels)
    for i, label in enumerate(labels):
        x = 58 + i * 263
        color = TEAL if i == active else MUTED
        d.text((x, 484), f'0{i+1}', fill=AMBER if i == active else '#697d86', font=font(16, mono=True))
        d.text((x+38, 481), label, fill=color, font=font(18, bold=True))
        if i < 4:
            d.line((x+192, 494, x+225, 494), fill='#9cafb7', width=1)
            d.line((x+221, 490, x+225, 494, x+221, 498), fill='#9cafb7', width=1)
    return im


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    frames = [draw_frame(i / 60) for i in range(60)]
    frames[0].save(ASSETS / 'anaxia-hero.png', optimize=True)
    # Shared palette prevents flashing/dithering shifts between frames.
    palette = frames[0].quantize(colors=128)
    animated = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    animated[0].save(ASSETS / 'anaxia-hero.gif', save_all=True, append_images=animated[1:],
                     duration=80, loop=0, optimize=True, disposal=1)
    # A scalable, static companion that uses the same composition.
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="560" viewBox="0 0 1400 560" role="img" aria-labelledby="title desc">
<title id="title">Anaxia — Explore boldly. Verify exactly.</title>
<desc id="desc">A mathematical orbit connects discover, formalize, explore, critique and verify.</desc>
<rect x="1" y="1" width="1398" height="558" rx="22" fill="#fffdf7" stroke="#cbdedc" stroke-width="2"/>
<g font-family="Segoe UI,Arial,sans-serif">
<rect x="56" y="43" width="34" height="34" rx="9" fill="#087f6b"/>
<path d="M63 68 L73 51 L83 68 M68 63 H78" fill="none" stroke="#fffdf7" stroke-width="3"/>
<text x="106" y="67" fill="#536b79" font-size="18" font-weight="700" letter-spacing="1">A LIVING MATHEMATICS LAB</text>
<text x="52" y="193" fill="#15394a" font-size="94" font-weight="700">ANAXIA</text>
<text x="57" y="252" fill="#087f6b" font-size="33">Explore boldly. Verify exactly.</text>
<text x="58" y="308" fill="#15394a" font-size="23">Open research. Local models. Exact certificates.</text>
<text x="58" y="343" fill="#536b79" font-size="22">A research loop built for checkable mathematics.</text>
<rect x="58" y="372" width="199" height="35" rx="17" fill="#e0f3e9" stroke="#b0d8c4"/>
<text x="73" y="395" fill="#087f6b" font-size="13" font-weight="700">LOCAL + CLOUD MODELS</text>
<text x="278" y="395" fill="#536b79" font-size="13">SOURCE-LINKED / OPEN RESEARCH</text>
<g transform="translate(1098 225)" fill="none">
<circle r="195" stroke="#d7e5ec"/><circle r="169" stroke="#d7e5ec"/><circle r="143" stroke="#d7e5ec"/>
<ellipse rx="183" ry="73" stroke="#6caaa0" stroke-width="2"/>
<ellipse rx="183" ry="73" transform="rotate(60)" stroke="#9aaecf" stroke-width="2"/>
<ellipse rx="183" ry="73" transform="rotate(-60)" stroke="#cf9a8f" stroke-width="2"/>
<circle r="56" fill="#eff6ff" stroke="#a3c8c0" stroke-width="2"/>
<circle cx="183" r="5" fill="#087f6b"/>
<circle cy="155" r="5" fill="#bc4b3e"/>
</g>
<text x="1076" y="247" fill="#15394a" font-size="59" font-weight="700">A</text>
<text x="937" y="50" fill="#536b79" font-size="20">p(x) = Σ wᵢ qᵢ(x)²</text>
<text x="1298" y="285" fill="#bc4b3e" font-size="15">wᵢ ≥ 0</text>
<text x="911" y="375" fill="#536b79" font-size="16">A = L D Lᵀ</text>
<text x="917" y="430" fill="#536b79" font-size="12">HYPOTHESIS</text>
<path d="M1010 422 H1176" stroke="#9cb7c0"/>
<text x="1194" y="430" fill="#087f6b" font-size="12">CERTIFICATE</text>
<path d="M56 453 H1344" stroke="#cbdedc"/>
<g fill="#536b79" font-size="18" font-weight="700">
<text x="58" y="503" fill="#087f6b">01 DISCOVER</text><text x="321" y="503">02 FORMALIZE</text>
<text x="584" y="503">03 PROPOSE</text><text x="847" y="503">04 CRITIQUE</text><text x="1110" y="503">05 VERIFY</text>
</g></g></svg>'''
    (ASSETS / 'anaxia-hero.svg').write_text(svg + '\n', encoding='utf-8')
    print('Generated Anaxia hero: GIF animation, PNG reduced-motion fallback, SVG companion.')


if __name__ == '__main__':
    main()
