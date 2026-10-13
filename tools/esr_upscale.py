# Real-ESRGAN x4plus on CPU via ncnn (pip install ncnn), tiled. usage: esr_upscale.py MODEL_DIR IN OUT
# MODEL_DIR holds realesrgan-x4plus.param/.bin from the realesrgan-ncnn-vulkan-20220424-ubuntu.zip GitHub release (v0.2.5.0).
import sys, time, numpy as np, ncnn
from PIL import Image
mdir, src, out = sys.argv[1:4]
T, P, S = 192, 12, 4
net = ncnn.Net(); net.opt.use_vulkan_compute = False; net.opt.num_threads = 4
net.load_param(f'{mdir}/realesrgan-x4plus.param'); net.load_model(f'{mdir}/realesrgan-x4plus.bin')
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32) / 255.0
H, W, _ = im.shape
res = np.zeros((H * S, W * S, 3), np.float32)
tiles = [(y, x) for y in range(0, H, T) for x in range(0, W, T)]
t0 = time.time()
for i, (y, x) in enumerate(tiles):
    y0, x0, y1, x1 = max(y - P, 0), max(x - P, 0), min(y + T + P, H), min(x + T + P, W)
    tile = np.ascontiguousarray(im[y0:y1, x0:x1].transpose(2, 0, 1))
    ex = net.create_extractor(); ex.input('data', ncnn.Mat(tile))
    _, o = ex.extract('output'); o = np.array(o).transpose(1, 2, 0)
    ty, tx = (y - y0) * S, (x - x0) * S
    h, w = (min(y + T, H) - y) * S, (min(x + T, W) - x) * S
    res[y * S:y * S + h, x * S:x * S + w] = o[ty:ty + h, tx:tx + w]
    print(f'{i + 1}/{len(tiles)} {time.time() - t0:.0f}s', flush=True)
Image.fromarray((np.clip(res, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out)
print('done', res.shape)
