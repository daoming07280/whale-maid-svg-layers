"""Trace visible color regions and add explicitly reconstructed hidden reserves."""
from pathlib import Path
import sys,json,re,subprocess,html,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).parent.parent/'whale-maid-svg-deps'))
import vtracer

ROOT=Path(__file__).parent
spec=json.loads((ROOT/'parts-spec.json').read_text());w,h=spec['width'],spec['height']
parts=sorted(spec['parts'],key=lambda p:p['z'])
defs=(ROOT/'shared-defs.svgfrag').read_text()
header=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
for p in parts:
    if p['underpaint']:
        (ROOT/'work'/f"{p['name']}-reserve.svg").write_text(header+'<defs>'+defs+'</defs>'+p['underpaint']+'</svg>')
subprocess.run(['node',str(ROOT/'render.cjs'),'reserves'],check=True)

labels=np.load(ROOT/'work/labels.npy')
ztable=np.zeros(256,dtype=np.int16)-1000
for i,p in enumerate(spec['parts'],1):ztable[i]=p['z']
zfield=ztable[labels]

def trace(image,pathstem,clip=False):
    bbox=image.getbbox()
    if not bbox:return ''
    x,y,x1,y1=bbox
    crop=image.crop(bbox)
    scale=1 if clip else (3 if pathstem.startswith(('irides-','eyelash-','eyebrow-','ahoge','whale-emblem')) else 2)
    if scale>1:crop=crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.LANCZOS)
    crop.save(ROOT/'work'/f'{pathstem}-crop.png')
    dest=ROOT/'work'/f'{pathstem}-trace.svg'
    vtracer.convert_image_to_svg_py(str(ROOT/'work'/f'{pathstem}-crop.png'),str(dest),
        colormode='color',hierarchical='stacked',mode='spline',
        filter_speckle=1 if clip else 2,color_precision=6 if clip else 8,layer_difference=12 if clip else 3,
        corner_threshold=60,length_threshold=2,max_iterations=10,splice_threshold=45,path_precision=3)
    s=dest.read_text();s=s[s.index('>',s.index('<svg'))+1:s.rindex('</svg>')]
    return f'<g transform="translate({x} {y}) scale({1/scale:.8f})">{s}</g>'

masterdefs=[defs];groups=[];visible_groups=[];manifest=[]
for n,p in enumerate(parts,1):
    name=p['name'];visible=trace(Image.open(ROOT/'work'/f'{name}-visible.png').convert('RGBA'),name)
    clipdef='';reserve='';reservepixels=0
    if p['underpaint']:
        reserve_a=np.array(Image.open(ROOT/'work'/f'{name}-reserve.png').convert('RGBA'))[:,:,3]
        # At the neutral pose, hidden reconstruction must be covered by a higher part.
        valid=(reserve_a>0)&(zfield>p['z'])
        reservepixels=int(valid.sum())
        if reservepixels:
            rgba=np.zeros((h,w,4),np.uint8);rgba[valid,:3]=255;rgba[valid,3]=255
            clip=trace(Image.fromarray(rgba),name+'-reserve-mask',clip=True)
            clipgroup=ET.fromstring(clip)
            clipcontent=''.join(ET.tostring(c,encoding='unicode') for c in clipgroup)
            clipdef=f'<clipPath id="reserve-clip-{name}" clipPathUnits="userSpaceOnUse" transform="{clipgroup.attrib["transform"]}">{clipcontent}</clipPath>'
            reserve=f'<g id="{name}-reconstructed" data-kind="reconstructed-hidden-area" clip-path="url(#reserve-clip-{name})">{p["underpaint"]}</g>'
    label=html.escape(p['label'],quote=True)
    attributes=f'id="{name}" inkscape:groupmode="layer" inkscape:label="{n:02d} {label}" data-part="{name}" data-z="{p["z"]}"'
    visible_group=f'<g {attributes}><g id="{name}-visible">{visible}</g></g>'
    group=f'<g {attributes}>{reserve}<g id="{name}-visible">{visible}</g></g>'
    masterdefs.append(clipdef);groups.append(group);visible_groups.append(visible_group)
    filename=f'{n:02d}-{name}'
    doc=header+f'<title>{label}</title><defs>'+defs+clipdef+'</defs>'+group+'</svg>'
    (ROOT/'parts/svg'/f'{filename}.svg').write_text(doc,encoding='utf-8')
    manifest.append(dict(index=n,id=name,label=p['label'],z=p['z'],role=p['role'],
       svg=f'parts/svg/{filename}.svg',png=f'parts/png/{filename}.png',
       visible_pixels=p['visible_pixels'],visible_bbox=p['visible_bbox'],reconstructed_pixels=reservepixels,
       reconstruction='inferred hidden overlap; not present in source' if reservepixels else None))
    print(f'{n:02d}/{len(parts)} {name}: visible={p["visible_pixels"]}, hidden={reservepixels}',flush=True)

title='<title>Whale maid — vector redraw and separated artwork</title>'
description='<desc>Pure vector paths traced from the supplied reference. Semantic layers with inferred hidden overlap reserves. Not a rigged Cubism model. Character-right is screen-left. Native canvas 1229 by 1536.</desc>'
(ROOT/'whale-maid.svg').write_text(header+title+description+'<defs>'+''.join(masterdefs)+'</defs>'+''.join(groups)+'</svg>',encoding='utf-8')
(ROOT/'work/visible-only.svg').write_text(header+title+''.join(visible_groups)+'</svg>',encoding='utf-8')
manifest_doc=dict(schema_version=1,canvas=dict(width=w,height=h),coordinates='top-left origin; character-right is screen-left',layer_order='bottom-to-top',source='reference.png',master='whale-maid.svg',
 method='Source-guided color-region vector tracing; manual semantic boundaries; inferred hidden-area vector extensions.',
 raster_embedded_in_svg=False,live2d_rigged=False,parts=manifest)
(ROOT/'manifest.json').write_text(json.dumps(manifest_doc,ensure_ascii=False,indent=2),encoding='utf-8')
print('Saved master, manifest, and 59 aligned SVG layers.',flush=True)
