import json,pathlib,re
root=pathlib.Path(__file__).resolve().parents[2]; work=root/'work'; build=work/'build'; gml=build/'gml';gml.mkdir(exist_ok=True)
strings=json.loads((work/'source/strings.json').read_text(encoding='utf-8')); byid={str(x['id']):x['text'] for x in strings}
mapping={}
for filename in ['translations_ui.json','translations_extra.json','translations_expansion.json']:
    mapping.update(json.loads((work/filename).read_text(encoding='utf-8')))
for k,v in json.loads((work/'translations_tutorial_ids.json').read_text(encoding='utf-8')).items(): mapping[byid[k]]=v
for group in ['help','arrival','city','ui','inventory','press','citylife','keyquest','trumpetquest','pioneerquest','howling','institutions','museum','glassquest','society','mill','hallow','hallowcrew','wakers','nicholas','nicholasdialogue','fargyle','fargylecrew','startertalk','hallowtalk','fargyletalk','morecrew','midcrew','lorecrew','vanchtalk','elegantcrew','strangecrew','ashentalk','bishoptalk','delgadotalk','spiretalk','chartalk','ashenevents','bishopevents','spireevents','delgadoevents','charevents','rotherfordevents','bradleyevents','interface','penpusherevents','banjoevents','judithevents','tybaltevents','violanteevents']:
    batch={x['id']:x['text'] for x in json.loads((work/'source'/f'{group}_batch.json').read_text(encoding='utf-8'))}
    for k,v in json.loads((work/f'translations_{group}_batch.json').read_text(encoding='utf-8')).items():
        if group=='banjoevents':
            from generated_banjo import FRAGMENTS
            if int(k.split('_')[1]) in FRAGMENTS:continue
        if group=='tybaltevents':
            from generated_tybalt import FRAGMENTS
            if int(k.split('_')[1]) in FRAGMENTS:continue
        if group=='violanteevents':
            from generated_violante import FRAGMENTS
            if int(k.split('_')[1]) in FRAGMENTS:continue
        mapping[batch[k]]=v
from generated_banjo import add_banjo
add_banjo(mapping,work)
from generated_crew_quests import add_crew_quests
add_crew_quests(mapping,work)
from generated_terms import add_terms
add_terms(mapping,work,strings)
templates=json.loads((work/'translation_templates.json').read_text(encoding='utf-8'))
from generated_tybalt import add_tybalt
add_tybalt(mapping,work,templates)
from generated_violante import add_violante
add_violante(work,templates)
from generated_press import add_press
add_press(mapping,work,strings,templates)
from generated_notifications import add_notifications
add_notifications(mapping,work,strings,templates)
multi=json.loads((work/'translation_multi.json').read_text(encoding='utf-8'))
from generated_interface import add_interface,write_interface_gml
add_interface(mapping,work,templates,multi)
from generated_museum import add_museum
add_museum(mapping,work,templates,multi)
from generated_nicholas import add_nicholas
add_nicholas(mapping,work,templates)
from generated_crew_descriptions import add_crew_descriptions
add_crew_descriptions(mapping,work)
# Decompilation normalizes line endings; a runtime multiline literal may still use CRLF.
for en,ru in list(mapping.items()):
    if '\n' in en: mapping[en.replace('\r\n','\n').replace('\n','\r\n')]=ru
stats={'Grit':'Бойкость','Guts':'Стойкость','Graft':'Мастерство','Insight':'Проницательность','Vigilance':'Бдительность','Guile':'Хитрость','Esoterica':'Тайноведение','Spirit':'Дух'}
for stat,ru in stats.items():
    for n in (5,10,20):mapping[f'[Increases {stat} by {n}, and will impact the story.]']=f'[{ru} +{n}. Выбор повлияет на историю.]'
for n in (250,500,750):mapping[f'[You start with an extra {n} guineas. This will also impact the story.]']=f'[В начале игры у вас будет на {n} гиней больше. Выбор повлияет на историю.]'
# Expand the game's random-background variants without retranslating identical prose.
for x in strings:
    text=x['text'];m=re.match(r'^(.*) (\[[^\]]+\])$',text)
    if m and m[1] in mapping and re.search(r'\+(5|10|20|250|500|750)\b',m[2]):
        suffix=m[2]
        for s,r in stats.items():suffix=suffix.replace(s.upper(),r.upper())
        suffix=suffix.replace('guineas','гиней')
        mapping[text]=mapping[m[1]]+' '+suffix
