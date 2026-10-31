"""Validate composed dialogue using the actual expressions in ten crew scripts.

Read-only coverage checks, not a gameplay test. Counts cover empty inventories,
single items, the ritual threshold, and three-digit quantities independently.
"""
import itertools,json,pathlib,re
w=pathlib.Path(__file__).resolve().parents[2]/'work'
def read(path):return json.loads((w/path).read_text(encoding='utf-8'))
mapping=read('build/translations.json');templates=read('build/templates.json');multi=read('build/templates_multi.json')
literal=re.compile(r'''"[^"]*"|'[^']*' '''.strip())
dynamic=re.compile(r'PlayerName|NameString|SurgeonFirstName|ReturnNumberOfItems')

def arguments(source,start):
    """Split call arguments without splitting quoted text or nested calls."""
    quote=None;level=1;begin=start;args=[]
    for at in range(start,len(source)):
        c=source[at]
        if quote:
            if c==quote:quote=None
        elif c in ['"',"'"]:quote=c
        elif c=='(':level+=1
        elif c==')':
            level-=1
            if level==0:return args+[source[begin:at].strip()]
        elif c==',' and level==1:
            args.append(source[begin:at].strip());begin=at+1
    raise AssertionError('Unclosed call')

expressions=[]
for name in ['Bradley','Rotherford','Banjo','Penpusher','Judith','Tybalt','Violante','Fiona','Ransack','Cromlech']:
    source=(w/f'source/CodeEntries/gml_Script_{name}Dialogue.gml').read_text(encoding='utf-8-sig')
    for call in re.finditer(r'\b(DialogueText|DialogueButton\w+|ChallengeText)\(',source):
        for arg in arguments(source,call.end())[:3 if 'Button' in call[1] else 1]:
            if dynamic.search(literal.sub('',arg)):
                record=(name,arg)
                if record not in expressions:expressions.append(record)

token=re.compile(r'''\s*(?:("[^"]*"|'[^']*')|string\(((?:Cargo|Experiences)ReturnNumberOfItems\(\d+\))\)|([A-Za-z_.][A-Za-z_0-9.]*)|(\+))''',re.S)
def evaluate(expr,variables,counts):
    at=0;parts=[]
    while at<len(expr):
        m=token.match(expr,at);assert m,(expr,expr[at:])
        quoted,count,var,plus=m.groups()
        if quoted:parts.append(quoted[1:-1])
        elif count:parts.append(counts[count])
        elif var:parts.append(variables[var])
        at=m.end()
    return ''.join(parts)

def translate(s,depth=0):
    assert depth<4,s
    if s in mapping:return mapping[s]
    for t in multi:
        separator=r'([0-9]+)' if t.get('numeric') else r'(.+?)'
        m=re.fullmatch(separator.join(re.escape(p) for p in t['parts']),s,re.S)
        if m:
            values=[translate(v,depth+1) for v in m.groups()] if t.get('translate_values') else m.groups()
            return t['ru_parts'][0]+''.join(v+r for v,r in zip(values,t['ru_parts'][1:]))
    for t in templates:
        pre,post=t['prefix'],t['suffix']
        if not s.startswith(pre) or not s.endswith(post) or len(s)<len(pre)+len(post):continue
        value=s[len(pre):len(s)-len(post) if post else None]
        if t.get('numeric') and not re.fullmatch('[0-9]+',value):continue
        if t.get('translate_value'):value=translate(value,depth+1)
        return t['ru_prefix']+value+t['ru_suffix']
    return s

checked=[];rejected=0
for script,expr in expressions:
    count_keys=list(dict.fromkeys(re.findall(r'(?:Cargo|Experiences)ReturnNumberOfItems\(\d+\)',expr)))
    if count_keys:
        cases=[({},dict(zip(count_keys,counts))) for counts in itertools.product(['0','1','3','100'],repeat=len(count_keys))]
    elif 'SurgeonFirstName' in expr:
        crew=(w/'source/CodeEntries/gml_Script_KeepingTrackOfCrewVariables.gml').read_text(encoding='utf-8-sig')
        names=list(dict.fromkeys(re.findall(r'SurgeonFirstName = "([^"]+)"',crew)))
        cases=[({'oPausableGame.SurgeonFirstName':name},{}) for name in names]
    else:
        cases=[({'oPlayer.PlayerName':name,'NameString':name},{}) for name in ['Ирина','Morgan','Эхо','Капитан А-Б']]
    for variables,counts in cases:
        en=evaluate(expr,variables,counts);ru=translate(en)
        assert en!=ru,(script,en)
        remainder=ru
        for name in variables.values():remainder=remainder.replace(name,'')
        assert not re.search('[A-Za-z]',remainder),(script,ru)
        assert ru.count('«')==ru.count('»'),ru
        if counts:assert re.findall(r'\d+',ru)[-len(counts):]==list(counts.values()),(script,ru,counts)
        if 'PlayerName' in expr or 'NameString' in expr:
            assert variables['NameString'] in ru,ru
        checked.append({'script':script,'source':en,'translation':ru})
    if count_keys:
        # Malformed counter values must not enter a numeric template.
        for key in count_keys:
            for bad in ['', '-1', '1.5', 'unknown']:
                values={k:'3' for k in count_keys};values[key]=bad
                en=evaluate(expr,{},values)
                assert translate(en)==en,(script,en)
                rejected+=1

assert len(expressions)==18,len(expressions)
result={'source_expressions':len(expressions),'checked_variants':len(checked),'invalid_counts_rejected':rejected,'cases':checked}
(w/'build/companion-dynamic-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Companion source-expression checks:',{k:v for k,v in result.items() if k!='cases'})
