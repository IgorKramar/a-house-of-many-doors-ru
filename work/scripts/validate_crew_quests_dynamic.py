"""Check quest substitutions against original GML, without launching the game."""
import itertools,json,re
import validate_companion_dynamic as shared
w=shared.w
groups=['ashenevents','bishopevents','spireevents','delgadoevents','charevents']
batch={x['id']:x['text'] for x in shared.read('source/ashenevents_batch.json')}
values={
 'oPlayer.PlayerName':['Ирина','Morgan','Эхо','Капитан А-Б'],
 'GunString':[batch[f'ashenevents_{i}'] for i in [263,264]],
 'GunString2':['.',batch['ashenevents_274']],
 'WoundString':['',batch['ashenevents_286']],
 'ApprehensionsString':[f'Gained x{n} Apprehensions.' for n in [0,1,2,10,100]],
}
char={x['id']:x['text'] for x in shared.read('source/charevents_batch.json')}
values['FirstString']=[char[f'charevents_{i}'] for i in [244,245]]
tracking=(w/'source/CodeEntries/gml_Script_KeepingTrackOfCrewVariables.gml').read_text(encoding='utf-8-sig')
values['oPausableGame.GuardCaptainFirstName']=list(dict.fromkeys(re.findall(r'GuardCaptainFirstName = "([^"]+)"',tracking)))
values['oPlayer.Surgeon']=list(dict.fromkeys(n for n in re.findall(r'oPlayer\.Surgeon == "([^"]+)"',tracking) if n not in ['Dead','Gone']))
scripts=list(dict.fromkeys(x['code'] for group in groups for x in shared.read(f'source/{group}_batch.json')))
expressions=[]
for name in scripts:
    source=(w/f'source/CodeEntries/{name}.gml').read_text(encoding='utf-8-sig')
    for call in re.finditer(r'\b(DialogueText|DialogueButton\w+|ChallengeText)\(',source):
        for arg in shared.arguments(source,call.end())[:3 if 'Button' in call[1] else 1]:
            if re.search('[A-Za-z]',shared.literal.sub('',arg)) and (name,arg) not in expressions:expressions.append((name,arg))
checked=[];rejected=0
for script,expr in expressions:
    count_keys=list(dict.fromkeys(re.findall(r'(?:Cargo|Experiences)ReturnNumberOfItems\(\d+\)',expr)))
    mask=shared.literal.sub('',expr)
    mask=re.sub(r'string\((?:Cargo|Experiences)ReturnNumberOfItems\(\d+\)\)','',mask)
    variables=list(dict.fromkeys(re.findall(r'[A-Za-z_.][A-Za-z_0-9.]*',mask)))
    assert all(v in values for v in variables),(script,variables)
    for varvalues in itertools.product(*(values[v] for v in variables)):
        varmap=dict(zip(variables,varvalues))
        for countvalues in itertools.product(['0','1','3','100'],repeat=len(count_keys)):
            counts=dict(zip(count_keys,countvalues))
            en=shared.evaluate(expr,varmap,counts);ru=shared.translate(en)
            assert en!=ru,(script,en)
            player=varmap.get('oPlayer.PlayerName','')
            remainder=ru.replace(player,'') if player else ru
            for key in ['oPausableGame.GuardCaptainFirstName','oPlayer.Surgeon']:
                if key in varmap:
                    expected=shared.translate(varmap[key])
                    assert expected in ru and expected!=varmap[key],(key,expected,ru)
            assert not re.search('[A-Za-z]',remainder.replace(' IV','')),(script,ru)
            assert ru.count('«')==ru.count('»'),ru
            assert not re.search(r'\s+[,.]',ru),ru
            if player:assert player in ru,ru
            if counts:assert re.findall(r'\d+',ru)[-len(counts):]==list(counts.values()),(ru,counts)
            checked.append({'script':script,'source':en,'translation':ru})
    for key in count_keys:
        for bad in ['', '-1', '1.5', 'unknown']:
            counts={k:'3' for k in count_keys};counts[key]=bad
            en=shared.evaluate(expr,{},counts)
            assert shared.translate(en)==en,(script,en)
            rejected+=1
assert len(expressions)==23,len(expressions)
result={'source_expressions':len(expressions),'checked_variants':len(checked),'invalid_counts_rejected':rejected,'cases':checked}
(w/'build/crew-quests-dynamic-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Crew quest source-expression checks:',{k:v for k,v in result.items() if k!='cases'})
