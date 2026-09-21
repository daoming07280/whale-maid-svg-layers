"""Replace traced facial backing with clean, complete, editable vector shapes."""
from pathlib import Path
import json,xml.etree.ElementTree as ET
ROOT=Path(__file__).parent
S='http://www.w3.org/2000/svg';I='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',S);ET.register_namespace('inkscape',I)
defs='''<radialGradient id="redraw-face" cx=".5" cy=".65" r=".8"><stop stop-color="#ffebdf"/><stop offset=".58" stop-color="#ffe7da"/><stop offset="1" stop-color="#ffd2c5"/></radialGradient>
<radialGradient id="redraw-blush"><stop stop-color="#ffa99b" stop-opacity=".65"/><stop offset=".58" stop-color="#ffb6a5" stop-opacity=".28"/><stop offset="1" stop-color="#ffbdad" stop-opacity="0"/></radialGradient>
<linearGradient id="redraw-white" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#e8dce5"/><stop offset=".28" stop-color="#fff9f4"/><stop offset="1" stop-color="#fffaf5"/></linearGradient>
<linearGradient id="redraw-mouth" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#db817a"/><stop offset=".42" stop-color="#ffa59a"/><stop offset="1" stop-color="#ffb5a3"/></linearGradient>
<radialGradient id="redraw-tongue"><stop stop-color="#ffc1ad"/><stop offset="1" stop-color="#ffad9c"/></radialGradient>'''
parts={
'face':'''<path d="M425 413 C416 302 478 218 604 216 C726 215 794 305 784 429 L777 521 C768 563 737 585 687 599 Q604 628 520 601 Q450 583 434 543 Q419 503 425 413Z" fill="url(#redraw-face)" stroke="#794b51" stroke-width="2.3"/>
<ellipse cx="464" cy="543" rx="47" ry="31" fill="url(#redraw-blush)"/><ellipse cx="738" cy="543" rx="47" ry="31" fill="url(#redraw-blush)"/>
<ellipse cx="595" cy="511" rx="2.3" ry="1.7" fill="#fff7ed" opacity=".9"/>''',
'eyewhite-r':'''<path d="M432 474 C439 441 463 421 490 424 C533 422 548 458 539 495 Q528 526 489 521 Q443 517 432 474Z" fill="url(#redraw-white)"/>''',
'eyewhite-l':'''<path d="M652 474 C653 439 676 422 704 424 C743 423 763 447 767 473 Q762 515 715 521 Q665 522 652 474Z" fill="url(#redraw-white)"/>''',
'eyebrow-r':'''<path d="M473 357 Q491 345 513 349" fill="none" stroke="#405d90" stroke-width="3.2" stroke-linecap="round"/>''',
'eyebrow-l':'''<path d="M674 348 Q699 342 726 359" fill="none" stroke="#405d90" stroke-width="3.2" stroke-linecap="round"/>''',
'mouth-open':'''<path d="M572 537 L583 537 L596 533 L611 537 L624 537 C631 554 623 578 608 582 Q590 588 580 576 Q569 561 572 537Z" fill="url(#redraw-mouth)" stroke="#bd766c" stroke-width="1.7"/>
<path d="M579 560 Q597 548 621 557 Q620 574 607 580 Q590 584 581 573Z" fill="url(#redraw-tongue)"/>
<path d="M573 538 L584 538 L596 534 L612 538 L622 538" fill="none" stroke="#a65f58" stroke-width="1.4" stroke-linecap="round"/>'''
}
(ROOT/'native-face.json').write_text(json.dumps({'defs':defs,'parts':parts},ensure_ascii=False,indent=2))
def children(fragment):return list(ET.fromstring(f'<svg xmlns="{S}">'+fragment+'</svg>'))
def update(file):
    tree=ET.parse(file);root=tree.getroot();d=root.find(f'{{{S}}}defs')
    if d is None:d=ET.SubElement(root,f'{{{S}}}defs')
    for child in list(d):
        if child.attrib.get('id','').startswith('redraw-'):d.remove(child)
    for child in children(defs):d.append(child)
    changed=False
    for name,body in parts.items():
        layer=root.find(f'{{{S}}}g[@id="{name}"]')
        if layer is None:continue
        for child in list(layer):layer.remove(child)
        content=ET.SubElement(layer,f'{{{S}}}g',{'id':name+'-redrawn','data-kind':'native-vector-reconstruction'})
        for child in children(body):content.append(child)
        changed=True
    if changed:tree.write(file,encoding='utf-8',xml_declaration=True)
update(ROOT/'whale-maid.svg');update(ROOT/'work/visible-only.svg')
manifest=json.loads((ROOT/'manifest.json').read_text())
for p in manifest['parts']:
    if p['id'] in parts:
        update(ROOT/p['svg']);p['native_redraw']=True
        p['reconstruction']='Complete native vector backing reconstructed from reference; no baked-in hair/eye/mouth contours.'
manifest['method']='Source-guided vector tracing and semantic separation; complete native vector redraw for face, sclera, brows, and mouth; inferred hidden-area extensions.'
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Reconstructed six facial layers as clean native vector artwork.')
