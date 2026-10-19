const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const C=require('../logic/core');
const pixels=require('../data/squirrel-sampled-rgba.json');
const seen=new Set();let chosen;
for(const threshold of [128,120,136,112,144,104,152,96,160,88,168,80,176]){
  const grid=C.pixelsToGrid(pixels,15,15,threshold),key=JSON.stringify(grid);
  if(seen.has(key))continue;seen.add(key);
  const result=C.analyze(grid,2500);
  console.log(`threshold ${threshold}: ${result.status}`);
  if(result.status==='unique'){chosen={grid,threshold,status:result.status};break;}
}
if(!chosen)throw Error('No unique direct silhouette found; review art or sample settings. No level changed.');
fs.writeFileSync(path.join(root,'data/squirrel-painted-grid.json'),JSON.stringify(chosen,null,2));
console.log(chosen.grid.map(r=>r.map(v=>v?'██':'  ').join('')).join('\n'));
