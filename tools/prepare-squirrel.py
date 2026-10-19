"""Fit generated alpha art and sample its silhouette for the existing puzzle converter."""
import argparse, json, pathlib
from PIL import Image

ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('source');args=parser.parse_args()
art=Image.open(args.source).convert('RGBA')
alpha=art.getchannel('A')
if alpha.getextrema()[0] == 255:
    raise RuntimeError('Generated squirrel has no transparency; request a transparent sprite.')
bbox=alpha.point(lambda a:255 if a>32 else 0).getbbox()
if not bbox:raise RuntimeError('Empty sprite')
cut=art.crop(bbox);cut.thumbnail((444,444),Image.Resampling.LANCZOS)
frame=Image.new('RGBA',(512,512));frame.alpha_composite(cut,((512-cut.width)//2,(512-cut.height)//2))
frame.save(ROOT/'assets/squirrel-painted-v1.png')
mask=frame.getchannel('A').resize((15,15),Image.Resampling.BOX)
# Use black subject pixels and the sampled alpha. The game converter composites
# transparent pixels on white, then applies its usual luminance threshold.
rgba=[v for a in mask.getdata() for v in (0,0,0,a)]
(ROOT/'data/squirrel-sampled-rgba.json').write_text(json.dumps(rgba),encoding='utf-8')
print('Saved centered 512px transparent sprite and 15x15 alpha coverage samples.')
