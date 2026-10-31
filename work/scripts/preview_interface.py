"""Static menu layout replay from the game assets and the actual font atlas.

This is deliberately not labeled or used as an in-game screenshot.
"""
import pathlib,json
from PIL import Image,ImageDraw,ImageFont
w=pathlib.Path(__file__).resolve().parents[1];b=w/'build';src=w/'source/ui-assets'
frames={(x['sprite'],x['frame']):x['page'] for x in json.loads((src/'frames.json').read_text())}
sprites={x['name']:x for x in json.loads((src/'sprites.json').read_text())}
def sprite(n):
    s=sprites[n];pg=frames[n,0];im=Image.new('RGBA',(s['Width'],s['Height']))
    im.paste(Image.open(src/f'{n}_0.png').convert('RGBA'),(pg['TargetX'],pg['TargetY']))
    return im
def text(s,name):
    font=json.loads((b/f'fonts/{name}.json').read_text());gs={g['Character']:g for g in font['glyphs']}
    atlas=Image.open(b/f'fonts/{name}.png').convert('RGBA')
    width=sum(gs[ord(c)]['Shift'] for c in s);height=max(gs[ord(c)]['SourceHeight'] for c in s)
    out=Image.new('RGBA',(width+10,height));x=5
    for c in s:
        q=gs[ord(c)]
        out.alpha_composite(atlas.crop((q['SourceX'],q['SourceY'],q['SourceX']+q['SourceWidth'],q['SourceY']+q['SourceHeight'])),(x+q['Offset'],0))
        x+=q['Shift']
    return out,width,height
canvas=Image.new('RGBA',(1280,720),'black')
for i in range(1,5):canvas.alpha_composite(sprite(f'sOpeningScreenLayer{i}').resize(canvas.size,Image.Resampling.LANCZOS))
title=Image.open(b/'title-native-preview.png').convert('RGBA').resize((round(693*.7),round(401*.7)),Image.Resampling.LANCZOS)
title.putalpha(title.getchannel('A').point(lambda v:round(v*.8)))
canvas.alpha_composite(title,(round(320-346*.7),round(180-200*.7)))
current=340
for s in ['ПРОДОЛЖИТЬ','НАЧАТЬ','ЗАГРУЗИТЬ','НАСТРОЙКИ','СОЗДАТЕЛИ','ВЫХОД']:
    lettering,width,height=text(s,'fStartMenu')
    button=sprite('sOptionButton').resize((280,height+28),Image.Resampling.LANCZOS)
    canvas.alpha_composite(button,(180,current));canvas.alpha_composite(lettering,(round(320-width/2)-5,current+14))
    current+=height+28
version,_,_=text('V2.3 · RU','fDialogueBold');canvas.alpha_composite(version,(25,690))
result=Image.new('RGB',(1280,754),'#17252b');result.paste(canvas,(0,0))
font=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',15)
ImageDraw.Draw(result).text((20,730),'Статический предпросмотр из ресурсов сборки. Игра не запускалась.',font=font,fill='#d0c7af')
result.save(b/'menu-ru-static-preview.png')
assert current<=720,current
print('Static menu layout:',current,'px of 720; saved menu-ru-static-preview.png')
