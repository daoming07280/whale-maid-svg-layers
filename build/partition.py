from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import numpy as np
import json,colorsys,io

ROOT=Path(__file__).parent
spec=json.loads((ROOT/'parts-spec.json').read_text())
parts=spec['parts'];w,h=spec['width'],spec['height']
a=np.array(Image.open(ROOT/'source-transparent.png').convert('RGBA'))
rgb=a[:,:,:3].astype(np.int16);fg=a[:,:,3]>0
blue=(rgb[:,:,2]-rgb[:,:,0]>8)&(rgb[:,:,2]-rgb[:,:,1]>-5)
dark=(rgb.min(2)<110)&(rgb.mean(2)<150)
skin=(rgb[:,:,0]>180)&(rgb[:,:,0]-rgb[:,:,2]>22)&(rgb[:,:,0]-rgb[:,:,1]>12)
white=(rgb.min(2)>140)&(np.abs(rgb[:,:,0]-rgb[:,:,2])<36)&(np.abs(rgb[:,:,0]-rgb[:,:,1])<30)
conditions={'blue':blue,'notblue':~blue,'dark':dark,'skinzone':ndimage.binary_dilation(skin,iterations=2),'whitezone':ndimage.binary_dilation(white,iterations=2),'':np.ones(fg.shape,bool)}
labels=np.zeros((h,w),np.uint8)
paint=list(enumerate(parts,1))
paint.sort(key=lambda ip: ip[0]+(1000 if ip[1]['name'] in ['hand-r','hand-l','leg-r','leg-l','neck'] else 0))
for i,p in paint:
    m=np.array(Image.open(ROOT/'masks'/f"{p['name']}.png").convert('RGBA'))[:,:,3]>127
    if p['name'].startswith('leg-'):m[:1148]=False
    if p['name'].startswith('irides-'):
        m=ndimage.binary_fill_holes(ndimage.binary_closing(m&blue,iterations=1))&m
    labels[m&fg&conditions[p['condition']]]=i
# Residual outlines near socks/hem or the crown belong to adjacent components,
# not the catch-all rear hair. Preserve the continuous side locks themselves.
rear=(labels==1)|(labels==2)
eligible=(labels>2)&fg
_,nearest=ndimage.distance_transform_edt(~eligible,return_indices=True)
orphan=rear.copy();orphan[220:1040]=False
labels[orphan]=labels[tuple(nearest[:,orphan])]
assert np.all(labels[fg]>0),'Unassigned foreground pixels'
np.save(ROOT/'work/labels.npy',labels)
pal=np.array([(0,0,0)]+[tuple(int(v*255) for v in colorsys.hsv_to_rgb((i*.61803398875)%1,.57,.94)) for i in range(len(parts))],np.uint8)
color=pal[labels];color[~fg]=(245,245,245)
Image.fromarray(color).save(ROOT/'work/layer-map.png')

thumbw,thumbh=210,262
board=Image.new('RGB',(thumbw*8,(len(parts)+7)//8*(thumbh+28)),(236,240,247))
draw=ImageDraw.Draw(board)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
stats=[]
for i,p in enumerate(parts,1):
    m=labels==i
    # A one-pixel overlap prevents seams from independent curve fitting.
    expanded=ndimage.binary_dilation(m,iterations=1)&fg
    pa=np.zeros_like(a);pa[expanded]=a[expanded]
    buffer=io.BytesIO();Image.fromarray(pa).save(buffer,format='PNG')
    (ROOT/'work'/f"{p['name']}-visible.png").write_bytes(buffer.getvalue())
    ys,xs=np.where(m)
    p['visible_pixels']=int(m.sum())
    p['visible_bbox']=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
    if not len(xs): print('EMPTY',p['name'])
    tile=Image.new('RGBA',(w,h),'#d0dbe9');tile.alpha_composite(Image.fromarray(pa));tile.thumbnail((thumbw,thumbh))
    x=((i-1)%8)*thumbw;y=((i-1)//8)*(thumbh+28)
    board.paste(tile.convert('RGB'),(x,y))
    draw.text((x+5,y+thumbh+5),f"{i:02d} {p['name']}",font=font,fill=(25,35,55))
    stats.append({'id':p['name'],'pixels':p['visible_pixels'],'bbox':p['visible_bbox']})
board.save(ROOT/'work/partition-check.jpg',quality=92)
(ROOT/'parts-spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2))
print(json.dumps(stats,ensure_ascii=False))
