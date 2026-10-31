"""Replay Judith's City of Masks dialogue and inventory requirement."""
import json,re
import validate_companion_dynamic as shared
w=shared.w
batch=shared.read('source/judithevents_batch.json')
files=list(dict.fromkeys(x['code'] for x in batch));checks=[];headings=0;seen=set();dynamic=0;rejected=0
for file in files:
    source=(w/'source/CodeEntries'/f'{file}.gml').read_text(encoding='utf-8-sig')
    for match in re.finditer(r'\b(DialogueText|DialogueButton\w+|ChallengeText)\(',source):
        for expr in shared.arguments(source,match.end())[:3 if 'Button' in match[1] else 1]:
            if not shared.literal.search(expr) or expr in seen:continue
            seen.add(expr)
            # Same string(count) syntax; normalize only the accessor name for the parser.
            normalized=expr.replace('InformationReturnNumberOfItems','ExperiencesReturnNumberOfItems')
            keys=re.findall(r'ExperiencesReturnNumberOfItems\(\d+\)',normalized)
            if keys:
                assert len(keys)==1;dynamic+=1
                cases=[{keys[0]:n} for n in ['0','1','2','3','4','100','999']]
            else:cases=[{}]
            for counts in cases:
                en=shared.evaluate(normalized,{},counts)
                if not re.search('[A-Za-z]',en):continue
                ru=shared.translate(en)
                assert ru!=en and not re.search('[A-Za-z]',ru),(file,en,ru)
                assert ru.count('«')==ru.count('»'),ru
                assert re.findall(r'\d+',ru)==re.findall(r'\d+',en),(en,ru)
                checks.append({'source':en,'translation':ru})
            for key in keys:
                for bad in ['', '-1','1.5','unknown']:
                    en=shared.evaluate(normalized,{},{key:bad})
                    assert shared.translate(en)==en,(en,shared.translate(en))
                    rejected+=1
    for first,rest in re.findall(r'DialogueHeadingFirstLetter\("([^"]+)"\);.*?DialogueHeadingRest\("([^"]+)"\);',source,re.S):
        en=first+rest;ru=shared.translate(en)
        assert en!=ru and not re.search('[A-Za-z]',ru),(en,ru)
        headings+=1
assert len(files)==2 and dynamic==1
result=dict(source_files=len(files),unique_visible_expressions=len(seen),checked_variants=len(checks),dynamic_expressions=dynamic,invalid_counts_rejected=rejected,headings_checked=headings,cases=checks)
(w/'build/judith-events-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Judith event checks:',{k:v for k,v in result.items() if k!='cases'})
