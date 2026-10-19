"""Load inline game modules without Electron's ambient CommonJS globals."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def bootstrap():
    sources = '\n'.join((ROOT / 'logic' / name).read_text(encoding='utf-8')
                        for name in ['core.js', 'levels.js', 'session.js', 'runtime.js'])
    # Electron preview exposes module/require, but these modules are already inline.
    # Lexical parameters keep their browser branch consistent in every export target.
    return '(function(module, exports, require){\n' + sources + '\n})(undefined, undefined, undefined);'
