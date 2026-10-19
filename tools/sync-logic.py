"""Update inline modules while preserving scene objects, layout and user events."""
import copy, datetime, json
from embedded_logic import ROOT, bootstrap

path = ROOT / 'game.json'
original = path.read_text(encoding='utf-8-sig')
project = json.loads(original)
before = copy.deepcopy(project)
updated = 0

def visit(events):
    global updated
    for event in events:
        if event.get('type') == 'BuiltinCommonInstructions::JsCode':
            source = '\n'.join(event.get('inlineCode', []))
            marker = '\nglobalThis.QuietForestLayouts='
            if marker in source and 'QuietForestGD.enter(runtimeScene,' in source:
                suffix = source[source.index(marker):]
                event['inlineCode'] = (bootstrap() + suffix).splitlines()
                updated += 1
        visit(event.get('events', []))

for scene in project['layouts']:
    visit(scene.get('events', []))
if updated != 6:
    raise RuntimeError(f'Expected six gameplay bootstraps; found {updated}. Project left unchanged.')
for old, new in zip(before['layouts'], project['layouts']):
    assert {k:v for k,v in old.items() if k!='events'} == {k:v for k,v in new.items() if k!='events'}
backup = ROOT / 'backups' / ('game-before-logic-sync-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.json')
backup.write_text(original, encoding='utf-8')
path.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Updated {updated} scene bootstraps; layout preserved. Backup: {backup.name}')
