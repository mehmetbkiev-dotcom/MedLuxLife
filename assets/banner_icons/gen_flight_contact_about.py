import math, os
D=os.path.dirname(os.path.abspath(__file__))
WRAP='<svg xmlns="http://www.w3.org/2000/svg" viewBox="400 170 400 350" aria-hidden="true"><defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="400" y1="170" x2="800" y2="520"><stop offset="0" stop-color="#f6d891"/><stop offset="1" stop-color="#d6a043"/></linearGradient></defs><g fill="none" stroke="url(#g)" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">{}</g></svg>'
def f(x): return ('%.1f' % x).rstrip('0').rstrip('.')
# --- Flight tickets: ticket with notches, perforation, plane; rotated
t = ('<g transform="rotate(-10 600 345)">'
 '<path d="M478 255 H 636 A 16 16 0 0 0 668 255 H 722 Q 745 255 745 278 V 412 Q 745 435 722 435 H 668 A 16 16 0 0 0 636 435 H 478 Q 455 435 455 412 V 278 Q 455 255 478 255 Z"/>'
 '<path d="M652 286 V 404" stroke-width="7" stroke-dasharray="1 17"/>'
 '<g transform="translate(548 345) rotate(-20) translate(-552 -345)"><path stroke-width="7" d="M612 345 C 612 337 606 333 598 333 H 572 L 545 293 H 529 L 546 333 H 516 L 506 318 H 495 L 501 345 L 495 372 H 506 L 516 357 H 546 L 529 397 H 545 L 572 357 H 598 C 606 357 612 353 612 345 Z"/></g>'
 '<path d="M690 318 H 718 M690 345 H 718 M690 372 H 708" stroke-width="7"/>'
 '</g>')
open(D+'/flight-tickets.svg','w').write(WRAP.format(t))
# --- Contact: envelope + speech bubble
cx,cy,r,gap=704,258,50,13
R=r+gap
def cut_y(x): return cy+math.sqrt(R*R-(x-cx)**2)
def cut_x(y): return cx-math.sqrt(R*R-(y-cy)**2)
x_top=cut_x(265); y_right=cut_y(690)
env=f'M{f(x_top)} 265 H 472 Q 455 265 455 282 V 408 Q 455 425 472 425 H 673 Q 690 425 690 408 V {f(y_right)}'
# flap: left (470,283) -> (560,350) -> curve -> (584,350) -> toward (676,283), stopped at circle
p0=(584,350); p1=(676,283)
lo,hi=0.0,1.0
for _ in range(50):
    m=(lo+hi)/2; x=p0[0]+(p1[0]-p0[0])*m; y=p0[1]+(p1[1]-p0[1])*m
    if math.hypot(x-cx,y-cy)>R: lo=m
    else: hi=m
ex=p0[0]+(p1[0]-p0[0])*lo; ey=p0[1]+(p1[1]-p0[1])*lo
flap=f'M471 283 L 560 350 Q 572 359 584 350 L {f(ex)} {f(ey)}'
a1,a2=math.radians(118),math.radians(150)
sx,sy=cx+r*math.cos(a1),cy+r*math.sin(a1); txe,tye=cx+r*math.cos(a2),cy+r*math.sin(a2)
bubble=f'M{f(sx)} {f(sy)} A {r} {r} 0 1 0 {f(txe)} {f(tye)} L 650 322 Z'
dots=''.join(f'<circle cx="{x}" cy="{cy}" r="7" fill="url(#g)" stroke="none"/>' for x in (684,704,724))
open(D+'/contact.svg','w').write(WRAP.format(f'<path d="{env}"/><path d="{flap}"/><path d="{bubble}"/>{dots}'))
# --- About us: compass ring with heart centre and north needle
heart='M600 410 C 560 382 534 360 534 333 C 534 314 548 301 565 301 C 580 301 592 310 600 322 C 608 310 620 301 635 301 C 652 301 666 314 666 333 C 666 360 640 382 600 410 Z'
ring='<circle cx="600" cy="345" r="132"/>'
ticks='<path d="M600 213 V 232 M600 458 V 477 M468 345 H 487 M713 345 H 732" stroke-width="7"/>'
needle='<path d="M600 246 L 612 290 H 588 Z" stroke-width="7" stroke-linejoin="round"/>'
open(D+'/about-us.svg','w').write(WRAP.format(ring+ticks+needle+f'<path d="{heart}"/>'))
print('ok')
