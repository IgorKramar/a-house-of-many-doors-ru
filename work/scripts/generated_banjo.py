"""Compose the finite forms of address without modifying quest-state values."""
import json

FRAGMENTS={118,119,121,122,128,129,148,149,161,162,176}
PAIRS=[(118,119),(121,122),(128,129),(148,149),(161,162),(128,176)]

def add_banjo(mapping,work):
    batch={int(x['id'].split('_')[1]):x['text'] for x in json.loads((work/'source/banjoevents_batch.json').read_text(encoding='utf-8'))}
    translated=json.loads((work/'translations_banjoevents_batch.json').read_text(encoding='utf-8'))
    ru=lambda n:translated[f'banjoevents_{n}']
    for n in range(95,118,2):
        for pre,post in PAIRS:
            en=batch[pre]+batch[n].lower()+batch[post]
            result=ru(pre)+ru(n)+ru(post)
            assert result.count('«')==result.count('»'),(n,pre,post,result)
            mapping[en]=result
    mapping.update({
        'AROZIM':'АРОЗИМ', 'THE GOLEMGARDE':'ГОЛЕМГАРД',
        'THE PROCURER':'ЗАКУПЩИЦА', 'CARAPAS':'КАРАПАС',
        "BUZZARDS' OMEN":'ЗНАМЕНИЕ СТЕРВЯТНИКОВ',
        'FROGBIT SMUT':'ВОДОКРАСНАЯ ГНИЛЬ',
        'THE SCARS OF SHENG':'ШРАМЫ ШЭНА',
        'THE MEMORY-BOX':'ШКАТУЛКА ВОСПОМИНАНИЙ',
    })
