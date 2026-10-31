import json,math,pathlib
from PIL import Image,ImageDraw,ImageFont
root=pathlib.Path(__file__).resolve().parents[2]
src=root/'work/source'; out=root/'work/build/fonts'; out.mkdir(parents=True,exist_ok=True)
fonts=json.loads((src/'fonts.json').read_text(encoding='utf-8'))
extras=list(range(0x400,0x460))+[0xA0,0xAB,0xB7,0xBB,0xD7,0x2013,0x2014,0x2018,0x2019,0x201C,0x201D,0x201E,0x2026,0x2116,0x2212]
report=[]
for f in fonts:
    original=Image.open(src/'font_textures'/(f['name']+'.png')).convert('RGBA')
    glyphs=f['glyphs']
    lineheight=max(g['SourceHeight'] for g in glyphs)
    decorative=f['display'] not in ('Georgia','Arial','DFKai-SB')
    if decorative:
        path=root/'work/fonts/CormorantGaramond.ttf'; family='Cormorant Garamond'
    else:
        suffix='z' if f['Bold'] and f['Italic'] else 'b' if f['Bold'] else 'i' if f['Italic'] else ''
        path=pathlib.Path('C:/Windows/Fonts/georgia'+suffix+'.ttf'); family='Georgia'
    old_cap=next(g for g in glyphs if g['Character']==ord('H'))
    cap=original.crop((old_cap['SourceX'],old_cap['SourceY'],old_cap['SourceX']+old_cap['SourceWidth'],old_cap['SourceY']+old_cap['SourceHeight'])).getchannel('A').getbbox()
    target_cap=(cap[3]-cap[1]) if cap else round(f['size']*.95)
    target_base=cap[3] if cap else lineheight-3
    # Match the actual ink height and baseline, keeping the original Latin glyphs.
    candidates=[]
    for size in range(max(6,round(f['size']*.8)),max(12,round(f['size']*2.1))):
        font=ImageFont.truetype(str(path),size)
        if decorative: font.set_variation_by_axes([600 if f['Bold'] else 500])
        box=font.getbbox('H',anchor='ls'); candidates.append((abs((box[3]-box[1])-target_cap),size,font))
    _,pixels,font=min(candidates,key=lambda v:(v[0],abs(v[1]-f['size']*4/3)))
    width=max(512,original.width); x=2; y=original.height+3; rowh=lineheight+3
    atlas=Image.new('RGBA',(width,4096),(255,255,255,0)); atlas.paste(original,(0,0))
    draw=ImageDraw.Draw(atlas)
    for cp in extras:
        ch=chr(cp); bbox=font.getbbox(ch,anchor='ls'); left,top,right,bottom=bbox
        gw=max(1,right-left+2); gh=lineheight
        if x+gw+2>width: x=2;y+=rowh
        if y+gh>4096: raise ValueError('Atlas too large')
        # A common baseline keeps Russian and existing Latin aligned.
        draw.text((x+1-left,y+target_base),ch,font=font,fill=(255,255,255,255),anchor='ls')
        glyphs.append({'Character':cp,'SourceX':x,'SourceY':y,'SourceWidth':gw,'SourceHeight':gh,'Shift':round(font.getlength(ch)),'Offset':left-1})
        x+=gw+3
    height=2**math.ceil(math.log2(y+rowh));atlas=atlas.crop((0,0,width,height));atlas.save(out/(f['name']+'.png'))
    glyphs.sort(key=lambda g:g['Character'])
    (out/(f['name']+'.json')).write_text(json.dumps({'name':f['name'],'family':family,'width':width,'height':height,'glyphs':glyphs},ensure_ascii=False),encoding='utf-8')
    report.append({'name':f['name'],'family':family,'pixels':pixels,'glyphs':len(glyphs),'baseline':target_base,'lineheight':lineheight})
(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
preview=Image.new('RGB',(1050,410),'#f8ebd8');d=ImageDraw.Draw(preview)
for y,name,text in [(24,'fDialogueHeading','ДОМ МНОГИХ ДВЕРЕЙ'),(88,'fStartMenu','НАЧАТЬ ИГРУ   НАСТРОЙКИ   ВЫХОД'),(150,'fActualBiggestDialogue','За глазом хрустит битое стекло.'),(195,'fActualBiggestDialogue','Из тумана проступают два встревоженных лица.'),(255,'fBiggerDialogue','«Вы помните своё имя?» — спрашивает тот, что полысее.'),(315,'fBiggerDialogue','Ёё Йй Щщ Цц Дд — «кавычки», многоточие… № 42')]:
    f=next(a for a in fonts if a['name']==name);a=Image.open(out/(name+'.png'));gs={g['Character']:g for g in f['glyphs']};x=24
    for ch in text:
        g=gs.get(ord(ch),gs[63]);piece=a.crop((g['SourceX'],g['SourceY'],g['SourceX']+g['SourceWidth'],g['SourceY']+g['SourceHeight']));ink=Image.new('RGB',piece.size,'#513527');preview.paste(ink,(x+g['Offset'],y),piece.getchannel('A'));x+=g['Shift']
preview.save(root/'work/build/font-preview.png')
print('Built',len(report),'Cyrillic font atlases')
