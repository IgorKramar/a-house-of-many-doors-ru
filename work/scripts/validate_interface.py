"""Check real journal expressions, localized labels and UI drawing recipes."""
import json,re,itertools
import validate_companion_dynamic as shared
w=shared.w
src=(w/'source/CodeEntries/gml_Script_WriteMemoirs.gml').read_text(encoding='utf-8-sig')
calls=[shared.arguments(src,m.end())[0] for m in re.finditer(r'\bJournalText\(',src)]
locations=shared.read('glossary_locations.json')
cases=[]
for expression in calls:
    # Replace the source date expression with a token to exercise the actual body.
    date='DayText + " " + DateOfMonthText + DateSuffix + " of " + MonthText + " " + YearText'
    body=expression
    if body.startswith('DateText + '):body=body[len('DateText + '):]
    if body.startswith(date):body=body[len(date):].strip();assert body.startswith('+');body=body[1:].strip()
    body=re.sub(r'string\((NavigatorFirstName|DiscoveredLocationString)\)',r'\1',body)
    vars=shared.literal.sub('',body)
    if 'NavigatorFirstName' in vars:
        name={'outdated maps':'Sandy','ghost-boxes':'Valeria','compass':'Peter','wind':'Cromlech'}
        nav=next(v for k,v in name.items() if k in body)
        values=[{'NavigatorFirstName':nav,'DiscoveredLocationString':p} for p in locations]
    elif 'oPlayer.PlayerName' in vars:
        values=[{'oPlayer.PlayerName':n} for n in ['Ирина','Morgan','Капитан А-Б']]
    else:
        assert not re.search('[A-Za-z]',vars),(expression,vars)
        values=[{}]
    for variables in values:
        en=shared.evaluate(body,variables,{})
        if en.startswith(': '):en=en[2:]
        ru=shared.translate(en)
        assert ru!=en,(en,ru)
        rest=ru.replace(variables.get('oPlayer.PlayerName','\0'),'')
        assert not re.search('[A-Za-z]',rest),(en,ru)
        assert ru.count('«')==ru.count('»'),ru
        if 'oPlayer.PlayerName' in variables:assert variables['oPlayer.PlayerName'] in ru
        cases.append({'source':en,'translation':ru})
layout=shared.read('build/ui-art-layout.json')
for item in layout:
    x,y,r,b=item['bounds'];a,c,d,e=item['mask']
    assert x>=a and y>=c and r<=d+.01 and b<=e+.01,item
recipes=shared.read('build/ui-art-recipes.json')
for labels in recipes.values():
    for q in labels:
        glyphs={g['Character'] for g in shared.read('build/fonts/'+q['font']+'.json')['glyphs']}
        assert all(ord(c) in glyphs for c in q['text']),q
assert sum(x['sprite']=='sMemoirs' and x['text']=='ЗАМЕТКИ' for x in layout)==20
assert sum(x['sprite']=='sMemoirs' and x['text']=='ПОСЛЕДНЕЕ ПОСЕЩЕНИЕ' for x in layout)==16
for prefix in ['Music: ','Sound: ','Difficulty: ','Fullscreen: ','Text Size: ']:
    assert prefix in shared.mapping
for en in ['ENEMY TURN','PLAYER TURN','(You are here)','RECENTRE','THANK YOU FOR PLAYING']:
    assert shared.translate(en)!=en,en
save_cases=0
for prefix in ['Autosave: ']+[f'Save Slot {i}: ' for i in range(1,4)]:
    for place,localized in locations.items():
        for date in ['0:01, 1/1/2026','23:59, 31/12/2026']:
            en=prefix+place+'#'+date;ru=shared.translate(en)
            assert localized in ru and ru.endswith('#'+date),(en,ru)
            assert not re.search('[A-Za-z]',ru),(en,ru)
            save_cases+=1
result=dict(journal_source_calls=len(calls),journal_variants=len(cases),save_label_variants=save_cases,sprite_families=len(recipes),native_labels=len(layout),cases=cases)
(w/'build/interface-coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print({k:v for k,v in result.items() if k!='cases'})
