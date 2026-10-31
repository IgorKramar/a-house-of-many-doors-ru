"""Check live-name compositions against their decompiled source expressions."""
import itertools,json,re
import validate_companion_dynamic as shared
w=shared.w
tracking=(w/'source/CodeEntries/gml_Script_KeepingTrackOfCrewVariables.gml').read_text(encoding='utf-8-sig')
roles={}
for role,name in re.findall(r'(\w+FirstName) = "([^"]+)"',tracking):
    key='oPausableGame.'+role
    if name not in roles.setdefault(key,[]):roles[key].append(name)
names=['Ирина','Morgan','Эхо','Капитан А-Б']
roles['oPlayer.PlayerName']=names
roles['oPlayer.Surgeon']=['Rotherford','Char Dvetistek','Dr Mobius Vanch','Jhang Ba Sho']
record=(w/'source/CodeEntries/gml_Script_OttoDialogue.gml').read_text(encoding='utf-8-sig')
record_exprs=re.findall(r'\bRecordkeeperString = (.*?);',record)
record_values=[]
for expr in record_exprs:
    if 'FirstName' in expr:
        for name in roles['oPausableGame.RecordkeeperFirstName']:
            if name!='Jack':record_values.append(shared.evaluate(expr,{'oPausableGame.RecordkeeperFirstName':name},{}))
    else:record_values.append(shared.evaluate(expr,{},{}))
roles['RecordkeeperString']=record_values
expressions=[]
for name in ['Tera','Viola','Sandy','Finnegan','Panorama','Otto','Giles','Gustave']:
    source=(w/f'source/CodeEntries/gml_Script_{name}Dialogue.gml').read_text(encoding='utf-8-sig')
    for call in re.finditer(r'\b(DialogueText|DialogueButton\w+|ChallengeText)\(',source):
        for arg in shared.arguments(source,call.end())[:3 if 'Button' in call[1] else 1]:
            masked=shared.literal.sub('',arg)
            if any(v in masked for v in roles) or 'ReturnNumberOfItems' in masked:
                if (name,arg) not in expressions:expressions.append((name,arg))
checked=[]
for script,expr in expressions:
    masked=shared.literal.sub('',expr)
    variables=list(dict.fromkeys(re.findall(r'oPausableGame\.\w+FirstName|oPlayer\.(?:PlayerName|Surgeon)|RecordkeeperString',masked)))
    count_keys=list(dict.fromkeys(re.findall(r'(?:Cargo|Experiences)ReturnNumberOfItems\(\d+\)',expr)))
    for values in itertools.product(*(roles[v] for v in variables)):
        for counts in itertools.product(['0','1','3','100'],repeat=len(count_keys)):
            varmap=dict(zip(variables,values))
            en=shared.evaluate(expr,varmap,dict(zip(count_keys,counts)));ru=shared.translate(en)
            assert en!=ru,(script,en)
            remainder=ru
            if 'oPlayer.PlayerName' in varmap:
                assert varmap['oPlayer.PlayerName'] in ru,ru
                remainder=remainder.replace(varmap['oPlayer.PlayerName'],'')
            assert not re.search('[A-Za-z]',remainder),(script,en,ru)
            assert ru.count('«')==ru.count('»'),ru
            checked.append({'script':script,'source':en,'translation':ru})
assert len(expressions)==11,len(expressions)
result={'source_expressions':len(expressions),'checked_variants':len(checked),'cases':checked}
(w/'build/morecrew-dynamic-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('More crew source-expression checks:',{k:v for k,v in result.items() if k!='cases'})
