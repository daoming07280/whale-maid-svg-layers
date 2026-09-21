const fs=require('fs'),path=require('path'),sharp=require('sharp');
const root=__dirname,s=JSON.parse(fs.readFileSync(path.join(root,'parts-spec.json'),'utf8'));
(async()=>{for(const p of s.parts){const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="${s.width}" height="${s.height}" viewBox="0 0 ${s.width} ${s.height}"><path d="${p.path}" fill="white"/></svg>`;await sharp(Buffer.from(svg)).png().toFile(path.join(root,'masks',p.name+'.png'));}console.log('Masks rendered:',s.parts.length)})().catch(e=>{console.error(e);process.exit(1)});