mapping['V2.3']='V2.3 · RU'
def lit(text):
    # GM 1.4 has no C-style quote escape. Compose quoted literal fragments.
    if '"' not in text:return '"'+text+'"'
    if "'" not in text:return "'"+text+"'"
    return ' + '.join(('"'+p+'"') if i%2==0 else "'\"'" for i,p in enumerate(re.split('(")',text)))
init=['global.homd_ru_map=ds_map_create();']
for en,ru in mapping.items():init.append(f'ds_map_add(global.homd_ru_map,{lit(en)},{lit(ru)});')
(gml/'gml_Script_homd_ru_init.gml').write_text('\n'.join(init),encoding='utf-8')
prefixes={k:v for k,v in mapping.items() if k.endswith(': ') or k=='Are you happy with that choice, '}
text=['var s, p, tail, tail2, count_value0, count_value1, count_value2, count_value3;','s=argument0;','if (!is_string(s)) return s;','switch(s) {']
for en,ru in mapping.items(): text.append(f'case {lit(en)}: return {lit(ru)};')
text.append('}')

from gml_numeric_template import compile_numeric_template
for item in multi:
    if len(item['parts'])>3:
        text+=compile_numeric_template(item,lit)
        continue
    pre,mid,post=item['parts'];rpre,rmid,rpost=item['ru_parts']
    condition=(f'string_pos({lit(pre)},s)==1 && ' if pre else '')+f'string_length(s)>={len(pre)+len(mid)+len(post)+2}'
    if post: condition+=f' && string_copy(s,string_length(s)-{len(post)-1},{len(post)})=={lit(post)}'
    text+=['if ('+condition+') {',f'p=string_pos({lit(mid)},s);',f'if (p>{len(pre)+1}) {{',
           f'tail=string_copy(s,{len(pre)+1},p-{len(pre)+1});',
           f'tail2=string_copy(s,p+{len(mid)},string_length(s)-p-{len(mid)+len(post)-1});']
    if item.get('numeric'):text.append('if (string_length(tail)>0 && string_digits(tail)==tail && string_length(tail2)>0 && string_digits(tail2)==tail2)')
    first='homd_ru_text(tail)' if item.get('translate_values') else 'tail'
    second='homd_ru_text(tail2)' if item.get('translate_values') else 'tail2'
    text+=[f'return {lit(rpre)}+{first}+{lit(rmid)}+{second}+{lit(rpost)};','}','}']
for item in templates:
    pre,post=item['prefix'],item['suffix']
    condition=(f'string_pos({lit(pre)},s)==1 && ' if pre else '')+f'string_length(s)>={len(pre)+len(post)}'
    if post: condition+=f' && string_copy(s,string_length(s)-{len(post)-1},{len(post)})=={lit(post)}'
    text+=['if ('+condition+') {',f'tail=string_copy(s,{len(pre)+1},string_length(s)-{len(pre)+len(post)});']
    if item.get('numeric'):text.append('if (string_length(tail)>0 && string_digits(tail)==tail)')
    value='homd_ru_text(tail)' if item.get('translate_value') else 'tail'
    text.append(f'return {lit(item["ru_prefix"])}+{value}+{lit(item["ru_suffix"])};')
    text.append('}')
for en,ru in prefixes.items():
    text+=['if (string_pos('+lit(en)+',s)==1) {',f'tail=string_delete(s,1,{len(en)});', 'tail=homd_ru_text(tail);',f'return {lit(ru)}+tail;','}']
