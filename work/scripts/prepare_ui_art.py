"""Typeset native GML UI labels; preserve original sprite art outside lettering.

No generated bitmap is shipped. The title is rendered by a real Cyrillic font.
Private static previews replay the same glyph atlas and rectangle recipe.
"""
import json,pathlib,math,re
from PIL import Image,ImageDraw,ImageFont
w=pathlib.Path(__file__).resolve().parents[1];out=w/'build';gml=out/'gml'
src=w/'source/ui-assets'
sprites={s['name']:s for s in json.loads((src/'sprites.json').read_text())}
frames={(f['sprite'],f['frame']):f['page'] for f in json.loads((src/'frames.json').read_text())}
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def original(n,i=0):
    s=sprites[n];p=frames[n,i];im=Image.new('RGBA',(s['Width'],s['Height']))
    im.paste(Image.open(src/f'{n}_{i}.png').convert('RGBA'),(p['TargetX'],p['TargetY']))
    return im

# One high-resolution native font for the large title, with exact glyph metrics.
font=ImageFont.truetype(str(w/'fonts/CormorantGaramond.ttf'),230)
font.set_variation_by_axes([700])
titlechars=sorted(set('ДОМ НГИХВЕРЙ'))
atlas=Image.new('RGBA',(2048,512),(255,255,255,0));d=ImageDraw.Draw(atlas)
glyphs=[];x=2;baseline=210;lineheight=280
for ch in titlechars:
    l,t,r,b=font.getbbox(ch,anchor='ls');gw=max(1,r-l+4)
    d.text((x+2-l,baseline),ch,font=font,anchor='ls',fill='white')
    glyphs.append(dict(Character=ord(ch),SourceX=x,SourceY=0,SourceWidth=gw,SourceHeight=lineheight,Shift=round(font.getlength(ch)),Offset=l-2))
    x+=gw+3
assert x<2048
atlas.save(out/'fonts/fRUtitle.png')
write(out/'fonts/fRUtitle.json',dict(name='fRUtitle',family='Cormorant Garamond',width=2048,height=512,pixels=230,lineheight=lineheight,glyphs=glyphs))

def fontdata(name):
    meta=json.loads((out/f'fonts/{name}.json').read_text())
    return Image.open(out/f'fonts/{name}.png').convert('RGBA'),{g['Character']:g for g in meta['glyphs']}
fontcache={}
def word(name,text):
    if name not in fontcache:fontcache[name]=fontdata(name)
    a,gs=fontcache[name]
    im=Image.new('RGBA',(int(sum(gs[ord(c)]['Shift'] for c in text))+30,max(gs[ord(c)]['SourceHeight'] for c in text)))
    x=10
    for c in text:
        q=gs[ord(c)];piece=a.crop((q['SourceX'],q['SourceY'],q['SourceX']+q['SourceWidth'],q['SourceY']+q['SourceHeight']))
        im.alpha_composite(piece,(x+q['Offset'],0));x+=q['Shift']
    bb=im.getbbox();return im.crop(bb),[bb[0]-10,bb[1],bb[2]-10,bb[3]]

# Coordinates are in the original untrimmed sprite canvas.
# mask rectangle + a clean source scanline replace only the old lettering.
recipes={}
def label(n,rect,text,font='fSmallerDialogueBold',height=12,sample=None,color='#ffffff',align='center'):
    recipes.setdefault(n,[]).append(dict(rect=rect,text=text,font=font,height=height,sample=sample,color=color,align=align))
for n,t in [('sBoardButton','АБОРДАЖ'),('sFleeButton','БЕГСТВО')]:
    label(n,[24,106,126,124],t,height=12,sample=104)
label('sHeartlightGUI',[42,173,177,192],'СЕРДЕЧНЫЙ СВЕТ',height=12,sample=172)
label('sFlaresOnly',[18,112,139,130],'РАКЕТА',height=12,sample=111)
label('sGloryOnly',[10,112,146,130],'РУКА СЛАВЫ',height=12,sample=111)
for top,t in [(17,'КОРПУС'),(43,'РАССУДОК'),(69,'ТОПЛИВО')]:
    label('sGauge',[16,top,80,top+15],t,height=10,sample=top-1,align='left')
for top,t in [(17,'КОРПУС'),(43,'РАССУДОК')]:
    label('sEnemyGauge',[16,top,80,top+15],t,height=10,sample=top-1,align='left')
