"""Finite variants of translated character quests, preserving source logic."""
import json

def add_crew_quests(mapping,work):
    batch={x['id']:x['text'] for x in json.loads((work/'source/ashenevents_batch.json').read_text(encoding='utf-8'))}
    def en(n):return batch[f'ashenevents_{n}']
    def ru(n):return mapping[en(n)]
    for n in [263,264]:
        mapping[en(265)+en(n)]=ru(265)+ru(n)
    for text,translated in [('.', '.'),(en(274),' и бросает вам пистолет.')]:
        mapping[en(275)+text+en(276)]=ru(275).rstrip()+translated+ru(276)
    for text,translated in [('', ''),(en(286),ru(286))]:
        mapping[en(287)+text]=ru(287)+translated
    char={x['id']:x['text'] for x in json.loads((work/'source/charevents_batch.json').read_text(encoding='utf-8'))}
    ending=' Насколько я вижу, проблема у нас общая. Чар вернётся к алхимикам, где будет несчастна. А вы потратите уйму времени, сил и денег, чтобы ваш собственный работник — ценное вложение — перестал на вас работать».'
    for n,opening in [(244,'«Боюсь, вот тут вы ошибаетесь.'),(245,'«Именно.')]:
        mapping[char[f'charevents_{n}']+char['charevents_246']]=opening+ending
