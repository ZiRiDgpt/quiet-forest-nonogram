"""Install the painted demo, preserving existing UI and unrelated scenes."""
import copy, datetime, json, subprocess, sys
from embedded_logic import ROOT

path=ROOT/'game.json';original=path.read_text(encoding='utf-8-sig')
(ROOT/'backups'/('game-before-painted-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.json')).write_text(original,encoding='utf-8')
manifest={'forest':'forest-painted-v1.png','squirrel':'squirrel-painted-v1.png'}
(ROOT/'data/art-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
levels=json.loads((ROOT/'data/levels.json').read_text(encoding='utf-8'))
sample=json.loads((ROOT/'data/squirrel-painted-grid.json').read_text(encoding='utf-8'))
level=next(l for l in levels if l['id']=='squirrel')
level.update(grid=sample['grid'],x=43,y=23,displaySize=140)
(ROOT/'data/levels.json').write_text(json.dumps(levels,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'logic/levels.js').write_text('(function(root){\nconst levels='+json.dumps(levels,ensure_ascii=False)+';\nif(typeof module!=="undefined")module.exports=levels;else root.NonogramLevels=levels;\n})(typeof window!=="undefined"?window:globalThis);\n',encoding='utf-8')
subprocess.run([sys.executable,str(ROOT/'tools/build-project.py'),'--output','validation/painted-generated.json'],check=True)
generated=json.loads((ROOT/'validation/painted-generated.json').read_text(encoding='utf-8'))
project=json.loads(original)
for r in generated['resources']['resources']:
    if r['name'] in manifest.values() and not any(old['name']==r['name'] for old in project['resources']['resources']):
        project['resources']['resources'].append(r)
for scene in project['layouts']:
    for obj in scene['objects']:
        for anim in obj.get('animations',[]):
            for direction in anim['directions']:
                for frame in direction['sprites']:
                    for key,value in manifest.items():
                        if frame['image']==key+'.svg':frame['image']=value
    if scene['name']=='Forest':
        bg=next(i for i in scene['instances'] if i['name']=='ForestBackground')
        sprite=next(i for i in scene['instances'] if i['name']=='Discovery_squirrel')
        size=level['displaySize']
        sprite.update(x=bg['x']+bg['width']*level['x']/100-size/2,y=bg['y']+bg['height']*level['y']/100-size/2,width=size,height=size,customSize=True)
    if scene['name']=='Nonogram_squirrel':
        fresh=next(s for s in generated['layouts'] if s['name']==scene['name'])
        def board(name):return name in ['Cell','Hint','BoardSize'] or name.startswith(('GridV','GridH'))
        for key in ['objects','instances']:
            scene[key]=[o for o in scene[key] if not board(o['name'])]+[copy.deepcopy(o) for o in fresh[key] if board(o['name'])]
        # Keep all unrelated UI. Update shared grid metadata in existing bootstraps below.
        scene['objectsFolderStructure']['children']=[{'objectName':o['name']} for o in scene['objects']]
    def geometry(events):
        for e in events:
            lines=e.get('inlineCode',[])
            for i,line in enumerate(lines):
                if line.startswith('globalThis.QuietForestLayouts='):
                    data=json.loads(line.split('=',1)[1].rstrip(';'))
                    data['squirrel']={'x':230,'y':220,'cell':30}
                    lines[i]='globalThis.QuietForestLayouts='+json.dumps(data)+';'
            geometry(e.get('events',[]))
    geometry(scene.get('events',[]))
path.write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
subprocess.run([sys.executable,str(ROOT/'tools/sync-logic.py')],check=True)
print('Painted forest and squirrel installed; squirrel board is 15x15.')
