"""Localize complete Tybalt dialogue with player/custom crew names intact."""
import json
FRAGMENTS={32,41,42,160,161,199,200,201,203,245,246}

def add_tybalt(mapping,w,templates):
    batch={int(x['id'].split('_')[1]):x['text'] for x in json.loads((w/'source/tybaltevents_batch.json').read_text(encoding='utf-8'))}
    ru=json.loads((w/'translations_tybaltevents_batch.json').read_text(encoding='utf-8'))
    for pre,post,rpre,rpost in [
        ('"',batch[32],'«',ru['tybaltevents_32']),
        (batch[41],batch[42],ru['tybaltevents_41'],ru['tybaltevents_42']),
        (batch[160],batch[161],ru['tybaltevents_160'],ru['tybaltevents_161']),
        ('',batch[203],'Потеря в охране: ','.'),
    ]:
        templates.append(dict(prefix=pre,suffix=post,ru_prefix=rpre,ru_suffix=rpost))
    for middle,post,rpost in [
        (200,201,' из вашей охраны; грудь залита кровью. Не ваша ли это была пуля? Вы надеетесь, что нет.'),
        (245,246,' из вашей охраны; грудь залита кровью.'),
    ]:
        for pronoun in ['his','her','its']:
            templates.append(dict(prefix=batch[199],suffix=batch[middle]+pronoun+batch[post],ru_prefix=ru['tybaltevents_199'],ru_suffix=rpost))
    mapping['A SHADECORE SCORPIOPEDE']='СКОРПИОПОД ШЕЙДКОРА'
