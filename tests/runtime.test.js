const {test}=require('node:test');
const assert=require('node:assert/strict');
const project=require('../game.json');
global.NonogramCore=require('../logic/core');
global.NonogramLevels=require('../logic/levels');
global.QuietForestSession=require('../logic/session');
global.QuietForestLayouts={};
global.localStorage={getItem:()=>null,setItem:()=>{}};
global.gdjs={evtTools:{runtimeScene:{replaceScene:(scene,name)=>{scene.destination=name;}}}};
require('../logic/runtime');
const api=global.QuietForestGD;
function scene(name,game){
  const data=project.layouts.find(s=>s.name===name),objects={};
  for(const i of data.instances){
    const v=Object.fromEntries((i.initialVariables||[]).map(v=>[v.name,v.value]));
    const o={x:i.x,y:i.y,w:i.width,h:i.height,animation:0,opacity:255,hidden:false,
      getX(){return this.x},getY(){return this.y},getWidth(){return this.w},getHeight(){return this.h},
      setX(x){this.x=x},setPosition(x,y){this.x=x;this.y=y},setWidth(w){this.w=w},setHeight(h){this.h=h},
      setAnimation(a){if(i.name==='Discovery_squirrel'&&a===1&&this.animation!==1){this.w*=5.12;this.h*=5.12;}this.animation=a},setOpacity(a){this.opacity=a},hide(h=true){this.hidden=h},
      setString(s){this.string=s},setColor(c){this.color=c},
      getVariables(){return {get:n=>({getAsString:()=>v[n],getAsNumber:()=>Number(v[n])})}}};
    (objects[i.name]??=[]).push(o);
  }
  return {getObjects:n=>objects[n]||[],getGame:()=>game,getElapsedTime:()=>100};
}
for(const level of global.NonogramLevels)test(`GDevelop adapter completes scene cycle: ${level.id}`,()=>{
  const input={isMouseButtonPressed:()=>false,isMouseButtonReleased:()=>false};
  const game={getInputManager:()=>input};
  const puzzle=scene(api.sceneFor(level.id),game);
  global.QuietForestLayouts[level.id]={x:230,y:220,cell:42};
  api.enter(puzzle,'puzzle',level.id);
  for(let y=0;y<level.grid.length;y++)for(let x=0;x<level.grid[y].length;x++)if(level.grid[y][x])api.applyCell(puzzle,x,y,1);
  assert.equal(puzzle.__qf.phase,'morph');
  assert.deepEqual(game.__quietForest.completed,[level.id]);
  for(let i=0;i<23;i++)api.tick(puzzle);
  assert.equal(puzzle.destination,'Reward');
  assert.equal(puzzle.getObjects('RewardArt')[0].opacity,255);
  const reward=scene('Reward',game);api.enter(reward,'reward');
  assert.equal(reward.getObjects('Art_'+level.id)[0].hidden,false);
  api.command(reward,'next');assert.equal(reward.destination,'Forest');
  const forest=scene('Forest',game);api.enter(forest,'forest');
  assert.equal(forest.getObjects('Discovery_'+level.id)[0].animation,1);
  const home=project.layouts.find(s=>s.name==='Forest').instances.find(i=>i.name==='Discovery_'+level.id);
  assert.equal(forest.getObjects('Discovery_'+level.id)[0].getWidth(),home.width);
  assert.equal(forest.__qf.revealId,level.id);
  for(let i=0;i<24;i++)api.tick(forest);
  assert.equal(forest.__qf.revealId,null);
  assert.equal(forest.getObjects('RevealRing')[0].hidden,true);
});
