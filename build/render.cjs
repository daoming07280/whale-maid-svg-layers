const sharp=require('sharp');
const fs=require('fs'),path=require('path');
const root=__dirname;
(async()=>{
  const spec=JSON.parse(fs.readFileSync(path.join(root,'parts-spec.json'),'utf8'));
  if(process.argv[2]==='reserves'){
    for(const p of spec.parts){if(p.underpaint){await sharp(path.join(root,'work',p.name+'-reserve.svg')).png().toFile(path.join(root,'work',p.name+'-reserve.png'));}}
    console.log('Rendered reconstruction masks');return;
  }
  const manifest=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
  for(const p of manifest.parts){await sharp(path.join(root,p.svg)).png().toFile(path.join(root,p.png));}
  await sharp(path.join(root,'whale-maid.svg')).png().toFile(path.join(root,'whale-maid.png'));
  await sharp(path.join(root,'whale-maid.svg')).flatten({background:'#ffffff'}).png().toFile(path.join(root,'preview.png'));
  await sharp(path.join(root,'work/visible-only.svg')).png().toFile(path.join(root,'work/visible-only.png'));
  console.log('Rendered aligned transparent layers and master preview.');
})().catch(e=>{console.error(e);process.exit(1)});
