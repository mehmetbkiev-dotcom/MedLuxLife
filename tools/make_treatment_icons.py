#!/usr/bin/env python3
"""Gold line icons for the title banners of treatment detail pages (Anna 2026-10-18: the banner icon must show the treatment).
Same style as the other banner icons (assets/banner_icons/final): 400x350, stroke 9, gold gradient, round caps, dotted contour arcs;
no crosses or plus signs. Writes assets/banner_icons/treatments/<slug>.svg; render with tools/icon_preview.mjs."""
import pathlib
OUT = pathlib.Path(__file__).resolve().parent.parent / 'assets/banner_icons/treatments'
DOT = ' stroke-dasharray="7 19"'

def svg(*paths):
    body = ''.join('<path d="%s"%s/>' % ((p, '') if isinstance(p, str) else (p[0], DOT)) for p in paths)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 350" aria-hidden="true"><defs><linearGradient id="g" gradientUnits="userSpaceOnUse" '
            'x1="0" y1="0" x2="400" y2="350"><stop offset="0" stop-color="#f6d891"/><stop offset="1" stop-color="#d6a043"/></linearGradient></defs>'
            '<g fill="none" stroke="url(#g)" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">' + body + '</g></svg>')

def dotted(p):
    return (p,)

TORSO = ['M135 35 C 140 90 165 120 162 170 C 159 215 128 240 132 320', 'M265 35 C 260 90 235 120 238 170 C 241 215 272 240 268 320']
BRA = ['M112 160 L 132 72', 'M288 160 L 268 72',
       'M98 168 C 98 226 138 254 174 247 C 190 243 198 228 200 206', 'M98 168 C 140 160 176 176 200 206',
       'M302 168 C 302 226 262 254 226 247 C 210 243 202 228 200 206', 'M302 168 C 260 160 224 176 200 206']
FACE = 'M200 45 C 142 45 116 95 118 158 C 120 228 160 292 200 297 C 240 292 280 228 282 158 C 284 95 258 45 200 45 Z'

