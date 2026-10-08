"""Gold line icons for the 62 department pages. Coordinate system: viewBox 400 170 400 350 (centre 600,345)."""
import os, re
HERE = os.path.dirname(os.path.abspath(__file__))
LINE = os.path.join(HERE, 'line')
def body(name):
    s = open(os.path.join(LINE, name + '.svg')).read()
    a = s.index('<g fill'); a = s.index('>', a) + 1; return s[a:s.rindex('</g>')]
def old(name):  # first-generation icons (cardiology/neurology/...)
    s = open(os.path.join(HERE, name + '-icon-plain.svg')).read()
    a = s.index('<g fill="none"'); a = s.index('>', a) + 1; return s[a:s.rindex('</g>')].replace('url(#g_' + name + ')', 'url(#g)')
G = {
 'heart': old('cardiology'), 'brain': old('neurology'), 'kidneys': old('nephrology'), 'eye': old('ophthalmology'),
 'ribbon': body('medical-oncology'), 'bone': body('orthopedics'), 'spine': body('neurosurgery'), 'stomach': body('bariatric-surgery'),
 'stetho': body('check-up-packages'), 'profile': body('plastic-surgery'), 'renew': '<path d="M470 330 A 135 135 0 0 1 690 225"/><path d="M690 225 L 668 222 M690 225 L 686 247"/><path d="M730 360 A 135 135 0 0 1 510 465"/><path d="M510 465 L 532 468 M510 465 L 514 443"/>',
 'drop': '<path d="M600 205 C 560 270 525 315 525 370 C 525 420 560 455 600 455 C 640 455 675 420 675 370 C 675 315 640 270 600 205 Z"/><path d="M565 380 C 568 405 582 420 602 424" stroke-width="7"/>',
 'lungs': '<path d="M600 215 V 330 M600 300 C 585 315 570 320 560 320 M600 300 C 615 315 630 320 640 320"/><path d="M560 255 C 520 260 490 330 488 400 C 487 440 505 460 535 455 C 565 450 575 430 575 400 L 575 300"/><path d="M640 255 C 680 260 710 330 712 400 C 713 440 695 460 665 455 C 635 450 625 430 625 400 L 625 300"/>',
 'ear': '<path d="M560 450 C 540 450 530 430 545 410 C 560 390 565 375 545 350 C 520 318 525 255 575 225 C 630 195 690 230 690 290 C 690 335 655 345 640 370 C 625 395 630 450 580 455"/><path d="M590 300 C 590 270 625 262 640 285 C 652 305 635 322 618 330 C 605 336 605 352 615 360" stroke-width="7"/>',
 'uterus': '<path d="M600 300 C 560 300 545 330 548 360 C 552 395 575 410 585 430 L 585 470 M615 470 L 615 430 C 625 410 648 395 652 360 C 655 330 640 300 600 300 Z"/><path d="M548 330 C 520 310 495 300 470 312 C 450 322 452 345 470 348 M652 330 C 680 310 705 300 730 312 C 750 322 748 345 730 348"/><circle cx="470" cy="360" r="16" stroke-width="7"/><circle cx="730" cy="360" r="16" stroke-width="7"/>',
 'pregnant': '<circle cx="585" cy="225" r="26"/><path d="M585 252 C 575 285 570 300 572 320 C 610 325 650 350 650 395 C 650 430 620 445 590 440 L 585 490 M572 320 C 560 350 555 400 560 440 L 555 490"/><path d="M572 290 L 540 345" stroke-width="7"/>',
 'liver': '<path d="M470 300 C 470 260 520 240 590 240 C 660 240 735 250 735 285 C 735 315 700 330 660 360 C 620 390 590 430 555 430 C 505 430 470 380 470 300 Z"/><path d="M595 245 C 590 290 595 330 625 370" stroke-width="7"/>',
 'thyroid': '<path d="M600 300 C 590 280 570 230 545 230 C 515 230 505 270 510 320 C 515 370 540 410 570 400 C 590 393 595 360 600 345 C 605 360 610 393 630 400 C 660 410 685 370 690 320 C 695 270 685 230 655 230 C 630 230 610 280 600 300 Z"/><path d="M600 200 V 250 M600 380 V 480" stroke-width="7" stroke-dasharray="14 12"/>',
 'virus': '<circle cx="600" cy="345" r="80"/>' + ''.join('<path d="M%d %d L %d %d"/><circle cx="%d" cy="%d" r="11" fill="url(#g)" stroke="none"/>' % (600+80*c, 345+80*s, 600+118*c, 345+118*s, 600+124*c, 345+124*s) for c, s in [(1,0),(-1,0),(0,1),(0,-1),(.707,.707),(-.707,.707),(.707,-.707),(-.707,-.707)]) + '<circle cx="575" cy="325" r="12" stroke-width="7"/><circle cx="625" cy="370" r="9" stroke-width="7"/>',
 'shield': '<path d="M600 205 C 650 230 690 235 715 235 C 715 360 680 430 600 480 C 520 430 485 360 485 235 C 510 235 550 230 600 205 Z"/><path d="M600 290 V 400 M545 345 H 655"/>',
 'microscope': '<path d="M560 210 L 600 200 L 640 300 L 600 315 Z"/><path d="M610 312 L 622 345"/><path d="M590 360 C 650 360 690 330 690 285 C 690 260 675 245 655 240"/><path d="M500 465 H 720 M560 465 C 560 420 590 405 620 405 H 680 V 465"/><circle cx="618" cy="355" r="8" fill="url(#g)" stroke="none"/>',
 'dna': '<path d="M540 200 C 540 270 660 280 660 345 C 660 410 540 420 540 490"/><path d="M660 200 C 660 270 540 280 540 345 C 540 410 660 420 660 490"/><path d="M558 230 H 642 M575 265 H 625 M575 425 H 625 M558 460 H 642 M555 330 H 645 M555 362 H 645" stroke-width="6"/>',
 'xray': '<rect x="480" y="210" width="240" height="270" rx="22"/><path d="M600 240 V 450" stroke-width="7"/><path d="M600 280 C 560 280 535 290 525 305 M600 320 C 555 320 530 330 520 345 M600 360 C 560 360 535 372 528 385 M600 280 C 640 280 665 290 675 305 M600 320 C 645 320 670 330 680 345 M600 360 C 640 360 665 372 672 385" stroke-width="7"/>',
 'atom': '<circle cx="600" cy="345" r="18" fill="url(#g)" stroke="none"/><ellipse cx="600" cy="345" rx="140" ry="52"/><ellipse cx="600" cy="345" rx="140" ry="52" transform="rotate(60 600 345)"/><ellipse cx="600" cy="345" rx="140" ry="52" transform="rotate(-60 600 345)"/>',
 'scalpel': '<path d="M480 470 L 600 350"/><path d="M590 360 L 690 240 C 715 215 735 230 720 255 L 615 375 Z"/><path d="M500 490 H 720" stroke-width="6"/>',
 'skin': '<path d="M470 270 C 515 250 555 290 600 270 C 645 250 685 290 730 270"/><path d="M470 345 H 730 M470 420 H 730" stroke-width="7"/><path d="M600 200 V 390" stroke-width="7"/><ellipse cx="600" cy="400" rx="16" ry="22" stroke-width="7"/><path d="M520 300 V 470 M680 300 V 470" stroke-width="6" stroke-dasharray="2 18"/>',
 'bladder': '<ellipse cx="520" cy="215" rx="24" ry="34"/><ellipse cx="680" cy="215" rx="24" ry="34"/><path d="M520 250 C 520 275 530 295 545 310 M680 250 C 680 275 670 295 655 310"/><path d="M600 300 C 530 300 505 350 515 395 C 525 440 560 455 600 455 C 640 455 675 440 685 395 C 695 350 670 300 600 300 Z"/><path d="M600 455 V 490"/>',
 'joint': '<path d="M520 210 L 520 300 C 520 330 545 345 575 340 L 590 337"/><path d="M680 210 L 680 300"/><path d="M610 353 L 625 356 C 655 360 680 375 680 405 L 680 490 M520 400 L 520 490"/><circle cx="600" cy="345" r="45"/><path d="M640 255 L 700 230 M650 285 L 712 280" stroke-width="6" opacity=".9"/>',
 'bolt': '<path d="M625 205 L 535 355 H 600 L 570 485 L 670 320 H 605 Z"/>',
 'figure': '<circle cx="600" cy="225" r="27"/><path d="M600 255 V 370 M600 285 L 535 330 M600 285 L 665 250 M600 370 L 550 470 M600 370 L 660 455 L 700 455"/>',
 'apple': '<path d="M600 285 C 560 260 500 270 495 335 C 490 400 535 470 575 465 C 590 463 595 455 600 455 C 605 455 610 463 625 465 C 665 470 710 400 705 335 C 700 270 640 260 600 285 Z"/><path d="M600 285 C 600 255 605 235 620 215"/><path d="M612 240 C 640 215 675 220 690 235 C 665 255 635 255 612 240 Z"/>',
 'monitor': '<rect x="465" y="225" width="270" height="190" rx="18"/><path d="M490 330 H 545 L 565 290 L 590 370 L 615 300 L 630 330 H 710" stroke-width="7"/><path d="M560 465 H 640 M600 415 V 465"/>',
 'baby': '<circle cx="600" cy="255" r="45"/><path d="M582 255 h 0.1 M618 255 h 0.1" stroke-width="12"/><path d="M585 280 C 595 288 605 288 615 280" stroke-width="6"/><path d="M548 310 C 520 340 520 420 555 455 C 580 478 620 478 645 455 C 680 420 680 340 652 310"/><path d="M548 360 C 580 380 620 380 652 360" stroke-width="7"/>',
 'cross': '<rect x="540" y="215" width="120" height="260" rx="22"/><rect x="470" y="285" width="260" height="120" rx="22"/>',
 'mask': '<path d="M520 300 C 560 270 640 270 680 300 C 690 350 670 410 600 430 C 530 410 510 350 520 300 Z"/><path d="M520 300 L 470 270 M680 300 L 730 270"/><path d="M600 430 C 600 460 620 480 650 485 C 690 490 720 470 730 450" stroke-width="7"/><path d="M565 345 H 635 M575 375 H 625" stroke-width="7"/>',
 'child': '<circle cx="600" cy="235" r="35"/><path d="M600 272 V 380 M600 300 L 545 345 M600 300 L 655 345 M600 380 L 565 465 M600 380 L 635 465"/>',
 'head': '<path d="M625 200 C 570 195 530 230 528 285 C 527 305 515 318 503 332 C 497 340 505 347 516 350 C 520 360 517 372 523 380 C 516 392 523 402 536 404 C 540 425 553 440 583 440 L 598 440 L 603 490"/><path d="M710 300 C 712 240 675 205 625 200"/><path d="M710 300 C 710 345 690 380 665 405 L 670 490"/>',
 'pituitary': '',
 'wavy': '',
}
G['pituitary'] = G['brain'] + '<circle cx="600" cy="430" r="16" fill="url(#g)" stroke="none"/>'
def T(g, s=1.0, dx=0, dy=0):
    # keep the visual stroke width constant when a glyph is scaled down
    inner = re.sub(r'stroke-width="([\d.]+)"', lambda m: 'stroke-width="%g"' % (float(m.group(1)) / s), G[g])
    return '<g stroke-width="%g" transform="translate(%g %g) scale(%g) translate(%g %g)">%s</g>' % (9 / s, 600 + dx, 345 + dy, s, -600, -345, inner)
