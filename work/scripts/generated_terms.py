"""Assemble repeated, human-translated glossary and divine-status text."""
import json,re
def add_terms(mapping,work,strings):
    alltexts={x['text'] for x in strings}
    locations=json.loads((work/'glossary_locations.json').read_text(encoding='utf-8'))
    bare={re.sub(r'^(?:The |the )','',en):ru for en,ru in locations.items()}
    for en,ru in locations.items():mapping[en.upper()]=ru.upper()
    for en in alltexts:
        place=re.sub(r'^(?:The |the )','',en)
        if place in bare:mapping[en]=bare[place]
        for pre,ru in [('Current Affairs: ','Свежие новости: '),('Passenger: ','Пассажир: ')]:
            if en.startswith(pre):
                place=re.sub(r'^(?:The |the )','',en[len(pre):])
                if place in bare:mapping[en]=ru+bare[place]
    gods=[
      ('Graveddon','Граведдона','The Iron Swine. The Undreaming Carcass.','Железный Боров. Туша Без Сновидений.','His','Его'),
      ('Nahash','Нахаша','The Serpent. The Infinite Coils.','Змей. Бесконечные Кольца.','His','Его'),
      ('Abjah','Абджи','The Void-Shaped God. The God-Shaped Void.','Бог в Обличье Пустоты. Пустота в Обличье Бога.','Her','Её'),
      ('Cobblestone','Булыжника','The Trodden God. The Carved and Hewn.','Попираемый Бог. Высеченный и Изваянный.','Its','Его'),
      ('Anglecrab','Углокраба','The Impossible Geometries. The Great Contortion.','Невозможные Геометрии. Великое Искажение.','Its','Его'),
      ("Wyl o' Pan",'Уил-о-Пана','The Son of Stars. The Glimmer-smith.','Сын Звёзд. Кузнец Сияния.','His','Его'),
      ('Morbazar','Морбазара','The Storyteller. The Clock-faced God.','Сказитель. Бог с Лицом-Циферблатом.','His-and-her','Его-её'),
      ('Scorthidion','Скортидиона','The Mountainous Scab. The Coagulant God.','Горный Струп. Свернувшийся Бог.','Its','Его')]
    for god,gen,epithet,ru_epithet,poss,ru_poss in gods:
        for en,ru in [('Scrutiny','Внимание'),('Favour','Благосклонность'),('Reproach','Немилость')]:
            mapping[en+': '+god]=ru+' '+gen
        mapping['Saint of '+god]='Святой '+gen
        base=epithet+' A Sanctioned deity. '
        ru_base=ru_epithet+' Признанное божество. '
        pairs=[
          ('(You have attracted the attention of a god. They are not sure what to do with you... yet.)','(Вы привлекли внимание божества. Оно ещё не решило, что с вами делать. Пока.)'),
          ('('+poss+' Favours can be traded away, or accumulated in hope of becoming one of the permanently Favoured.)','('+ru_poss+' благосклонностью можно расплачиваться. Или копить её в надежде обрести вечную милость.)'),
          ("(The one trait shared amongst all gods is holding a grudge. If you allow a god's Reproach to grow too high, you may suffer a divine curse.)",'(Все боги сходятся в одном: они злопамятны. Если немилость божества станет слишком велика, вас может постигнуть божественное проклятие.)')]
        for en,ru in pairs:
            assert base+en in alltexts,(god,en)
            mapping[base+en]=ru_base+ru
