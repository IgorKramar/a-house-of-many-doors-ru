"""Museum counts and donations, using the manually translated item glossary."""
import json,re

def add_museum(mapping,work,templates,multi):
    batch={int(x['id'].split('_')[1]):x['text'] for x in json.loads((work/'source/museum_batch.json').read_text(encoding='utf-8'))}
    mapping['THE MUSEUM OF UNNATURAL CURIOSITY']='МУЗЕЙ НЕЕСТЕСТВЕННЫХ ДИКОВИН'
    for i in range(112,174,2):
        match=re.fullmatch(r'\[Requires x1 (.+)\. You currently have x',batch[i+1])
        assert match,(i,batch[i+1])
        item=mapping[match[1]]
        mapping[batch[i]]='Передать в дар: '+item+'.'
        templates.append(dict(prefix=batch[i+1],suffix='.]',ru_prefix='[Нужно: '+item+' ×1. У вас: ×',ru_suffix='.]',numeric=True))
    for index,pre,rpre,rpost in json.loads((work/'translation_museum_counts.json').read_text(encoding='utf-8')):
        templates.append(dict(prefix=pre,suffix=batch[index],ru_prefix=rpre,ru_suffix=rpost,numeric=True))
    multi.append(dict(parts=['',batch[91],batch[92]],ru_parts=['Восстановленные обломки надгробий выставлены напоказ. Их здесь ','. Эпитафий из иных миров — тоже ',': одна непонятнее другой.'],numeric=True))
