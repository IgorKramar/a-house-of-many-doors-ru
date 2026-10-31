"""Check the source expressions added for Harmony through Jhang Ba Sho."""
import itertools,json,re
import validate_companion_dynamic as shared
w=shared.w
expressions=[]
for name in ['Harmony','Valeria','Augustus','Peter','Abbas','Jack','Vanch','Gladys','Genevieve','Lucetta','JhangBaSho']:
    source=(w/f'source/CodeEntries/gml_Script_{name}Dialogue.gml').read_text(encoding='utf-8-sig')
    for call in re.finditer(r'\b(DialogueText|DialogueButton\w+|ChallengeText)\(',source):
        for arg in shared.arguments(source,call.end())[:3 if 'Button' in call[1] else 1]:
            if re.search(r'PlayerName|ReturnNumberOfItems',shared.literal.sub('',arg)):
                if (name,arg) not in expressions:expressions.append((name,arg))
checked=[];rejected=0
for script,expr in expressions:
    count_keys=list(dict.fromkeys(re.findall(r'(?:Cargo|Experiences)ReturnNumberOfItems\(\d+\)',expr)))
    names=['Ирина','Morgan','Эхо','Капитан А-Б'] if 'PlayerName' in shared.literal.sub('',expr) else ['']
    for name in names:
        for values in itertools.product(['0','1','3','100'],repeat=len(count_keys)):
            counts=dict(zip(count_keys,values))
            en=shared.evaluate(expr,{'oPlayer.PlayerName':name},counts);ru=shared.translate(en)
            assert en!=ru,(script,en)
            assert not re.search('[A-Za-z]',ru.replace(name,'') if name else ru),(script,ru)
            assert ru.count('«')==ru.count('»'),(script,ru)
            if name:assert name in ru,(script,ru)
            if counts:assert re.findall(r'\d+',ru)[-len(counts):]==list(counts.values()),(script,ru,counts)
            checked.append({'script':script,'source':en,'translation':ru})
    for key in count_keys:
        for bad in ['', '-1', '1.5', 'unknown']:
            values={k:'3' for k in count_keys};values[key]=bad
            en=shared.evaluate(expr,{},values)
            assert shared.translate(en)==en,(script,en)
            rejected+=1
assert len(expressions)==16,len(expressions)
result={'source_expressions':len(expressions),'checked_variants':len(checked),'invalid_counts_rejected':rejected,'cases':checked}
(w/'build/current-crew-dynamic-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Current crew source-expression checks:',{k:v for k,v in result.items() if k!='cases'})