def badge(g):  # small secondary glyph, bottom right
    return T(g, 0.42, 125, 115).replace('stroke-width="', 'stroke-width="1')  # thicker strokes after scaling
def kid(main, s=0.82):
    return T(main, s, -35, -10) + T('child', 0.38, 160, 110)
ICONS = {
 'adult-bone-marrow-transplantation': T('bone', .9, -10, -20) + T('drop', .42, 125, 110),
 'algology-pain-medicine': T('spine', .9, -40) + T('bolt', .5, 130, -40),
 'anaesthesiology-and-reanimation': T('mask'),
 'audiology': T('ear') + '<path d="M705 300 C 725 320 725 365 705 385 M735 280 C 765 315 765 370 735 405" stroke-width="7"/>',
 'breast-surgery': T('ribbon', .85, -40) + T('heart', .38, 125, 100),
 'cardiovascular-surgery': T('heart', .9, -30) + T('scalpel', .42, 125, 100),
 'chest-diseases-pulmonology': T('lungs'),
 'child-and-adolescent-psychiatry': T('head', .85, -40) + T('child', .38, 160, 110),
 'dermatology': T('skin'),
 'emergency-medicine': T('cross') + '<path d="M555 345 H 585 L 597 320 L 612 370 L 622 345 H 645" stroke-width="7"/>',
 'endocrine-surgery': T('thyroid', .9, -30) + T('scalpel', .42, 125, 100),
 'endocrinology-and-metabolic-diseases': T('thyroid'),
 'gastroenterological-surgery': T('stomach', .9, -30) + T('scalpel', .42, 125, 100),
 'gastroenterology': T('stomach'),
 'general-surgery': T('scalpel'),
 'gynaecological-oncology': T('uterus', .85, -30, -15) + T('ribbon', .42, 125, 100),
 'haematology': T('drop'),
 'hirsutism-clinic': T('profile', .9, -20) + '<path d="M532 360 C 528 380 535 395 545 400 M550 410 C 548 425 556 432 566 434" stroke-width="5"/>',
 'imaging-unit': T('xray'),
 'immunology': T('shield'),
 'infectious-diseases-and-clinical-microbiology': T('virus'),
 'intensive-care-unit': T('monitor'),
 'internal-medicine': T('stetho', .9, -20) + '<path d="M690 230 V 290 M660 260 H 720" stroke-width="8"/>',
 'interventional-radiology': T('xray', .85, -30) + '<path d="M690 470 C 650 470 640 420 650 380 C 660 340 690 330 700 300" stroke-width="7"/><circle cx="700" cy="296" r="8" fill="url(#g)" stroke="none"/>',
 'kidney-transplant-clinic': T('kidneys', .7) + T('renew', 1.0),
 'liver-transplant-clinic': T('liver', .62) + T('renew', 1.0),
 'medical-genetics': T('dna'),
 'medical-histology-and-embryology': T('microscope', .9, -30) + T('ivf', .0) if False else T('microscope', .9, -30) + '<circle cx="705" cy="430" r="34" stroke-width="7"/><circle cx="705" cy="430" r="14" stroke-width="6"/>',
 'medical-microbiology': T('microscope', .9, -30) + T('virus', .32, 125, 100),
 'medical-pathology': T('microscope'),
 'neonatal-intensive-care-unit-nicu': T('baby', .85, -30) + T('monitor', .36, 125, 105),
 'nuclear-medicine': T('atom'),
 'nutrition-and-dietetics': T('apple'),
 'obstetrics-and-gynaecology': T('pregnant'),
 'otolaryngology-ent': T('ear', .9, -20) + '<path d="M690 260 C 700 290 700 330 690 360 M712 300 H 740" stroke-width="7"/>',
 'paediatric-allergy-and-immunology': kid('shield'),
 'paediatric-bone-marrow-transplantation': T('bone', .75, -40, -30) + T('drop', .32, 100, 90) + T('child', .34, 170, 110),
 'paediatric-cardiology': kid('heart'),
 'paediatric-endocrinology': kid('thyroid'),
 'paediatric-gastroenterology-hepatology-and-nutrition': kid('stomach'),
 'paediatric-haematology': kid('drop'),
 'paediatric-infectious-diseases': kid('virus', .7),
 'paediatric-nephrology': kid('kidneys'),
 'paediatric-neurology': kid('brain'),
 'paediatric-oncology': kid('ribbon'),
 'paediatric-rheumatology': kid('joint'),
 'paediatric-surgery': kid('scalpel'),
 'paediatrics': T('child', 1.05) + '<path d="M690 250 C 690 235 705 228 714 238 C 723 228 738 235 738 250 C 738 265 714 278 714 278 C 714 278 690 265 690 250 Z" stroke-width="6"/>',
 'parathyroid-transplant-clinic': T('thyroid', .62) + T('renew', 1.0),
 'pcos-and-hirsutism-clinic': T('uterus', .9, -20) + '<path d="M705 420 C 700 440 708 455 720 460 M725 410 C 722 430 730 440 742 444" stroke-width="5"/>',
 'pelvic-pain-and-endometriosis-clinic': T('uterus', .9, -30) + T('bolt', .38, 125, 95),
 'perinatology': T('pregnant', .9, -30) + T('heart', .34, 125, 105),
 'physical-therapy-and-rehabilitation': T('figure'),
 'pituitary-clinic': T('pituitary'),
 'psychiatry': T('head', .95) + T('brain', .32, 22, -45),
 'psychology': T('head', .95) + T('heart', .3, 22, -40),
 'radiology': T('xray'),
 'rheumatology': T('joint'),
 'thoracic-surgery': T('lungs', .9, -30) + T('scalpel', .42, 125, 100),
 'thyroid-and-parathyroid-diseases-and-surgery-clinic': T('thyroid', .9, -30) + '<circle cx="545" cy="290" r="9" fill="url(#g)" stroke="none"/><circle cx="625" cy="290" r="9" fill="url(#g)" stroke="none"/>',
 'transfusion-centre': T('drop', .85, -40) + '<path d="M690 230 V 290 M660 260 H 720" stroke-width="8"/>',
 'urology': T('bladder'),
}
WRAP = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="400 170 400 350" aria-hidden="true"><defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="400" y1="170" x2="800" y2="520"><stop offset="0" stop-color="#f6d891"/><stop offset="1" stop-color="#d6a043"/></linearGradient></defs><g fill="none" stroke="url(#g)" stroke-width="9" stroke-linecap="round" stroke-linejoin="round">{}</g></svg>'
if __name__ == '__main__':
    out = os.path.join(HERE, 'dept'); os.makedirs(out, exist_ok=True)
    for k, b in ICONS.items():
        # strokes in scaled groups: keep visual width ~9 by vector-effect
        open(os.path.join(out, k + '.svg'), 'w').write(WRAP.format(b))
    print(len(ICONS))
