"""Check all four alternative homes and return visits against the source."""
import json,re
import validate_companion_dynamic as shared
w=shared.w
batch=shared.read('source/violanteevents_batch.json')
files=list(dict.fromkeys(x['code'] for x in batch));seen=set();checks=[];headings=0;dynamic=0
for file in files:
    source=(w/'source/CodeEntries'/f'{file}.gml').read_text(encoding='utf-8-sig')
    for call in re.finditer(r'\b(DialogueText|DialogueButton\w+|ChallengeText)\(',source):
        for expr in shared.arguments(source,call.end())[:3 if 'Button' in call[1] else 1]:
            if not shared.literal.search(expr) or expr in seen:continue
            seen.add(expr)
            if 'oPlayer.PlayerName' in shared.literal.sub('',expr):
                cases=[{'oPlayer.PlayerName':name} for name in ['Ирина','Morgan','Капитан А-Б','Dead','Pilot']];dynamic+=1
            else:cases=[{}]
            for variables in cases:
                en=shared.evaluate(expr,variables,{})
                if not re.search('[A-Za-z]',en):continue
                ru=shared.translate(en);assert ru!=en,(file,en)
                rest=ru
                if variables:
                    name=variables['oPlayer.PlayerName'];assert name in ru;rest=rest.replace(name,'')
                assert not re.search('[A-Za-z]',rest),(en,ru)
                assert ru.count('«')==ru.count('»'),ru
                checks.append({'source':en,'translation':ru})
    for first,rest in re.findall(r'DialogueHeadingFirstLetter\("([^"]+)"\);.*?DialogueHeadingRest\("([^"]+)"\);',source,re.S):
        en=first+rest;ru=shared.translate(en);assert en!=ru and not re.search('[A-Za-z]',ru),(en,ru)
        headings+=1
assert len(files)==4 and dynamic==1
result=dict(source_files=len(files),unique_visible_expressions=len(seen),checked_variants=len(checks),dynamic_expressions=dynamic,headings_checked=headings,cases=checks)
(w/'build/violante-events-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Violante event checks:',{k:v for k,v in result.items() if k!='cases'})
