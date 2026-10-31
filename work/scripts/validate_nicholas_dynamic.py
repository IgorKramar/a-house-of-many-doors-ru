"""Check composed Nicholas lines against the actual decompiled expressions.

This verifies dictionary/template coverage; it does not run the game.
"""
import json,pathlib,re
w=pathlib.Path(__file__).resolve().parents[2]/'work'
mapping=json.loads((w/'build/translations.json').read_text(encoding='utf-8'))
templates=json.loads((w/'build/templates.json').read_text(encoding='utf-8'))
source=(w/'source/CodeEntries/gml_Script_NicholasByssusEvent.gml').read_text(encoding='utf-8-sig')
expressions=[]
for line in source.splitlines():
    line=line.strip()
    if line.startswith('DialogueText(') and any(v in line for v in ['NameString','PronounHisHer','oPlayer.PlayerName']):
        expressions.append(line[len('DialogueText('):-2])
    if line.startswith('if (DialogueButtonPressedNew("Give up " + NameString'):
        expressions.append(line[len('if (DialogueButtonPressedNew('):].split(', "", "",')[0])
expressions=list(dict.fromkeys(expressions))
assert len(expressions)==8,expressions
token=re.compile(r'\s*(?:("[^"]*"|\'[^\']*\')|string_lower\((\w+)\)|([A-Za-z_.]+)|(\+))',re.S)
def evaluate(expr,values):
    at=0;parts=[]
    while at<len(expr):
        m=token.match(expr,at)
        assert m,(expr[at:],expr)
        literal,lower,var,plus=m.groups()
        if literal:parts.append(literal[1:-1])
        elif lower:parts.append(values[lower].lower())
        elif var:parts.append(values[var])
        at=m.end()
    return ''.join(parts)
def translate(s,depth=0):
    assert depth<4,s
    if s in mapping:return mapping[s]
    for t in templates:
        pre,post=t['prefix'],t['suffix']
        if not s.startswith(pre) or not s.endswith(post) or len(s)<len(pre)+len(post):continue
        value=s[len(pre):len(s)-len(post) if post else None]
        if t.get('numeric') and not re.fullmatch('[0-9]+',value):continue
        if t.get('translate_value'):value=translate(value,depth+1)
        return t['ru_prefix']+value+t['ru_suffix']
    return s
checked=[]
for he,him,his in [('He','Him','His'),('She','Her','Her'),('It','It','Its')]:
    for name in ['Ирина','Morgan','Эхо']:
        values={'NameString':name,'oPlayer.PlayerName':name,'PronounHeShe':he,'PronounHimHer':him,'PronounHisHer':his}
        for expr in expressions:
            en=evaluate(expr,values);ru=translate(en)
            assert ru!=en,(en,ru)
            assert not re.search('[A-Za-z]',ru.replace(name,'')),ru
            if 'NameString' in expr or 'PlayerName' in expr:assert name in ru,ru
            assert ru.count('«')==ru.count('»'),ru
            checked.append({'source':en,'translation':ru})
(w/'build/nicholas-dynamic-coverage.json').write_text(json.dumps(checked,ensure_ascii=False,indent=2),encoding='utf-8')
print('Nicholas composed dialogue checks:',len(checked),'passed (3 pronoun sets, 3 names).')
