"""Read-only replay of visible expressions in Banjo's eight location scripts."""
import json,re,itertools
import validate_companion_dynamic as shared
from generated_banjo import FRAGMENTS
w=shared.w
batch=shared.read('source/banjoevents_batch.json')
files=list(dict.fromkeys(x['code'] for x in batch))
source_expressions=[];checks=[];dynamic=set();rejected=0;headings=0
names=[x['text'].lower() for x in batch if int(x['id'].split('_')[1]) in range(95,118,2)]
for file in files:
    source=(w/'source/CodeEntries'/f'{file}.gml').read_text(encoding='utf-8-sig')
    for match in re.finditer(r'\b(DialogueText|DialogueButton\w+|ChallengeText)\(',source):
        args=shared.arguments(source,match.end())
        for expr in args[:3 if 'Button' in match[1] else 1]:
            if not shared.literal.search(expr):continue
            if expr not in source_expressions:source_expressions.append(expr)
    for first,rest in re.findall(r'DialogueHeadingFirstLetter\("([^"]+)"\);.*?DialogueHeadingRest\("([^"]+)"\);',source,re.S):
        en=first+rest;ru=shared.translate(en)
        assert en!=ru and not re.search('[A-Za-z]',ru),(file,en,ru)
        headings+=1
for expr in source_expressions:
    normalized=expr.replace('string_lower(PreferredFormOfAddress)','PreferredFormOfAddress')
    keys=list(dict.fromkeys(re.findall(r'(?:Cargo|Experiences)ReturnNumberOfItems\(\d+\)',expr)))
    if keys:
        cases=[({},dict(zip(keys,counts))) for counts in itertools.product(['0','1','2','10','100','999'],repeat=len(keys))]
        dynamic.add(expr)
    elif 'PreferredFormOfAddress' in shared.literal.sub('',normalized):
        cases=[({'PreferredFormOfAddress':n},{}) for n in names];dynamic.add(expr)
    else:cases=[({},{})]
    for variables,counts in cases:
        en=shared.evaluate(normalized,variables,counts);ru=shared.translate(en)
        if not re.search('[A-Za-z]',en):continue
        assert ru!=en,(expr,en)
        remainder=ru.replace('just ice','').replace('justice','').replace('Just ice','').replace('Justice','')
        assert not re.search('[A-Za-z]',remainder),(en,ru)
        assert ru.count('«')==ru.count('»'),(en,ru)
        if counts:assert re.findall(r'\d+',ru)[-len(keys):]==list(counts.values()),(en,ru)
        checks.append({'source':en,'translation':ru})
    for key in keys:
        for bad in ['', '-1','1.5','unknown']:
            counts={k:'2' for k in keys};counts[key]=bad
            en=shared.evaluate(normalized,{},counts)
            assert shared.translate(en)==en,(en,shared.translate(en))
            rejected+=1
assert len(files)==8
assert len(dynamic)==7,len(dynamic)
assert len(names)==12
result=dict(source_files=len(files),unique_visible_expressions=len(source_expressions),dynamic_expressions=len(dynamic),forms_of_address=len(names),headings_checked=headings,checked_variants=len(checks),invalid_counts_rejected=rejected,composed_fragment_ids=sorted(FRAGMENTS),cases=checks)
(w/'build/banjo-events-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Banjo event checks:',{k:v for k,v in result.items() if k!='cases'})