for x1,x2,t in [(49,223,'ОХРАНА'),(305,480,'АРТИЛЛЕРИСТЫ'),(559,740,'МЛ. ИНЖЕНЕРЫ'),(813,994,'РАЗНОРАБОЧИЕ')]:
    label('sLowerCrewBackground',[x1,42,x2,62],t,height=13,sample=40,color='#d0bcaa',align='left')
label('sMemoirsDown',[147,47,242,69],'ЗАМЕТКИ',height=16,sample=45,color='#c5c5b9')
label('sMemoirs',[147,251,242,273],'ЗАМЕТКИ',height=16,sample=249,color='#c5c5b9')
label('sGone',[27,57,104,82],'Нет в команде',height=13,sample=55)
# Text-only sprite, so replace it entirely with native text.
label('sWhoAreYou',[0,0,74,48],'Кто вы?',height=20)
label('sTitleText',[62,47,392,180],'ДОМ',font='fRUtitle',height=133)
label('sTitleText',[402,123,657,180],'МНОГИХ',font='fRUtitle',height=57)
label('sTitleText',[58,196,667,339],'ДВЕРЕЙ',font='fRUtitle',height=143)

def cut_regions(width,height,masks):
    ys=sorted(set([0,height]+[v for r in masks for v in [r[1],r[3]]]))
    result=[]
    for y1,y2 in zip(ys,ys[1:]):
        intervals=sorted((r[0],r[2]) for r in masks if r[1]<=y1 and r[3]>=y2)
        x=0
        for a,b in intervals:
            if a>x:result.append([x,y1,a,y2])
            x=max(x,b)
        if x<width:result.append([x,y1,width,y2])
    return result

code=['var spr,fr,px,py,sx,sy,col,al,oldfont,oldcolor,oldalpha,oldh,oldv,ox,oy;',
      'spr=argument0;fr=argument1;px=argument2;py=argument3;sx=argument4;sy=argument5;col=argument7;al=argument8;',
      'if (argument6!=0) {draw_sprite_ext(argument0,argument1,argument2,argument3,argument4,argument5,argument6,argument7,argument8);return;}',
      'switch(spr) {']
