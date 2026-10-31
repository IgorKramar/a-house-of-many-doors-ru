"""Check rendered names in the last five onboard dialogue scripts."""
import itertools,json,re
import validate_companion_dynamic as shared
w=shared.w
tracking=(w/'source/CodeEntries/gml_Script_KeepingTrackOfCrewVariables.gml').read_text(encoding='utf-8-sig')
roles={}
for role,name in re.findall(r'(\w+FirstName) = "([^"]+)"',tracking):
    if name not in roles.setdefault('oPausableGame.'+role,[]):roles['oPausableGame.'+role].append(name)
for role,name in re.findall(r'oPlayer\.(Pilot|Navigator|Lookout|Surgeon|ChiefEngineer|Lightbearer|GuardCaptain|Recordkeeper) == "([^"]+)"',tracking):
    if name not in ['Dead','Gone'] and name not in roles.setdefault('oPlayer.'+role,[]):roles['oPlayer.'+role].append(name)
roles['oPlayer.PlayerName']=['Ирина','Morgan','Эхо','Капитан А-Б']
# Lower crew may be renamed by the user; unrecognised names must survive intact.
roles['NameString']=['Ирина','Morgan','Капитан А-Б','Abbott Baggs','Двенадцатый','Twelve']
expressions=[]
for name in ['Ashen','Bishop','DrDelgado','Spire','Char']:
    source=(w/f'source/CodeEntries/gml_Script_{name}Dialogue.gml').read_text(encoding='utf-8-sig')
    for call in re.finditer(r'\b(DialogueText|DialogueButton\w+|ChallengeText)\(',source):
        for arg in shared.arguments(source,call.end())[:3 if 'Button' in call[1] else 1]:
            masked=shared.literal.sub('',arg)
            if any(v in masked for v in roles):
                if (name,arg) not in expressions:expressions.append((name,arg))
checked=[]
for script,expr in expressions:
    masked=shared.literal.sub('',expr)
    variables=list(dict.fromkeys(re.findall(r'oPausableGame\.\w+FirstName|oPlayer\.\w+|NameString',masked)))
    for values in itertools.product(*(roles[v] for v in variables)):
        varmap=dict(zip(variables,values))
        en=shared.evaluate(expr,varmap,{});ru=shared.translate(en)
        assert en!=ru,(script,en)
        remainder=ru
        for key,value in varmap.items():
            expected=value if key=='oPlayer.PlayerName' else shared.translate(value)
            assert expected in ru,(script,value,expected,ru)
            if key not in ['NameString','oPlayer.PlayerName']:
                assert expected!=value and not re.search('[A-Za-z]',expected.replace(' IV','')),(key,value)
            remainder=remainder.replace(expected,'')
        assert not re.search('[A-Za-z]',remainder),(script,ru)
        assert ru.count('«')==ru.count('»'),(script,ru)
        checked.append({'script':script,'source':en,'translation':ru})
assert len(expressions)==18,len(expressions)
result={'source_expressions':len(expressions),'checked_variants':len(checked),'cases':checked}
(w/'build/lastcrew-dynamic-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Last crew source-expression checks:',{k:v for k,v in result.items() if k!='cases'})
