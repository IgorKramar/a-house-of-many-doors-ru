import json,pathlib,re
w=pathlib.Path(__file__).resolve().parents[2]/'work'
def read(p):return json.loads((w/p).read_text(encoding='utf-8'))
mapping=read('build/translations.json')
for en,ru in mapping.items():
    assert ru and '\ufffd' not in ru and not re.search('[\x00-\x08\x0b-\x1f]',ru),en
    assert ru.count('«')==ru.count('»'),(en,ru)
    if en.startswith('[') and en.endswith(']'):assert ru.startswith('[') and ru.endswith(']'),(en,ru)
templates=read('build/templates.json')
multi=read('build/templates_multi.json')
for item in multi:
    assert len(item['parts'])==len(item['ru_parts']),item
    ru='123'.join(item['ru_parts'])
    assert ru.count('«')==ru.count('»') and '\ufffd' not in ru,item
for item in templates:
    ru=item['ru_prefix']+'ИМЯ'+item['ru_suffix']
    assert ru.count('«')==ru.count('»'),item
    assert '\ufffd' not in ru,item
def matches_template(en,t):
    pre,post=t['prefix'],t['suffix']
    if not en.startswith(pre) or not en.endswith(post) or len(en)<len(pre)+len(post):return False
    value=en[len(pre):len(en)-len(post) if post else None]
    return bool(re.fullmatch('[0-9]+',value)) if t.get('numeric') else True

for group in ['help','arrival','city','inventory','ui','press','citylife','keyquest','trumpetquest','pioneerquest','howling','institutions','museum','glassquest','society','mill','hallow','hallowcrew','wakers','nicholas','nicholasdialogue','fargyle','fargylecrew','startertalk','hallowtalk','fargyletalk','morecrew','midcrew','lorecrew','vanchtalk','elegantcrew','strangecrew','ashentalk','bishoptalk','delgadotalk','spiretalk','chartalk','ashenevents','bishopevents','spireevents','delgadoevents','charevents','rotherfordevents','bradleyevents','interface','penpusherevents','banjoevents','judithevents','tybaltevents','violanteevents']:
    missing=[]
    for x in read(f'source/{group}_batch.json'):
        # Preserve real contributors' names, handles, studio names and backer credits.
        if group=='interface' and int(x['id'].rsplit('_',1)[1]) in [89,91,93,95,97,99,101,103,105]:continue
        en=x['text']
        if group=='tybaltevents':
            # Full player/crew-name expressions are replayed by validate_tybalt_events.py.
            from generated_tybalt import FRAGMENTS
            if int(x['id'].split('_')[1]) in FRAGMENTS:continue
        if group=='banjoevents':
            from generated_banjo import FRAGMENTS,PAIRS
            if int(x['id'].split('_')[1]) in FRAGMENTS:
                # Verify finite composed variants rather than translating sentence fragments alone.
                b={int(y['id'].split('_')[1]):y['text'] for y in read('source/banjoevents_batch.json')}
                for a,z in PAIRS:
                    if int(x['id'].split('_')[1]) not in (a,z):continue
                    for n in range(95,118,2):assert b[a]+b[n].lower()+b[z] in mapping
                continue
        templated=any(en==t['prefix'] or en==t['suffix'] or matches_template(en,t) for t in templates) or any(en in t['parts'] for t in multi)
        heading=any(c+en in mapping for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        if en not in mapping and not templated and not heading and (group=='inventory' or len(en.split())>=3):
            missing.append({'id':x['id'],'text':en})
    print(group,'not exact matched:',json.dumps(missing,ensure_ascii=False))
print('Editorial syntax checks passed:',len(mapping),'entries')
