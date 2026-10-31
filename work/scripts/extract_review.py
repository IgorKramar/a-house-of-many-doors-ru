import re,json,pathlib,collections
root=pathlib.Path(__file__).resolve().parents[2]
src=root/'work/source'
strings=json.loads((src/'strings.json').read_text(encoding='utf-8'))
bytext={x['text']:x['id'] for x in strings}
literal=re.compile(r'''"([^"\n]*)"|'([^'\n]*)' '''.strip())
refs=collections.defaultdict(list)
for p in (src/'CodeEntries').glob('*.gml'):
    for n,line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(),1):
        for m in literal.finditer(line):
            text=m.group(1) if m.group(1) is not None else m.group(2)
            if text in bytext: refs[text].append({'code':p.stem,'line':n,'context':line.strip()})
catalog=[]
for x in strings:
    t=x['text']
    if re.search('[A-Za-z]',t) and t in refs:
        catalog.append({**x,'ru':None,'status':'untranslated','refs':refs[t]})
(src/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2),encoding='utf-8')
for label,pattern in [('menu','oStartMenu'),('tutorial','oTutorialDialogueBox'),('ui','oPauseMenu|oDialoguePauseMenu|oCombatPauseMenu|MakeTheTabsWork|DrawStats')]:
    texts=[]
    for x in catalog:
        rr=[r for r in x['refs'] if re.search(pattern,r['code'])]
        if rr: texts.append({'id':x['id'],'text':x['text']})
    (src/(label+'_review.json')).write_text(json.dumps(texts,ensure_ascii=False,indent=2),encoding='utf-8')
    print(label,len(texts),sum(len(x['text'].split()) for x in texts))
print('Referenced string entries:',len(catalog))
print('Entries of at least 8 words:',sum(len(x['text'].split())>=8 for x in catalog))
print('Words in entries of at least 8 words:',sum(len(x['text'].split()) for x in catalog if len(x['text'].split())>=8))
