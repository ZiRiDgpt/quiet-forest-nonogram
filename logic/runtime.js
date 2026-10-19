/* GDevelop adapter. Every visible game element is a native Sprite or Text object.
   This file is compiled into scene events by tools/build-project.py. */
(function(root){
  'use strict';
  if(root.QuietForestGD)return;
  const C=root.NonogramCore,S=root.QuietForestSession,levels=root.NonogramLevels;
  const KEY='quiet-forest-gdevelop-v1',INK='37;62;52',GRAY='153;163;147';
  const clone=v=>JSON.parse(JSON.stringify(v));
  const obj=(scene,name)=>scene.getObjects(name)[0];
  const text=(scene,name,value)=>{const o=obj(scene,name);if(o)o.setString(String(value));};
  function state(scene){
    const game=scene.getGame();
    if(!game.__quietForest){
      let saved={completed:[],sessions:{},autoCross:true};
      try{const raw=JSON.parse(localStorage.getItem(KEY));if(raw&&Array.isArray(raw.completed)&&raw.sessions&&typeof raw.sessions==='object'){saved={completed:raw.completed.filter(id=>levels.some(l=>l.id===id)),sessions:raw.sessions,autoCross:raw.autoCross!==false};}}catch(_){saved.storageWarning=true;}
      game.__quietForest=saved;
    }
    return game.__quietForest;
  }
  function persist(scene){
    const s=state(scene);
    try{localStorage.setItem(KEY,JSON.stringify({completed:s.completed,sessions:s.sessions,autoCross:s.autoCross}));}catch(_){s.storageWarning=true;}
  }
  function savePuzzle(scene){
    const q=scene.__qf,s=state(scene);
    if(!q.model)return;
    if(q.model.done||q.model.failed)delete s.sessions[q.id];
    else s.sessions[q.id]=clone(q.model);
    persist(scene);
  }
  function changeScene(scene,name){gdjs.evtTools.runtimeScene.replaceScene(scene,name,false);}
  function sceneFor(id){return id==='mushroom'?'Nonogram':`Nonogram_${id}`;}
  function buttonHit(scene,name){const o=obj(scene,name);return o&&!o.isHidden()&&o.cursorOnObject();}
  function enter(scene,kind,id){
    const shared=state(scene);
    const q=scene.__qf={kind,id,age:0,tool:1,phase:'play',restartUntil:0,lastCell:'',left:false,right:false};
    if(kind==='forest'){
      text(scene,'Progress',`${shared.completed.length} / ${levels.length} открытий`);
      text(scene,'ForestCaption',shared.storageWarning?'Сохранения недоступны: прогресс останется до закрытия игры.':'Нажмите на неизвестный объект, чтобы открыть головоломку.');
      levels.forEach(level=>{const o=obj(scene,`Discovery_${level.id}`);const width=o.getWidth(),height=o.getHeight();o.setAnimation(shared.completed.includes(level.id)?1:0);o.setWidth(width);o.setHeight(height);q[`home_${level.id}`]={x:o.getX(),y:o.getY(),w:o.getWidth(),h:o.getHeight()};text(scene,`CardLabel_${level.id}`,`${level.title}\n${level.grid.length}×${level.grid[0].length}${shared.completed.includes(level.id)?' · '+level.object:''}`);});
      q.revealId=shared.pendingReveal;delete shared.pendingReveal;
      obj(scene,'RevealRing').hide();
      if(q.revealId){text(scene,'ForestCaption',`${levels.find(l=>l.id===q.revealId).object} теперь на лесной поляне.`);obj(scene,'RevealRing').hide(false);}
    }else if(kind==='puzzle'){
      q.level=levels.find(l=>l.id===id);q.model=S.create(q.level.grid,shared.sessions[id],shared.autoCross);
      text(scene,'Title',q.level.title);
      text(scene,'Message','Заполняйте клетки по числам.\nОтметки не стираются.');
      obj(scene,'RewardArt').hide();
      q.geometry=clone(root.QuietForestLayouts[id]);
      q.cells=scene.getObjects('Cell').map(o=>({o,x:o.getVariables().get('GridX').getAsNumber(),y:o.getVariables().get('GridY').getAsNumber(),px:o.getX(),py:o.getY()}));
      paint(scene);savePuzzle(scene);
    }else if(kind==='reward'){
      q.id=shared.rewardId||levels[0].id;
      const level=levels.find(l=>l.id===q.id);
      text(scene,'Title',`Это ${level.object.toLocaleLowerCase('ru')}!`);
      text(scene,'Description','Секрет разгадан. Верните находку на лесную поляну.');
      levels.forEach(l=>obj(scene,`Art_${l.id}`).hide(l.id!==q.id));
    }
  }
  function paint(scene){
    const q=scene.__qf,s=q.model,shared=state(scene);
    for(const {o,x,y} of q.cells)o.setAnimation(s.player[y][x]===1?1:s.player[y][x]===-1?2:0);
    const clues=C.clues(s.grid),rows=s.grid.map((r,y)=>C.completedRuns(r,s.player[y]));
    const cols=s.grid[0].map((_,x)=>C.completedRuns(s.grid.map(r=>r[x]),s.player.map(r=>r[x])));
    for(const h of scene.getObjects('Hint')){
      const v=h.getVariables(),axis=v.get('Axis').getAsString(),line=v.get('Line').getAsNumber(),run=v.get('Run').getAsNumber();
      h.setString(String((axis==='row'?clues.rows:clues.cols)[line][run]));
      h.setColor((axis==='row'?rows:cols)[line][run]?GRAY:INK);
    }
    for(let i=0;i<3;i++)obj(scene,`Heart${i}`).setAnimation(i<s.lives?0:1);
    text(scene,'LivesLabel',`${s.lives} / 3`);
    text(scene,'AutoLabel',`${shared.autoCross?'☑':'☐'} Автокрестики`);
    text(scene,'FillLabel',`${q.tool===1?'● ':'○ '}Закрасить`);
    text(scene,'CrossLabel',`${q.tool===-1?'● ':'○ '}Крестик`);
    text(scene,'BoardSize',`${s.grid[0].length} × ${s.grid.length}`);
  }
  function command(scene,name){
    const q=scene.__qf;
    if(q.kind==='reward'&&name==='next'){
      state(scene).pendingReveal=q.id;changeScene(scene,'Forest');return;
    }
    if(q.kind!=='puzzle'||q.phase!=='play')return;
    if(name==='back'){savePuzzle(scene);changeScene(scene,'Forest');return;}
    if(name==='fill'||name==='cross'){q.tool=name==='fill'?1:-1;paint(scene);return;}
    if(name==='auto'){
      state(scene).autoCross=!state(scene).autoCross;
      if(state(scene).autoCross)q.model.player=C.autoCross(q.model.grid,q.model.player);
      paint(scene);savePuzzle(scene);return;
    }
    if(name==='restart'){
      if(q.age>q.restartUntil){q.restartUntil=q.age+3;text(scene,'RestartLabel','Подтвердить сброс');return;}
      q.model=S.create(q.level.grid,null,state(scene).autoCross);q.restartUntil=0;text(scene,'RestartLabel','Начать заново');text(scene,'Message','Новая попытка. У вас три жизни.');paint(scene);savePuzzle(scene);
    }
  }
  function applyCell(scene,x,y,tool){
    const q=scene.__qf;if(q.phase!=='play')return {changed:false};
    const result=S.apply(q.model,x,y,tool,state(scene).autoCross);
    if(!result.changed)return result;
    if(result.error){q.errorAge=0;q.lostHeart=q.model.lives;text(scene,'Message',q.model.failed?'Жизни закончились.\nНажмите «Начать заново».':'Ошибка: минус одна жизнь.\nЗдесь стоит крестик.');}
    paint(scene);savePuzzle(scene);
    if(result.won){
      q.phase='morph';q.morphAge=0;
      const shared=state(scene);if(!shared.completed.includes(q.id))shared.completed.push(q.id);shared.rewardId=q.id;persist(scene);
      text(scene,'Message','Клетки оживают…');
      obj(scene,'RewardArt').hide(false);obj(scene,'RewardArt').setOpacity(0);
    }
    return result;
  }
  function tick(scene){
    const q=scene.__qf;if(!q)return;
    const dt=Math.min(scene.getElapsedTime()/1000,.1);q.age+=dt;
    const input=scene.getGame().getInputManager(),left=input.isMouseButtonPressed(0),right=input.isMouseButtonPressed(1),released=input.isMouseButtonReleased(0),rightReleased=input.isMouseButtonReleased(1);
    if(q.kind==='forest'){
      if(q.revealId){
        const t=Math.min(q.age/2.2,1),home=q[`home_${q.revealId}`],o=obj(scene,`Discovery_${q.revealId}`),scale=1+.65*(1-t)*(1-t);
        o.setWidth(home.w*scale);o.setHeight(home.h*scale);o.setPosition(home.x-(o.getWidth()-home.w)/2,home.y-(o.getHeight()-home.h)/2-20*(1-t));o.setOpacity(Math.min(255,q.age*550));
        const ring=obj(scene,'RevealRing'),size=home.w*(1+1.4*t);ring.setPosition(home.x+home.w/2-size/2,home.y+home.h/2-size/2);ring.setWidth(size);ring.setHeight(size);ring.setOpacity(255*(1-t));
        if(t===1){ring.hide();q.revealId=null;}
      }
      if(released&&q.age>.2){
        for(const l of levels)if(buttonHit(scene,`Discovery_${l.id}`)||buttonHit(scene,`Card_${l.id}`)){changeScene(scene,sceneFor(l.id));return;}
      }
    }else if(q.kind==='reward'){
      if(released&&q.age>.2&&buttonHit(scene,'NextButton'))command(scene,'next');
    }else if(q.kind==='puzzle'){
      if(q.phase==='morph'){
        q.morphAge+=dt;const t=Math.min(q.morphAge/.8,1),fade=Math.max(0,Math.min((q.morphAge-.7)/1.2,1)),g=q.geometry;
        const targetSize=330/q.model.grid.length,tx=430,ty=230;
        for(const c of q.cells){
          if(q.model.player[c.y][c.x]!==1){c.o.setOpacity(255*(1-t));continue;}
          const ease=1-Math.pow(1-t,3);c.o.setPosition(c.px+(tx+c.x*targetSize-c.px)*ease,c.py+(ty+c.y*targetSize-c.py)*ease);c.o.setWidth(g.cell+(targetSize-g.cell)*ease);c.o.setHeight(g.cell+(targetSize-g.cell)*ease);c.o.setOpacity(255*(1-fade));
        }
        scene.getObjects('Hint').forEach(o=>o.setOpacity(255*(1-t)));
        for(let i=0;i<=q.model.grid.length;i+=5)for(const prefix of ['GridV','GridH']){const line=obj(scene,prefix+i);if(line)line.setOpacity(255*(1-t));}
        obj(scene,'RewardArt').setOpacity(255*fade);
        if(q.morphAge>=2.1)changeScene(scene,'Reward');
        return;
      }
      if(q.restartUntil&&q.age>q.restartUntil){q.restartUntil=0;text(scene,'RestartLabel','Начать заново');}
      for(let i=0;i<3;i++){
        const heart=obj(scene,`Heart${i}`),baseX=972+i*43;
        if(q.errorAge!==undefined&&q.lostHeart===i&&q.errorAge<.6)heart.setX(baseX+Math.sin(q.errorAge*45)*5*(1-q.errorAge/.6));else heart.setX(baseX);
        if(i===0&&q.model.lives===1)heart.setOpacity(210+45*Math.sin(q.age*4));else heart.setOpacity(255);
      }
      if(q.errorAge!==undefined)q.errorAge+=dt;
      if(released&&q.age>.2){for(const [o,cmd] of [['BackButton','back'],['FillButton','fill'],['CrossButton','cross'],['AutoButton','auto'],['RestartButton','restart']])if(buttonHit(scene,o)){command(scene,cmd);break;}}
      if((left||right||released||rightReleased)&&q.age>.2&&!q.model.failed){
        const x=gdjs.evtTools.input.getCursorX(scene,'',0),y=gdjs.evtTools.input.getCursorY(scene,'',0),g=q.geometry;
        const selected=right||rightReleased?-1:q.tool;
        const cx=Math.floor((x-g.x)/g.cell),cy=Math.floor((y-g.y)/g.cell),cell=`${cx},${cy},${selected}`;
        if(!q.left&&!q.right)q.lastCell='';
        if(cell!==q.lastCell){q.lastCell=cell;applyCell(scene,cx,cy,selected);}
      }
    }
    q.left=left;q.right=right;
  }
  root.QuietForestGD={enter,tick,command,applyCell,sceneFor};
})(globalThis);
