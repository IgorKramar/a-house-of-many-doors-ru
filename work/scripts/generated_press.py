"""Inflect recurring assignment text from manually translated location forms.

Rules only produce exact phrases attested in the extracted game, never replace
parts of arbitrary prose. Dynamic salary and name templates preserve the value.
"""
import json,re

def add_press(mapping,work,strings,templates):
    texts={x['text'] for x in strings}
    batch=json.loads((work/'source/press_batch.json').read_text(encoding='utf-8'))
    texts.update(x['text'] for x in batch)
    places=json.loads((work/'glossary_locations.json').read_text(encoding='utf-8'))
    bare={re.sub(r'^(?:The |the )','',k):v for k,v in places.items()}
    about={
        "Waker's Respite":"о Приюте Бодрствующих",
        'Blad Raddock':'о Блад-Рэддоке','Skimmerskard':'о Скиммерскарде',
        'Jabad':'о Джабаде',"Wordhunters' Hearth":'об Очаге Словоловов',
        'Threshold':'о Пороге','New Draden':'о Новом Дрейдене',
        'Byssus':'о Биссусе','Mergulus':'о Мергулусе','Filimenor':'о Филименоре',
    }
    first='Your first assignment is to write a report on '
    for en,ru in list(mapping.items()):
        if en.startswith(first) and ru.startswith('Ваше первое задание — написать репортаж '):
            place=en[len(first):-1]
            about[re.sub(r'^(?:The |the )','',place)]=ru[len('Ваше первое задание — написать репортаж '):-1]
            variant=en.replace('Your first assignment','Your assignment',1)
            if variant in texts:mapping[variant]=ru.replace('Ваше первое задание','Ваше задание',1)
    for en in texts:
        m=re.fullmatch(r'(Write a freelance report|Submit a report) on Current Affairs (?:in|on) (.+)\.',en)
        if m:
            key=re.sub(r'^(?:The |the )','',m[2])
            if key in about:
                mapping[en]=('Написать внештатный репортаж ' if m[1].startswith('Write') else 'Сдать репортаж ')+about[key]+'.'
        m=re.fullmatch(r'\[Because (.+) is nearby, you will not receive a bonus\.\]',en)
        if m:
            key=re.sub(r'^(?:The |the )','',m[1])
            if key in bare:mapping[en]='[Доплаты за дальность не будет: '+bare[key]+' рядом.]'
        m=re.fullmatch(r'\[You will receive an? (\d+) G distance bonus\.\]',en)
        if m:mapping[en]='[Доплата за дальность: '+m[1]+' гиней.]'
        if en.endswith('.'):
            key=re.sub(r'^(?:The |the )','',en[:-1])
            if key in bare:mapping[en]=bare[key]+'.'
    mapping.update({
        'THE HOLLOW TRUMPET':'ПОЛАЯ ТРУБА',
        'THE KEY DETAILS':'КЛЮЧЕВЫЕ ПОДРОБНОСТИ',
        'THE PIONEER':'ПЕРВОПРОХОДЕЦ',
        'SELLING INK CHEAP':'ПЕРО НА ПРОДАЖУ',
        'A DEFINITIVE ARTICLE':'СТАТЬЯ БЕЗ ЛИШНИХ СЛОВ',
    })
    for en,ru in [('TO: ','КОМУ: '),('DEAREST ','С СЕРДЕЧНЫМ ПРИВЕТОМ, '),('DEAR ','ДОБРЫЙ ДЕНЬ, ')]:
        templates.append(dict(prefix=en,suffix=',',ru_prefix=ru,ru_suffix='!'))
    for value in (100,80,50):
        templates.append(dict(prefix=f'[You will earn {value} G plus your distance bonus of ',suffix=' G.]',
            ru_prefix=f'[Гонорар: {value} гиней. Доплата за дальность: ',ru_suffix=' гиней.]',numeric=True))
    for en in texts:
        m=re.fullmatch(r' G\. Because (.+) is nearby, you will not receive a bonus\.\]',en)
        if m:
            key=re.sub(r'^(?:The |the )','',m[1])
            if key in bare:
                templates.append(dict(prefix='[You will receive ',suffix=en,ru_prefix='[Гонорар: ',
                    ru_suffix=' гиней. Доплаты за дальность не будет: '+bare[key]+' рядом.]',numeric=True))
        m=re.fullmatch(r' G plus an? (\d+) G distance bonus\.\]',en)
        if m:
            templates.append(dict(prefix='[You will receive ',suffix=en,ru_prefix='[Гонорар: ',
                ru_suffix=' гиней. Доплата за дальность: '+m[1]+' гиней.]',numeric=True))
    for en in ['You gained ','Gained ']:
        templates.append(dict(prefix=en,suffix=' G!',ru_prefix='Получено гиней: ',ru_suffix='!',numeric=True))
    joined=json.loads((work/'translation_joined.json').read_text(encoding='utf-8'))
    batches={}
    for row in joined:
        group=row['group']
        if group not in batches:
            batches[group]={x['id']:x['text'] for x in json.loads((work/f'source/{group}_batch.json').read_text(encoding='utf-8'))}
        templates.append(dict(prefix=batches[group][row['prefix_id']],suffix=batches[group][row['suffix_id']],
            ru_prefix=row['ru_prefix'],ru_suffix=row['ru_suffix'],translate_value=row.get('translate_value',False)))
