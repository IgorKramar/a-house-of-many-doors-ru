"""Replay Tybalt quest and boarding dialogue with original source expressions."""
import json,re,itertools
import validate_companion_dynamic as shared
w=shared.w
batch=shared.read('source/tybaltevents_batch.json')
files=list(dict.fromkeys(x['code'] for x in batch));checks=[];headings=0;seen=set();dynamic=set()
pronoun_source=(w/'source/CodeEntries/gml_Script_DecideLowerCrewNameStringAndPronouns.gml').read_text(encoding='utf-8-sig')
pronouns=list(dict.fromkeys(s.lower() for s in re.findall(r'HisHerPronoun = "([^"]+)";',pronoun_source)))
names=['Ирина','Morgan','Капитан А-Б','Dead','Pilot','FirstScreen']
assert set(pronouns)=={'his','her','its'}
for file in files:
    source=(w/'source/CodeEntries'/f'{file}.gml').read_text(encoding='utf-8-sig')
    for match in re.finditer(r'\b(DialogueText|DialogueButton\w+|ChallengeText)\(',source):
        for expr in shared.arguments(source,match.end())[:3 if 'Button' in match[1] else 1]:
            if not shared.literal.search(expr) or expr in seen:continue
            seen.add(expr);normalized=expr.replace('string_lower(HisHerPronoun)','HisHerPronoun')
            variables_text=shared.literal.sub('',normalized)
            if 'NameString' in variables_text:
                cases=[{'NameString':name,'HisHerPronoun':pronoun} for name,pronoun in itertools.product(names,pronouns)]
                dynamic.add(expr)
            elif 'oPlayer.PlayerName' in variables_text:
                cases=[{'oPlayer.PlayerName':name} for name in names];dynamic.add(expr)
            else:cases=[{}]
            for variables in cases:
                en=shared.evaluate(normalized,variables,{})
                if not re.search('[A-Za-z]',en):continue
                ru=shared.translate(en)
                assert ru!=en,(file,en)
                rest=ru
                for k in ['NameString','oPlayer.PlayerName']:
                    if k in variables:
                        assert variables[k] in ru,(en,ru)
                        rest=rest.replace(variables[k],'')
                rest=re.sub(r'\b(?:III|IV)\b','',rest)
                assert not re.search('[A-Za-z]',rest),(en,ru)
                assert ru.count('«')==ru.count('»'),ru
                checks.append({'source':en,'translation':ru})
    for first,rest in re.findall(r'DialogueHeadingFirstLetter\("([^"]+)"\);.*?DialogueHeadingRest\("([^"]+)"\);',source,re.S):
        en=first+rest;ru=shared.translate(en)
        assert en!=ru and not re.search('[A-Za-z]',re.sub(r'\b(?:III|IV)\b','',ru)),(en,ru)
        headings+=1
assert len(files)==3 and len(dynamic)==6,(len(files),len(dynamic))
result=dict(source_files=len(files),unique_visible_expressions=len(seen),checked_variants=len(checks),dynamic_expressions=len(dynamic),custom_names=len(names),possessive_pronouns=pronouns,headings_checked=headings,cases=checks)
(w/'build/tybalt-events-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('Tybalt event checks:',{k:v for k,v in result.items() if k!='cases'})
