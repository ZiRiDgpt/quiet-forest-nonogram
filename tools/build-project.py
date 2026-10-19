"""Compile editable native GDevelop scenes and the small puzzle adapter.
Run from any directory. Use --output game.generated.json to preserve hand edits.
"""
import argparse, copy, json, pathlib, uuid
from embedded_logic import bootstrap as embedded_bootstrap

ROOT=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--output',default='game.json');args=parser.parse_args()
base=json.loads((ROOT/'backups/game-scaffold.json').read_text(encoding='utf-8'))
levels=json.loads((ROOT/'data/levels.json').read_text(encoding='utf-8'))
manifest_path=ROOT/'data/art-manifest.json'
art_manifest=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
def illustration(key):return art_manifest.get(key,key+'.svg')
project={k:copy.deepcopy(v) for k,v in base.items() if k!='layouts'}
project['gdVersion']={'build':284,'major':5,'minor':6,'revision':0}
project['properties'].update(name='Тихий лес',description='Нонограммы и открытия на лесной поляне',version='0.4.0',windowWidth=1280,windowHeight=800,adaptGameResolutionAtRuntime=False,orientation='landscape',latestCompilationDirectory=str(ROOT/'build'))
project['resources']={'resources':[],'resourceFolders':[]};project['layouts']=[]
text_template=next(o for o in base['layouts'][0]['objects'] if o['type']=='TextObject::Text')
layer=copy.deepcopy(base['layouts'][0]['layers'][0])
assets=ROOT/'assets';assets.mkdir(exist_ok=True)
def asset(name,body,width=100,height=100):
    (assets/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{body}</svg>',encoding='utf-8')
asset('cell-empty.svg','<path fill="#fafaf4" stroke="#a4b19c" stroke-width="1" d="M.5.5h39v39H.5z"/>',40,40)
asset('cell-filled.svg','<rect width="40" height="40" fill="#2d483d"/>',40,40)
asset('cell-cross.svg','<path fill="#fafaf4" stroke="#a4b19c" d="M.5.5h39v39H.5z"/><path d="m14 14 12 12m0-12L14 26" stroke="#8a9b80" stroke-width="2.2"/>',40,40)
asset('button.svg','<rect width="300" height="60" rx="10" fill="#e7ebdc" stroke="#cbd3c0"/>',300,60)
asset('panel.svg','<rect width="600" height="600" rx="18" fill="#eeefe5"/>',600,600)
asset('locked.svg','<circle cx="50" cy="50" r="41" fill="#eef1db" fill-opacity=".2"/><circle cx="50" cy="50" r="32" fill="#f7f5ee"/><text x="50" y="63" text-anchor="middle" font-size="37" font-family="Georgia" fill="#253e34">?</text>')
asset('ring.svg','<circle cx="50" cy="50" r="47" fill="none" stroke="#e8e8b7" stroke-width="2"/>')
heart='M16 27S2 18 2 9C2 1 12-1 16 6c4-7 14-5 14 3 0 9-14 18-14 18Z'
asset('heart-full.svg',f'<path d="{heart}" fill="#be654f"/>',32,30)
asset('heart-empty.svg',f'<path d="{heart}" fill="none" stroke="#bdc0b1" stroke-width="2"/>',32,30)
# The migrated object illustrations live in assets/; no legacy project is required.
for p in sorted(p for p in assets.iterdir() if p.suffix.lower() in ['.svg','.png']):
    project['resources']['resources'].append({'file':'assets/'+p.name,'kind':'image','metadata':'','name':p.name,'smoothed':True,'userAdded':True})
def var(name,value):return {'name':name,'type':'string' if isinstance(value,str) else 'number','value':value}
def instance(scene,name,x,y,w=0,h=0,z=1,variables=None):
    scene['instances'].append({'name':name,'x':x,'y':y,'zOrder':z,'layer':'','angle':0,'customSize':w>0,'width':w,'height':h,'persistentUuid':str(uuid.uuid5(uuid.NAMESPACE_URL,f'quiet-forest/{scene["name"]}/{name}/{x}/{y}')),'numberProperties':[],'stringProperties':[],'initialVariables':[var(k,v) for k,v in (variables or {}).items()]})
    # UUID v4 shape is preferred by the validation helper; stable stored IDs remain stable on rebuild.
    scene['instances'][-1]['persistentUuid']=str(uuid.UUID(scene['instances'][-1]['persistentUuid'],version=4))
def add_object(scene,obj):
    if any(o['name']==obj['name'] for o in scene['objects']):return
    scene['objects'].append(obj);scene['objectsFolderStructure']['children'].append({'objectName':obj['name']})
def txt(scene,name,label,x,y,size=24,color=(37,62,52),z=5,variables=None):
    o=copy.deepcopy(text_template);o.update(name=name,string=label,characterSize=size,bold=False,textAlignment='left',color=dict(zip(['r','g','b'],color)))
    o['content'].update(text=label,characterSize=size,bold=False,textAlignment='left',color=';'.join(map(str,color)))
    o['variables']=[var(k,0 if not isinstance(v,str) else '') for k,v in (variables or {}).items()]
    add_object(scene,o);instance(scene,name,x,y,z=z,variables=variables)
def sprite(scene,name,images,x,y,w,h,z=1,variables=None):
    animations=[]
    for image in images:
        animations.append({'name':image,'useMultipleDirections':False,'directions':[{'looping':False,'timeBetweenFrames':.08,'sprites':[{'hasCustomCollisionMask':False,'image':image,'points':[],'originPoint':{'name':'origine','x':0,'y':0},'centerPoint':{'automatic':True,'name':'centre','x':0,'y':0},'customCollisionMask':[]}]}]})
    o={'name':name,'type':'Sprite','assetStoreId':'','adaptCollisionMaskAutomatically':True,'updateIfNotVisible':False,'variables':[var(k,0 if not isinstance(v,str) else '') for k,v in (variables or {}).items()],'effects':[],'behaviors':[],'animations':animations}
    add_object(scene,o);instance(scene,name,x,y,w,h,z,variables)
def button(scene,name,label,x,y,w=250,h=52):
    sprite(scene,name+'Button',['button.svg'],x,y,w,h,3);txt(scene,name+'Label',label,x+16,y+14,21,z=4)
def scene(name):
    template=base['layouts'][0]
    s={k:copy.deepcopy(v) for k,v in template.items() if k not in ['objects','instances','events','objectsFolderStructure','objectsGroups','variables','behaviorsSharedData']}
    s.update(name=name,mangledName=name,title=name,r=247,v=245,b=238,objects=[],instances=[],events=[],objectsGroups=[],objectsFolderStructure={'folderName':'__ROOT','children':[]},variables=[],behaviorsSharedData=[],layers=[copy.deepcopy(layer)])
    s['uiSettings'].update(zoomFactor=.7,gridWidth=20,gridHeight=20)
    project['layouts'].append(s);return s
def code(source):return {'type':'BuiltinCommonInstructions::JsCode','inlineCode':source.splitlines(),'parameterObjects':'','useStrict':False,'eventsSheetExpanded':False}
geometries={}
forest=scene('Forest')
txt(forest,'Eyebrow','ГЛАВА 01 · ПРОБУЖДЕНИЕ',60,26,16)
txt(forest,'Title','У каждого леса есть свои секреты.',60,62,43)
txt(forest,'Subtitle','Разгадывайте нонограммы и возвращайте жизнь на лесную поляну.',62,122,23,(103,119,101))
txt(forest,'Progress','0 / 4 открытий',1010,42,23)
sprite(forest,'ForestBackground',[illustration('forest')],60,190,1160,435,0)
sprite(forest,'RevealRing',['ring.svg'],0,0,100,100,4)
for i,l in enumerate(levels):
    size=l.get('displaySize',88)
    x=60+l['x']/100*1160-size/2;y=190+l['y']/100*435-size/2
    sprite(forest,'Discovery_'+l['id'],['locked.svg',illustration(l['id'])],x,y,size,size,3)
    sprite(forest,'Card_'+l['id'],['button.svg'],60+i*296,688,272,80,1)
    txt(forest,'CardLabel_'+l['id'],l['title']+'\n'+str(len(l['grid']))+'×'+str(len(l['grid'][0])),72+i*296,699,19,z=2)
txt(forest,'ForestCaption','Нажмите на неизвестный объект',62,642,21,(103,119,101))
def hints(row):
    out=[];n=0
    for v in row+[0]:
        if v:n+=1
        elif n:out.append(n);n=0
    return out or [0]
for l in levels:
    name='Nonogram' if l['id']=='mushroom' else 'Nonogram_'+l['id'];s=scene(name);n=len(l['grid']);cell=42 if n==10 else 30;gx=230;gy=220
    geometries[l['id']]={'x':gx,'y':gy,'cell':cell}
    button(s,'Back','← На поляну',50,28,190)
    txt(s,'Title',l['title'],280,36,34)
    txt(s,'BoardSize',str(n)+' × '+str(n),810,42,20,(103,119,101))
    sprite(s,'HeartsPanel',['button.svg'],942,24,286,60)
    for i in range(3):sprite(s,'Heart'+str(i),['heart-full.svg','heart-empty.svg'],972+i*43,40,32,30,4)
    txt(s,'LivesLabel','3 / 3',1113,43,21,(130,104,88))
    sprite(s,'BoardPanel',['panel.svg'],50,110,740,635,0)
    sprite(s,'ControlsPanel',['panel.svg'],820,110,410,635,0)
    for y in range(n):
        for x in range(n):sprite(s,'Cell',['cell-empty.svg','cell-filled.svg','cell-cross.svg'],gx+x*cell,gy+y*cell,cell,cell,2,{'GridX':x,'GridY':y})
    # Strong separators after each five cells remain separate native sprites.
    for x in range(0,n+1,5):sprite(s,'GridV'+str(x),['cell-filled.svg'],gx+x*cell-1,gy,1.4,n*cell,3)
    for y in range(0,n+1,5):sprite(s,'GridH'+str(y),['cell-filled.svg'],gx,gy+y*cell-1,n*cell,1.4,3)
    for y,row in enumerate(l['grid']):
        line=hints(row)
        for i,num in enumerate(line):txt(s,'Hint',str(num),gx-22*(len(line)-i)-9,gy+y*cell+(cell-18)/2,17,z=4,variables={'Axis':'row','Line':y,'Run':i})
    for x in range(n):
        line=hints([r[x] for r in l['grid']])
        for i,num in enumerate(line):txt(s,'Hint',str(num),gx+x*cell+(cell-16)/2,gy-22*(len(line)-i)-9,17,z=4,variables={'Axis':'col','Line':x,'Run':i})
    txt(s,'Instructions','Клетка за клеткой.\n\nМежду группами — хотя бы\nодна пустая клетка.\nОтметки нельзя стирать.',850,140,24)
    button(s,'Fill','● Закрасить',850,330,345)
    button(s,'Cross','○ Крестик',850,396,345)
    button(s,'Auto','☑ Автокрестики',850,462,345)
    button(s,'Restart','Начать заново',850,528,345)
    txt(s,'Message','Заполняйте клетки по числам.',850,602,19)
    txt(s,'InputHelp','ПКМ — крестик.\nМожно вести по клеткам.',850,674,18,(103,119,101))
    sprite(s,'RewardArt',[illustration(l['id'])],430,230,330,330,20)
reward=scene('Reward');txt(reward,'Eyebrow','НОНОГРАММА РАЗГАДАНА',440,48,17)
txt(reward,'Title','Секрет разгадан',400,92,48)
for l in levels:sprite(reward,'Art_'+l['id'],[illustration(l['id'])],470,205,340,340,3)
txt(reward,'Description','Секрет разгадан. Верните находку на лесную поляну.',330,578,23)
button(reward,'Next','Далее →',520,650,240)
# The old photo placeholder is intentionally not exposed through the playable menu.
photo=copy.deepcopy(next(s for s in base['layouts'] if s['name']=='PhotoWorkshop'));project['layouts'].append(photo)
bootstrap=embedded_bootstrap()
bootstrap+='\nglobalThis.QuietForestLayouts='+json.dumps(geometries)+';\n'
for s in project['layouts']:
    if s['name']=='PhotoWorkshop':continue
    kind='forest' if s['name']=='Forest' else 'reward' if s['name']=='Reward' else 'puzzle'
    id=next((l['id'] for l in levels if s['name']==('Nonogram' if l['id']=='mushroom' else 'Nonogram_'+l['id'])),None)
    init=code(bootstrap+'\nQuietForestGD.enter(runtimeScene,'+json.dumps(kind)+','+json.dumps(id)+');')
    s['events']=[{'type':'BuiltinCommonInstructions::Standard','conditions':[{'type':{'value':'SceneJustBegins'},'parameters':[]}],'actions':[],'events':[init]},code('QuietForestGD.tick(runtimeScene);'),{'type':'BuiltinCommonInstructions::Standard','conditions':[{'type':{'value':'BuiltinCommonInstructions::CompareNumbers'},'parameters':['0','=','1']},{'type':{'value':'MouseButtonFromTextPressed'},'parameters':['"Left"']}],'actions':[{'type':{'value':'Scene'},'parameters':['"Forest"','false']}]}]
    (ROOT/'validation'/f'{s["name"]}.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
project['firstLayout']='Forest'
(ROOT/args.output).write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Wrote {args.output}: {len(project["layouts"])} native scenes, '+str(sum(len(s['instances']) for s in project['layouts']))+' native instances')
