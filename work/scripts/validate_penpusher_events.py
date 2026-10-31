"""Check actual rendered source expressions in Penpusher's three location scenes."""
import json,re
import validate_companion_dynamic as shared
w=shared.w
batch=shared.read('source/penpusherevents_batch.json')
files=list(dict.fromkeys(x['code'] for x in batch));checks=[];headings=0;seen=set()
for file in files:
    source=(w/'source/CodeEntries'/f'{file}.gml').read_text(encoding='utf-8-sig')
    for match in re.finditer(r'\b(DialogueText|DialogueButton\w+|ChallengeText)\(',source):
        for expr in shared.arguments(source,match.end())[:3 if 'Button' in match[1] else 1]:
            if not shared.literal.search(expr) or expr in seen:continue
            seen.add(expr);en=shared.evaluate(expr,{},{})
            if not re.search('[A-Za-z]',en):continue
            ru=shared.translate(en)
            assert ru!=en and not re.search('[A-Za-z]',ru),(file,en,ru)
            assert ru.count('«')==ru.count('»'),ru
            assert re.findall(r'\d+',ru)==re.findall(r'\d+',en),(en,ru)
            checks.append({'source':en,'translation':ru})
    for first,rest in re.findall(r'DialogueHeadingFirstLetter\("([^"]+)"\);.*?DialogueHeadingRest\("([^"]+)"\);',source,re.S):
        en=first+rest;ru=shared.translate(en)
        assert en!=ru and not re.search('[A-Za-z]',ru),(en,ru)
        headings+=1
assert len(files)==3
result=dict(source_files=len(files),unique_visible_expressions=len(checks),headings_checked=headings,cases=checks)
(w/'build/penpusher-events-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Penpusher event checks:',{k:v for k,v in result.items() if k!='cases'})
