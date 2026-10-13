# Replace the two small tiles baked into the Home hero image with sharp photos.
import sys
from PIL import Image, ImageDraw
src, dental, hair, out = sys.argv[1:5]
K = 1.5                      # output scale vs original 1669x942
SS = 4                       # supersampling for smooth corners
GOLD = (212, 162, 76)        # site gold #d4a24c
base = Image.open(src).convert('RGB')
base = base.resize((round(base.width * K), round(base.height * K)), Image.LANCZOS)
tiles = [  # (outer box in original px, photo, crop box in photo px)
    ((24, 637, 268, 852), dental, (330, 190, 1250, 1000)),
    ((281, 637, 529, 852), hair, (450, 0, 1536, 955)),
]
R, BW = 14 * K, 2 * K
for (x0, y0, x1, y1), photo, crop in tiles:
    box = tuple(round(v * K) for v in (x0, y0, x1, y1))
    w, h = box[2] - box[0], box[3] - box[1]
    p = Image.open(photo).convert('RGB')
    cx0, cy0, cx1, cy1 = crop
    # fit crop to tile aspect, keep centre
    cw, ch = cx1 - cx0, cy1 - cy0
    if cw / ch > w / h:
        nw = ch * w / h; cx0 += (cw - nw) / 2; cx1 = cx0 + nw
    else:
        nh = cw * h / w; cy0 += (ch - nh) / 2; cy1 = cy0 + nh
    p = p.crop((round(cx0), round(cy0), round(cx1), round(cy1))).resize((w, h), Image.LANCZOS)
    mask = Image.new('L', (w * SS, h * SS), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w * SS - 1, h * SS - 1), radius=R * SS, fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)
    ring = Image.new('L', (w * SS, h * SS), 0)
    ImageDraw.Draw(ring).rounded_rectangle((0, 0, w * SS - 1, h * SS - 1), radius=R * SS, outline=255, width=round(BW * SS))
    ring = ring.resize((w, h), Image.LANCZOS)
    tile = Image.composite(Image.new('RGB', (w, h), GOLD), p, ring)
    base.paste(tile, box[:2], mask)
base.save(out, quality=90, optimize=True, progressive=True, subsampling=0)
print(base.size)