en='"Steady on," says Rotherford. "You\'re in no condition to go chasing down miscreants, '
end='. I want to make sure your brain wasn\'t too badly damaged - let me ask you some questions about your past."'
text+=['if (string_pos('+lit(en)+',s)==1) {', 'p=string_pos('+lit(end)+',s);',f'if (p>0) return "«Не спешите, — говорит Ротерфорд. — Вам сейчас не до погони за негодяями, "+string_copy(s,{len(en)+1},p-{len(en)+1})+". Надо убедиться, что ваш мозг пострадал не слишком сильно. Позвольте задать несколько вопросов о вашем прошлом».");'.replace('».");','».";'),'}','return s;']
(gml/'gml_Script_homd_ru_text.gml').write_text('\n'.join(text),encoding='utf-8')
signatures={'draw_text':(3,2),'draw_text_ext':(5,2),'string_width':(1,0),'string_height':(1,0),'string_width_ext':(3,0),'string_height_ext':(3,0)}
for fn,(count,pos) in signatures.items():
    args=[f'argument{i}' for i in range(count)];args[pos]='homd_ru_text('+args[pos]+')'
    body=('return ' if fn.startswith('string_') else '')+fn+'('+','.join(args)+');'
    (gml/('gml_Script_homd_ru_'+fn+'.gml')).write_text(body,encoding='utf-8')
# Preserve the original drop-cap behaviour, translating the entire heading together.
(gml/'gml_Script_DialogueHeadingFirstLetter.gml').write_text('SurfaceCurrentX+=22; LetterToDraw=argument0; homd_ru_head_x=SurfaceCurrentX; homd_ru_head_y=SurfaceCurrentY; WidthOfFirstLetter=0;',encoding='utf-8')
(gml/'gml_Script_DialogueHeadingRest.gml').write_text('''
var full, first, rest;
SurfaceCurrentX-=22;
full=homd_ru_text(LetterToDraw+argument0);
first=string_char_at(full,1);rest=string_delete(full,1,1);
draw_set_colour(make_colour_rgb(81,53,39));draw_set_halign(fa_left);
draw_set_font(fFirstLetterOfDialogueHeading);
draw_text(homd_ru_head_x,homd_ru_head_y-1,first);
WidthOfFirstLetter=string_width(first)+2;
draw_set_font(fDialogueHeading);draw_text(homd_ru_head_x+WidthOfFirstLetter,SurfaceCurrentY,rest);
draw_set_halign(fa_center);draw_set_colour(c_black);
SurfaceCurrentY=SurfaceCurrentY+string_height(first)+10;
SurfaceCurrentX+=22;
''',encoding='utf-8')
# Date formatting changes only the displayed date, not the English calendar in saves.
months=dict(zip(['Broach','Tenebres','Maunder','Echoweb','Lacuna','Crossroads','Nugatory','Dustfall','Eidolon','Quietus','Sempitern','Knell'],['Броача','Тенебреса','Мондера','Эховеба','Лакуны','Перепутий','Ньюгатори','Пылепада','Эйдолона','Квиетуса','Семпитерна','Кнелла']))
date=['var m; m=oPlayer.MonthOfTheYear; switch(m) {']
for en,ru in months.items():date.append(f'case {lit(en)}: m={lit(ru)}; break;')
date+=['}', 'return homd_ru_text(string(global.Region))+": "+homd_ru_text(oPlayer.DayOfTheWeek)+", "+string(oPlayer.DayOfTheMonth)+" "+m+" "+string(oPlayer.Year);']
(gml/'gml_Script_homd_ru_date.gml').write_text('\n'.join(date),encoding='utf-8')
date_expr='DayText + " " + DateOfMonthText + DateSuffix + " of " + MonthText + " " + YearText'
for name in ['gml_Script_DrawDate','gml_Script_DialogueBoxOtherTabs']:
    source=(work/'source/CodeEntries'/(name+'.gml')).read_text(encoding='utf-8-sig')
    assert source.count(date_expr)==3,(name,source.count(date_expr))
    (gml/(name+'.gml')).write_text(source.replace(date_expr,'homd_ru_date()'),encoding='utf-8')
write_interface_gml(work,gml)
(build/'translations.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
(build/'templates.json').write_text(json.dumps(templates,ensure_ascii=False,indent=2),encoding='utf-8')
(build/'templates_multi.json').write_text(json.dumps(multi,ensure_ascii=False,indent=2),encoding='utf-8')
(build/'hooks.json').write_text(json.dumps(list(signatures)),encoding='utf-8')
print('Translations:',len(mapping),'source words:',sum(len(k.split()) for k in mapping))
# Build typography/graphical-label hooks last, after the base hook manifest is written.
import prepare_ui_art
