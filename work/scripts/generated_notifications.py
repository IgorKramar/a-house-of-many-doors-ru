"""Compose recurring UI from exact, human-translated item and character names."""
import json,re

def add_notifications(mapping,work,strings,templates):
    texts={x['text'] for x in strings}
    for path in sorted((work/'source').glob('*_batch.json')):
        texts.update(x['text'] for x in json.loads(path.read_text(encoding='utf-8')))
    for en in sorted(texts):
        m=re.fullmatch(r'([+-]\d+) (Relationship|Reputation): (.+)',en)
        if m and m[3] in mapping:
            mapping.setdefault(en,('Отношения: ' if m[2]=='Relationship' else 'Репутация: ')+mapping[m[3]]+' '+m[1])
        m=re.fullmatch(r'(Gained|Lost|You gained|You lost) x(\d+) (.+?)([!.]?)',en)
        if m and m[3] in mapping:
            mapping.setdefault(en,('Получено: ' if 'gained' in m[1].lower() else 'Потеряно: ')+mapping[m[3]]+' ×'+m[2]+m[4])
        m=re.fullmatch(r'\[(Costs|Sells for) ([\d,]+) guineas\.\]',en)
        if m:
            mapping.setdefault(en,('['+'Цена покупки: ' if m[1]=='Costs' else '[Цена продажи: ')+m[2].replace(',',' ')+' гиней.]')
        m=re.fullmatch(r'(Stash away|Retrieve) (.+)\.',en)
        if m and m[2] in mapping:
            mapping.setdefault(en,('Оставить на складе: ' if m[1]=='Stash away' else 'Забрать со склада: ')+mapping[m[2]]+'.')
        # A short stand-alone item label in a black-market menu.
        m=re.fullmatch(r'(?:An? )?(.+)\.',en)
        if m and m[1] in mapping and len(m[1])<55:
            mapping.setdefault(en,mapping[m[1]]+'.')
    acc=json.loads((work/'glossary_character_accusatives.json').read_text(encoding='utf-8'))
    for en,ru in acc.items():mapping['Invite '+en+'.']='Пригласить '+ru+'.'
    mapping.update({
      'A NECESSARY REST':'НЕОБХОДИМЫЙ ОТДЫХ','A BRIEF RESPITE':'КОРОТКАЯ ПЕРЕДЫШКА',
      'GOOD AS NEW':'КАК НОВЕНЬКИЙ','TOO HEAVY!':'ПЕРЕГРУЗ!',
      'AN ADVERTISEMENT':'ОБЪЯВЛЕНИЕ','THE PROSPECTS':'СОИСКАТЕЛИ',
      'ENTERTAINING A GUEST':'ВЕЧЕР С ГОСТЕМ','ENTERTAINING DOZENS OF GUESTS':'ГОСТЯМ НЕТ ЧИСЛА',
      'WHO TO HOST?':'КОГО ПРИГЛАСИТЬ?','THE LATEST GOINGS-ON':'ПОСЛЕДНИЕ НОВОСТИ',
      'YOUR SHED':'ВАШ САРАЙ','ADDING ITEMS':'ОСТАВИТЬ ВЕЩИ','REMOVING ITEMS':'ЗАБРАТЬ ВЕЩИ',
    })
    batch={x['id']:x['text'] for x in json.loads((work/'source/citylife_batch.json').read_text(encoding='utf-8'))}
    for a,b,rpre,rpost in [
      ('citylife_46','citylife_47','[Нужны 10 захватывающих баек и 28 дней работы. Баек у вас: ×','; гонорар — 2000 гиней.]'),
      ('citylife_50','citylife_51','[Нужны 10 кровавых историй и 28 дней работы. Историй у вас: ×','; гонорар — 2000 гиней.]'),
      ('citylife_121','citylife_122','Ремонт кинетопода занял дней: ','.'),
      ('citylife_121','citylife_124','Ремонт кинетопода занял дней: ','.'),
    ]:
        templates.append(dict(prefix=batch[a],suffix=batch[b],ru_prefix=rpre,ru_suffix=rpost,numeric=True))
    for cup,ru in [('cup','чашку'),('cups','чашки')]:
        mapping[batch['citylife_507']+cup+batch['citylife_508']]='«Прекрасно», — вежливо говорит Аббас, принимая '+ru+'. «Спасибо. Вы хотели обсудить что-нибудь определённое или просто поболтать?»'
    templates.append(dict(prefix='"',suffix=batch['citylife_474'],ru_prefix='«',ru_suffix=', это моя жена Бренда», — бормочет он.'))