preview=[];manifest=[]
for n,labels in recipes.items():
    s=sprites[n];variants=range(s['frames']) if n=='sMemoirs' else [None]
    code+=[f'case {n}:','oldfont=-1;oldh=fa_left;oldv=fa_top;if(variable_global_exists("homd_ru_font"))oldfont=global.homd_ru_font;if(variable_global_exists("homd_ru_halign"))oldh=global.homd_ru_halign;if(variable_global_exists("homd_ru_valign"))oldv=global.homd_ru_valign;oldcolor=draw_get_colour();oldalpha=draw_get_alpha();',
           'draw_set_halign(fa_left);draw_set_valign(fa_top);draw_set_alpha(al);',
           f'ox=px-{s["OriginX"]}*sx;oy=py-{s["OriginY"]}*sy;']
    if n=='sMemoirs':code+=['fr=floor(fr);if(fr<0)fr=floor(image_index);fr=fr mod 20;','switch(fr) {']
    for variant in variants:
        ls=[dict(q) for q in labels]
        frame=variant or 0
        # Every animation frame retains the same art offset relationship.
        if n=='sMemoirs':
            shift=frames[n,frame]['TargetY']-frames[n,0]['TargetY']
            for q in ls:q['rect']=[q['rect'][0],q['rect'][1]+shift,q['rect'][2],q['rect'][3]+shift];q['sample']+=shift
            if frame>=4:
                for q in ls:q['color']='#68543f'
                # LAST VISITED is present only after the paper opens.
                ls.append(dict(rect=[56,300+shift,205,320+shift],text='ПОСЛЕДНЕЕ ПОСЕЩЕНИЕ',font='fSmallerDialogueBold',height=12,sample=298+shift,color='#776048',align='left'))
            code+=[f'case {frame}:']
        im=Image.new('RGBA',(s['Width'],s['Height']))
        stock=original(n,frame)
        if n not in ['sTitleText','sWhoAreYou']:
            for x1,y1,x2,y2 in cut_regions(s['Width'],s['Height'],[q['rect'] for q in ls]):
                code+=[f'draw_sprite_part_ext(spr,fr,{x1},{y1},{x2-x1},{y2-y1},ox+{x1}*sx,oy+{y1}*sy,sx,sy,col,al);']
                im.paste(stock.crop((x1,y1,x2,y2)),(x1,y1))
        for q in ls:
            x1,y1,x2,y2=q['rect'];ww,hh=x2-x1,y2-y1
            if q['sample'] is not None:
                code+=[f'draw_sprite_part_ext(spr,fr,{x1},{q["sample"]},{ww},1,ox+{x1}*sx,oy+{y1}*sy,sx,sy*{hh},col,al);']
                im.paste(stock.crop((x1,q['sample'],x2,q['sample']+1)).resize((ww,hh)),(x1,y1))
            letters,bb=word(q['font'],q['text'])
            if n=='sTitleText':scale_y=q['height']/letters.height;scale_x=ww/letters.width
            else:scale_y=q['height']/letters.height;scale_x=min(scale_y,(ww-2)/letters.width)
            tw,th=round(letters.width*scale_x),round(letters.height*scale_y)
            tx=x1+(ww-tw)/2 if q['align']=='center' else x1+1
            ty=y1+(hh-th)/2
            rgb=tuple(int(q['color'][i:i+2],16) for i in [1,3,5])
            code+=[f'draw_set_font({q["font"]});draw_set_colour(merge_colour(make_colour_rgb({rgb[0]},{rgb[1]},{rgb[2]}),col,0));',
                   f'draw_text_transformed(ox+{tx-bb[0]*scale_x:.5f}*sx,oy+{ty-bb[1]*scale_y:.5f}*sy,"{q["text"]}",{scale_x:.7f}*sx,{scale_y:.7f}*sy,0);']
            # Font atlas replay, not a screenshot of the running game.
            ink=letters.resize((tw,th),Image.Resampling.LANCZOS);paint=Image.new('RGBA',ink.size,rgb+(255,));paint.putalpha(ink.getchannel('A'))
            im.alpha_composite(paint,(round(tx),round(ty)))
            manifest.append(dict(sprite=n,frame=frame,text=q['text'],bounds=[tx,ty,tx+tw,ty+th],mask=q['rect']))
        if n=='sMemoirs':code+=['break;']
        if frame in [0,19]:preview.append((n+('_'+str(frame) if n=='sMemoirs' else ''),stock,im))
        if n=='sTitleText':im.save(out/'title-native-preview.png')
    if n=='sMemoirs':code+=['}']
    code+=['draw_set_font(oldfont);draw_set_colour(oldcolor);draw_set_alpha(oldalpha);draw_set_halign(oldh);draw_set_valign(oldv);return;']
code+=['}','draw_sprite_ext(argument0,argument1,argument2,argument3,argument4,argument5,argument6,argument7,argument8);']
(gml/'gml_Script_homd_ru_draw_sprite_ext.gml').write_text('\n'.join(code),encoding='utf-8')
hooks=json.loads((out/'hooks.json').read_text())
for kind in ['font','halign','valign']:
    name='draw_set_'+kind
    if name not in hooks:hooks.append(name)
    (gml/f'gml_Script_homd_ru_{name}.gml').write_text(f'global.homd_ru_{kind}=argument0;{name}(argument0);',encoding='utf-8')
write(out/'hooks.json',hooks)
write(out/'ui-art-recipes.json',recipes);write(out/'ui-art-layout.json',manifest)
uses=[]
for p in (w/'source/CodeEntries').glob('*.gml'):
    if any(re.search(r'\b'+n+r'\b',p.read_text(encoding='utf-8-sig')) for n in recipes):uses.append(p.stem)
write(out/'ui-art-hook-scripts.json',uses)
# Before/after proof sheet from private source assets and native drawing recipe.
sheet=Image.new('RGB',(1200,len(preview)*230),'#253239');d=ImageDraw.Draw(sheet)
for row,(n,before,after) in enumerate(preview):
    d.text((12,row*230+5),n,fill='white')
    for j,im in enumerate([before,after]):
        im=im.copy();im.thumbnail((570,202));sheet.paste(im,(j*600+(590-im.width)//2,row*230+24),im)
sheet.save(out/'ui-native-proof.png')
print('Native UI:',len(recipes),'sprite families;',len(uses),'source scripts; title font and static proof generated')
