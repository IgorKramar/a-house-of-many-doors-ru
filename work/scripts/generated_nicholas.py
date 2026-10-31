"""Translate the three attested pronoun sets used by the Byssus sacrifice scene.

Keep names as runtime values, and never change gender or identity in saves.
The source helper emits He/Him/His, She/Her/Her, or It/It/Its (mycena).
"""
import json

def add_nicholas(mapping, work, templates):
    dialogue=json.loads((work/'source/nicholasdialogue_batch.json').read_text(encoding='utf-8'))
    desc={int(x['id'].split('_')[1]):x['text'] for x in dialogue}
    for wound in ['',desc[5],desc[6]]:
        for sanity in ['',desc[7]]:
            mapping[desc[4]+wound+sanity]=mapping[desc[4]]+mapping.get(wound,'')+mapping.get(sanity,'')
    batch=json.loads((work/'source/nicholas_batch.json').read_text(encoding='utf-8'))
    b={int(x['id'].split('_')[1]):x['text'] for x in batch}
    for subject,object_,possessive,ru_subject,ru_object,ru_possessive,ru_obedient in [
        ('He','Him','His','он','его','Его','послушным'),
        ('She','Her','Her','она','её','Её','послушной'),
        ('It','It','Its','она','её','Её','послушной'),
    ]:
        suffix=(b[373]+object_.lower()+b[374]+subject.lower()+b[375]+object_.lower()
                +b[376]+possessive.lower()+b[377]+object_.lower()+b[378])
        ru_suffix=(f' умоляет, кричит, отбивается: двое приобщённых к Нити стражей волокут {ru_object} с кинетопода. '
                   f'На миг {ru_subject} вырывается — но Нить хлещет плетьми, возвращает {ru_object} в руки стражей, '
                   'и те заталкивают свою жертву в открытую боковую дверь.')
        templates.append(dict(prefix='',suffix=suffix,ru_prefix='',ru_suffix=ru_suffix,translate_value=True))
        for last,ru_ruler in [(380,'Императрица'),(381,'Император')]:
            en=possessive+b[379]+subject+b[last]
            mapping[en]=(f'{ru_possessive} крики разносятся по всему двору. '
                         f'«Не тревожьтесь. Скоро {ru_subject} станет {ru_obedient}», — обещает {ru_ruler}.')
