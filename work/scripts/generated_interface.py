"""UI composition rules kept separate from save-file and gameplay identifiers."""
import json,pathlib
def add_interface(mapping,w,templates,multi):
    source={x['id']:x['text'] for x in json.loads((w/'source/interface_batch.json').read_text(encoding='utf-8'))}
    ru=json.loads((w/'translations_interface_batch.json').read_text(encoding='utf-8'))
    for i in range(177,191):
        key=f'interface_{i}'
        mapping[source[key][2:]]=ru[key][2:]
    mapping.update({'ENEMY TURN':'ХОД ПРОТИВНИКА','PLAYER TURN':'ВАШ ХОД','A House of Many Doors':'Дом многих дверей'})
    mapping.update({
      'DELETING A HOUSE OF MANY DOORS...':'УДАЛЕНИЕ «ДОМА МНОГИХ ДВЕРЕЙ»...',
      'Autosave: Empty':'Автосохранение: пусто',
      'Waste Disposal of Another World':'Мусоросброс иного мира',
      'Capacity:':'Вместимость:',
      'THE CARGO HOLD IS FULL. THROW SOMETHING AWAY, OR YOU WILL NOT RECEIVE THIS ITEM.':'ТРЮМ ПОЛОН. ВЫБРОСЬТЕ ЧТО-НИБУДЬ, ИНАЧЕ НЕ ПОЛУЧИТЕ ЭТОТ ПРЕДМЕТ.',
      'x1':'×1',
    })
    for en,prefix_ru in [('Autosave: ','Автосохранение: ')]+[(f'Save Slot {n}: ',f'Сохранение {n}: ') for n in range(1,4)]:
        multi.append(dict(parts=[en,'#',''],ru_parts=[prefix_ru,'#',''],translate_values=True))
    for a,b,parts in [
      (168,169,['',' подходит к вам с одной из своих устаревших карт. «Тут совсем рядом — ','», — сообщает она с почти убедительной уверенностью.']),
      (170,171,['',' подходит к вам с открытой коробочкой для призрака. Обитатель исчез. «Рядом — ','», — говорит она и отмечает место на карте.']),
      (172,173,['',' корпит над картами, сверяясь с компасом. «Рядом — ','», — говорит он.']),
      (174,175,['',' поднимает палец, ловя ветер. «Рядом — ','», — рычит он, постукивая тростью по полу. Вы отмечаете место на карте.']),
    ]:
        multi.append(dict(parts=['',source[f'interface_{a}'],source[f'interface_{b}']],ru_parts=parts,translate_values=True))
    templates.extend([
      dict(prefix=source['interface_205'],suffix='',ru_prefix=ru['interface_205'],ru_suffix=''),
      dict(prefix='Hunt down ',suffix='',ru_prefix='Выследить цель: ',ru_suffix='',translate_value=True),
    ])

def write_interface_gml(w,gml):
    # The save list can wrap a long Russian location name onto an extra line.
    # Its clickable rectangle must use the same width/line spacing as the draw call.
    name='gml_Script_SaveSlotRectangleButtonPressed'
    src=(w/f'source/CodeEntries/{name}.gml').read_text(encoding='utf-8-sig')
    assert src.count('string_height(')==2
    src=src.replace('string_height(ButtonText)','string_height_ext(ButtonText, 25, 380)').replace('string_height(TextToDraw)','string_height_ext(TextToDraw, 25, 380)')
    (gml/f'{name}.gml').write_text(src,encoding='utf-8')
    # Journal date headers are visible text only. Calendar state in saves stays English.
    src=(w/'source/CodeEntries/gml_Script_WriteMemoirs.gml').read_text(encoding='utf-8-sig')
    expr='DayText + " " + DateOfMonthText + DateSuffix + " of " + MonthText + " " + YearText'
    assert src.count(expr)==19,src.count(expr)
    src=src.replace(expr,'homd_ru_journal_date()')
    (gml/'gml_Script_WriteMemoirs.gml').write_text(src,encoding='utf-8')
    (gml/'gml_Script_homd_ru_journal_date.gml').write_text('var s,p;s=homd_ru_date();p=string_pos(": ",s);if(p>0)return string_delete(s,1,p+1);return s;',encoding='utf-8')
    # Translate the body independently so it does not depend on the current date.
    src=(w/'source/CodeEntries/gml_Script_JournalText.gml').read_text(encoding='utf-8-sig')
    src=src.replace('TextToDraw = argument0;','TextToDraw = homd_ru_journal_text(argument0);')
    (gml/'gml_Script_JournalText.gml').write_text(src,encoding='utf-8')
    (gml/'gml_Script_homd_ru_journal_text.gml').write_text('''var s,p,tail;s=argument0;p=string_pos(": ",s);
if(p>0) {tail=string_copy(s,p+2,string_length(s)-p-1);return string_copy(s,1,p+1)+homd_ru_text(tail);}
return homd_ru_text(s);''',encoding='utf-8')
