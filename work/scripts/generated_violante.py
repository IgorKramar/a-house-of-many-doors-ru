"""Keep the captain's name intact in Violante's shivering dialogue."""
import json
FRAGMENTS={27,28}

def add_violante(w,templates):
    batch={int(x['id'].split('_')[1]):x['text'] for x in json.loads((w/'source/violanteevents_batch.json').read_text(encoding='utf-8'))}
    ru=json.loads((w/'translations_violanteevents_batch.json').read_text(encoding='utf-8'))
    templates.append(dict(prefix=batch[27],suffix=batch[28],ru_prefix=ru['violanteevents_27'],ru_suffix=ru['violanteevents_28']))
