from pathlib import Path
import sys,json,io,zipfile,hashlib,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
import numpy as np
sys.path.insert(0,str(Path(__file__).parent.parent/'whale-maid-svg-deps'))
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
from psd_tools.constants import Compression

ROOT=Path(__file__).parent
manifest=json.loads((ROOT/'manifest.json').read_text());parts=manifest['parts']
w,h=manifest['canvas']['width'],manifest['canvas']['height']
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(fontpath,17);small=ImageFont.truetype(fontpath,13);large=ImageFont.truetype(fontpath,28)
def save_png(im,path):
    b=io.BytesIO();im.save(b,format='PNG');Path(path).write_bytes(b.getvalue())
def white(im):
    bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im.convert('RGBA'));return bg.convert('RGB')

master_svg=ET.parse(ROOT/'whale-maid.svg').getroot()
SVG='{http://www.w3.org/2000/svg}'
assert not list(master_svg.iter(SVG+'image')),'Embedded bitmap found'
assert len([e for e in master_svg if e.tag==SVG+'g'])==len(parts)==59
for p in parts:
    doc=ET.parse(ROOT/p['svg']).getroot()
    assert doc.attrib['viewBox']==f'0 0 {w} {h}'
    assert not list(doc.iter(SVG+'image'))
    im=Image.open(ROOT/p['png']);assert im.size==(w,h) and im.mode=='RGBA'

psd=PSDImage.new('RGBA',(w,h),(0,0,0,0))
recombined=Image.new('RGBA',(w,h))
tilew,tileh=240,260;cols=6;rows=(len(parts)+cols-1)//cols
sheet=Image.new('RGB',(cols*tilew,rows*tileh+84),'#eef2f8');d=ImageDraw.Draw(sheet)
d.text((22,14),'WHALE MAID / 59 SEPARATE PARTS',font=large,fill='#20334e')
d.text((24,53),'Detail view: each tile is scaled to fit. All exported layers share one canvas.',font=small,fill='#63728b')
for i,p in enumerate(parts):
    im=Image.open(ROOT/p['png']).convert('RGBA');bbox=im.getbbox();assert bbox is not None
    crop=im.crop(bbox)
    PixelLayer.frompil(crop,psd,name=f"{i+1:02d} {p['id']}",top=bbox[1],left=bbox[0],compression=Compression.RLE)
    recombined.alpha_composite(im)
    x=(i%cols)*tilew;y=(i//cols)*tileh+84
    d.rounded_rectangle((x+8,y+7,x+tilew-8,y+tileh-9),radius=12,fill='#ffffff')
    tile=Image.new('RGBA',(tilew-32,tileh-64),'#dfe6f0')
    crop.thumbnail((tile.width-20,tile.height-18),Image.Resampling.LANCZOS)
    tile.alpha_composite(crop,((tile.width-crop.width)//2,(tile.height-crop.height)//2))
    sheet.paste(tile.convert('RGB'),(x+16,y+16))
    d.text((x+17,y+tileh-41),f"{i+1:02d} {p['id']}",font=small,fill='#293e5e')
    if p['reconstructed_pixels']:d.ellipse((x+tilew-26,y+tileh-39,x+tilew-19,y+tileh-32),fill='#3e9eac')
psd.save(ROOT/'whale-maid-layered.psd')
print('PSD saved with',len(psd),'layers.',flush=True)
reopen=PSDImage.open(ROOT/'whale-maid-layered.psd')
assert len(reopen)==59 and reopen.size==(w,h)
assert [p.name for p in reopen]==[f"{i+1:02d} {p['id']}" for i,p in enumerate(parts)]
save_png(sheet,ROOT/'parts-contact-sheet.png')

pad=40;cw=650;ch=round(h*cw/w)
comparison=Image.new('RGB',(cw*2+pad*3,ch+150),'#f1f4f9');d=ImageDraw.Draw(comparison)
d.text((pad,25),'REFERENCE',font=large,fill='#243553')
d.text((pad*2+cw,25),'SVG REDRAW',font=large,fill='#243553')
left=white(Image.open(ROOT/'reference.png'));right=white(Image.open(ROOT/'whale-maid.png'))
left=left.resize((cw,ch),Image.Resampling.LANCZOS);right=right.resize((cw,ch),Image.Resampling.LANCZOS)
comparison.paste(left,(pad,75));comparison.paste(right,(pad*2+cw,75))
d.text((pad,ch+97),'Original supplied character',font=font,fill='#62728b')
d.text((pad*2+cw,ch+97),'Pure paths / 59 aligned parts',font=font,fill='#62728b')
save_png(comparison,ROOT/'comparison.png')

rendered=np.array(white(Image.open(ROOT/'whale-maid.png'))).astype(float)
neutral=np.array(white(Image.open(ROOT/'work/visible-only.png'))).astype(float)
ref=np.array(white(Image.open(ROOT/'source-transparent.png'))).astype(float)
recomp=np.array(white(recombined)).astype(float)
qa=dict(canvas=[w,h],semantic_layers=len(parts),native_vector_paths=len(list(master_svg.iter(SVG+'path'))),embedded_images=0,
        source_mean_absolute_color_error=float(np.mean(np.abs(rendered-ref))),
        reconstruction_neutral_mean_absolute_color_change=float(np.mean(np.abs(rendered-neutral))),
        png_recomposition_mean_absolute_color_error=float(np.mean(np.abs(rendered-recomp))),
        psd_reopened=True,psd_layer_count=len(reopen),cubism_editor_tested=False)
(ROOT/'validation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
assert qa['png_recomposition_mean_absolute_color_error']<1.0,'Layer render differs from master'
assert qa['reconstruction_neutral_mean_absolute_color_change']<1.0,'Hidden reconstruction changes neutral result'
print(json.dumps(qa,ensure_ascii=False),flush=True)

deliver=['whale-maid.svg','whale-maid.png','preview.png','whale-maid-layered.psd','comparison.png','parts-contact-sheet.png','manifest.json','README.md','reference.png','validation.json']
scripts=['prepare.py','partition.py','build-vectors.py','apply-native-face.py','masks.cjs','render.cjs','package-assets.py']
zip_path=ROOT.parent/'whale-maid-svg-layers.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for name in deliver:z.write(ROOT/name,'whale-maid/'+name)
    for p in parts:
        z.write(ROOT/p['svg'],'whale-maid/'+p['svg']);z.write(ROOT/p['png'],'whale-maid/'+p['png'])
    for name in scripts:z.write(ROOT/name,'whale-maid/build/'+name)
print('Package:',zip_path,zip_path.stat().st_size,flush=True)
