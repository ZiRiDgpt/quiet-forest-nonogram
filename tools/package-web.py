"""Bundle GDevelop's exported classic scripts in their original order.
This keeps deployment deterministic and reduces many small HTTP requests.
It does not modify the engine sources or the editable project.
"""
import pathlib,re,hashlib
root=pathlib.Path(__file__).resolve().parents[1]/'build'
index=root/'index.html';html=index.read_text(encoding='utf-8')
pattern=re.compile(r'<script\s+src="([^"]+)"[^>]*>\s*</script>')
matches=list(pattern.finditer(html))
if not matches:raise SystemExit('No exported scripts found')
if any(m[1]=='game.bundle.js' for m in matches):raise SystemExit('Already packaged; export again before packaging')
parts=[]
for m in matches:
    p=(root/m[1]).resolve()
    if not p.is_relative_to(root.resolve()):raise SystemExit('Invalid script path')
    source=p.read_text(encoding='utf-8')
    source=re.sub(r'^\s*//# sourceMappingURL=.*$','',source,flags=re.M)
    parts.append('// '+m[1]+'\n'+source+'\n;\n')
bundle='\n'.join(parts)
(root/'game.bundle.js').write_text(bundle,encoding='utf-8')
version=hashlib.sha256(bundle.encode('utf-8')).hexdigest()[:12]
first=True
def replace(m):
    global first
    if first:first=False;return '<script src="game.bundle.js?v='+version+'"></script>'
    return ''
index.write_text(pattern.sub(replace,html),encoding='utf-8')
print('Packaged',len(matches),'exported scripts in their original order')
