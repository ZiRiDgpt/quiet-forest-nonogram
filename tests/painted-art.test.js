const {test}=require('node:test'),assert=require('node:assert/strict');
const C=require('../logic/core'),levels=require('../logic/levels'),project=require('../game.json');
test('painted squirrel puzzle is the direct sampled silhouette and has one solution',()=>{
  const sample=require('../data/squirrel-painted-grid.json');
  const pixels=require('../data/squirrel-sampled-rgba.json');
  const level=levels.find(l=>l.id==='squirrel');
  assert.deepEqual(C.pixelsToGrid(pixels,15,15,sample.threshold),level.grid);
  assert.equal(C.analyze(level.grid,2500).status,'unique');
  const scene=project.layouts.find(s=>s.name==='Nonogram_squirrel');
  assert.equal(scene.instances.filter(i=>i.name==='Cell').length,225);
  const reward=scene.objects.find(o=>o.name==='RewardArt');
  assert.equal(reward.animations[0].directions[0].sprites[0].image,'squirrel-painted-v1.png');
});