ICONS = {
 # Plastic Surgery hub (263): whole body instead of the face only (Anna 2026-10-18)
 'plastic-surgery': svg('M190 22 m-26 0 a26 26 0 1 0 52 0 a26 26 0 1 0 -52 0'.replace('M190 22', 'M190 48'),
                        'M178 76 C 178 86 172 90 160 93 C 144 97 136 108 136 126 L 132 210', 'M202 76 C 202 86 208 90 220 93 C 236 97 244 108 244 126 L 248 210',
                        'M154 120 C 156 150 166 168 170 186 C 174 204 152 224 150 252 C 148 280 158 306 164 335',
                        'M226 120 C 224 150 214 168 210 186 C 206 204 228 224 230 252 C 232 280 222 306 216 335', 'M190 262 L 190 335',
                        dotted('M282 70 C 318 120 322 220 286 284'), dotted('M318 110 C 340 160 338 230 314 268')),
 'mommy-makeover': svg(*TORSO, 'M200 262 C 180 247 170 236 170 223 C 170 212 178 205 187 205 C 193 205 198 208 200 213 C 202 208 207 205 213 205 C 222 205 230 212 230 223 C 230 236 220 247 200 262 Z',
                       dotted('M300 80 C 332 130 334 200 302 255')),
 'rhinoplasty': svg('M262 35 C 212 35 180 66 177 112 C 176 128 171 140 162 152 L 128 202 C 124 210 129 217 137 217 L 160 219 C 162 227 158 233 160 240 C 164 247 160 253 162 260 C 164 271 171 279 182 281 C 204 285 218 290 226 305 L 230 332',
                    dotted('M146 128 C 108 160 92 205 116 250')),
 'tummy-tuck': svg(*TORSO, 'M200 196 m-6 0 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0', 'M78 170 L 120 170', 'M106 156 L 120 170 L 106 184', 'M322 170 L 280 170', 'M294 156 L 280 170 L 294 184'),
 'liposuction': svg(*TORSO, 'M200 168 C 200 168 176 197 176 214 C 176 228 187 238 200 238 C 213 238 224 228 224 214 C 224 197 200 168 200 168 Z',
                    dotted('M96 120 C 70 160 70 210 96 250'), dotted('M304 120 C 330 160 330 210 304 250')),
 'breast-augmentation': svg(*BRA, dotted('M70 200 C 70 130 125 105 175 135'), dotted('M330 200 C 330 130 275 105 225 135')),
 'breast-lift': svg(*BRA, 'M345 270 L 345 120', 'M325 140 L 345 120 L 365 140'),
 'breast-reduction': svg(*BRA, 'M30 190 L 62 190', 'M50 176 L 64 190 L 50 204', 'M370 190 L 338 190', 'M350 176 L 336 190 L 350 204'),
 'gynecomastia-surgery': svg('M174 22 L 177 50', 'M226 22 L 223 50',
                             'M177 50 C 160 60 132 62 110 74 C 94 84 90 108 94 140 L 108 325', 'M223 50 C 240 60 268 62 290 74 C 306 84 310 108 306 140 L 292 325',
                             'M120 148 C 138 176 176 178 194 154', 'M280 148 C 262 176 224 178 206 154', 'M200 268 m-6 0 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0'),
 'arm-lift': svg('M48 92 C 48 140 56 162 70 180', 'M70 180 C 140 170 230 166 288 170', 'M92 235 C 150 235 230 218 288 208', 'M70 180 C 76 210 82 228 92 235',
                 'M288 170 C 310 163 340 161 360 167 C 373 171 373 186 360 188 L 322 192 L 330 202 C 335 211 327 217 317 214 L 288 208',
                 dotted('M108 268 C 150 274 200 262 236 244')),
 'brazilian-butt-lift': svg('M210 30 C 200 80 188 112 202 142 C 244 172 254 232 218 262 C 202 274 198 294 204 330',
                            'M118 30 C 112 90 118 140 118 182 C 116 242 128 284 138 330',
                            dotted('M248 128 C 302 160 306 244 250 282')),
 'eyelid-surgery': svg('M78 200 C 130 138 270 138 322 200 C 270 258 130 258 78 200 Z', 'M200 200 m-34 0 a34 34 0 1 0 68 0 a34 34 0 1 0 -68 0',
                       dotted('M92 168 C 148 108 252 108 308 168')),
 'facelift': svg(FACE, 'M88 258 C 66 214 66 168 84 128', 'M70 142 L 84 126 L 100 138', 'M312 258 C 334 214 334 168 316 128', 'M330 142 L 316 126 L 300 138'),
 'neck-lift': svg('M238 30 C 192 30 162 60 160 104 C 159 119 154 129 147 139 L 130 168 C 127 175 131 180 138 180 L 152 182 C 154 190 150 196 152 202 C 156 208 152 214 154 220 C 156 232 164 240 177 242',
                  'M177 242 C 207 240 242 225 264 200', 'M184 252 C 192 280 194 305 192 335', 'M292 190 C 287 240 292 290 302 335',
                  dotted('M166 280 C 202 292 244 276 270 244')),
 'buccal-fat-removal': svg(FACE, dotted('M150 168 C 136 200 142 230 166 248'), dotted('M250 168 C 264 200 258 230 234 248')),
 'otoplasty': svg('M228 58 C 300 56 324 138 304 188 C 290 224 258 230 250 266 C 243 298 214 308 194 292 C 179 280 177 262 190 252',
                  'M214 110 C 256 98 276 150 256 180 C 246 196 230 192 228 212', dotted('M126 92 C 98 150 98 220 126 278')),
}

if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, s in ICONS.items():
        (OUT / (slug + '.svg')).write_text(s + '\n')
    print(len(ICONS), 'icons ->', OUT)
