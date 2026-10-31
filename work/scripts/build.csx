using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;
using UndertaleModLib.Compiler;
var root=Path.Combine(Directory.GetCurrentDirectory(),"work","build");
var originalCode=Data.Code.ToList();
bool codeEnabled=Environment.GetEnvironmentVariable("HOMD_BUILD_MODE")!="fonts";
bool fontsEnabled=Environment.GetEnvironmentVariable("HOMD_BUILD_MODE")!="code";
int calls=0;
int correctedHeadingLiterals=0;
int uiArtCalls=0;
if(codeEnabled && Data.Fonts.ByName("fRUtitle")==null) Data.Fonts.Add(new UndertaleFont {
    Name=Data.Strings.MakeString("fRUtitle"),DisplayName=Data.Strings.MakeString("Cormorant Garamond"),
    EmSize=230, Bold=true,Italic=false,RangeStart=32,RangeEnd=1103,ScaleX=1,ScaleY=1,AntiAliasing=1
});
if(codeEnabled) {
// These two romance screens copied Bradley's heading. Change only their
// instruction references: the shared original string table must remain intact.
foreach(var fix in new[] {
    new {Code="gml_Script_LucettaDialogue", First="L", Rest="UCETTA QUETZL"},
    new {Code="gml_Script_DrDelgadoDialogue", First="D", Rest="R HENRY DELGADO"}
}) {
    var code=originalCode.Single(c=>c.Name.Content==fix.Code);
    foreach(var pair in new[] {new {From="B",To=fix.First},new {From="RADLEY BAGGS",To=fix.Rest}}) {
        var matches=code.Instructions.Where(i=>i.ValueString?.Resource?.Content==pair.From).ToList();
        if(matches.Count!=1) throw new Exception("Unexpected heading references in "+fix.Code+": "+pair.From);
        matches[0].ValueString=new UndertaleResourceById<UndertaleString,UndertaleChunkSTRG> {
            Resource=Data.Strings.MakeString(pair.To)
        };
        correctedHeadingLiterals++;
    }
}
var importer=new CodeImportGroup(Data) {AutoCreateAssets=true};
foreach(var path in Directory.GetFiles(Path.Combine(root,"gml"),"*.gml")) importer.QueueReplace(Path.GetFileNameWithoutExtension(path),File.ReadAllText(path));
importer.Import();
var hooks=JsonConvert.DeserializeObject<List<string>>(File.ReadAllText(Path.Combine(root,"hooks.json")));
foreach(var hook in hooks) Data.Functions.EnsureDefined("homd_ru_"+hook,Data.Strings);
Data.Functions.EnsureDefined("homd_ru_draw_sprite_ext",Data.Strings);
var uiArtScripts=JsonConvert.DeserializeObject<List<string>>(File.ReadAllText(Path.Combine(root,"ui-art-hook-scripts.json")));
foreach(var code in originalCode)
{
    // Text input must preserve a player's name even when it coincides with a translated word.
    bool nameInput=code.Name.Content=="gml_Script_InputPlayerName" || code.Name.Content=="gml_Script_InputLowerCrewName";
    foreach(var ins in code.Instructions)
    {
        if(ins.Kind==UndertaleInstruction.Opcode.Call && ins.ValueFunction!=null && hooks.Contains(ins.ValueFunction.Name.Content) && (!nameInput || ins.ValueFunction.Name.Content.StartsWith("draw_set_")))
        {ins.ValueFunction=Data.Functions.ByName("homd_ru_"+ins.ValueFunction.Name.Content) ?? throw new Exception("Missing hook function");calls++;}
        if(ins.Kind==UndertaleInstruction.Opcode.Call && ins.ValueFunction?.Name.Content=="draw_sprite_ext" && uiArtScripts.Contains(code.Name.Content)) {
            ins.ValueFunction=Data.Functions.ByName("homd_ru_draw_sprite_ext");uiArtCalls++;
        }
    }
}
}
if(fontsEnabled)
foreach(var font in Data.Fonts)
{
    var path=Path.Combine(root,"fonts",font.Name.Content);
    var meta=JObject.Parse(File.ReadAllText(path+".json"));
    ushort w=(ushort)meta["width"],h=(ushort)meta["height"];
    var texture=new UndertaleEmbeddedTexture {Name=new UndertaleString("RU font "+font.Name.Content)};
    texture.TextureData.Image=GMImage.FromPng(File.ReadAllBytes(path+".png"));Data.EmbeddedTextures.Add(texture);
    var page=new UndertaleTexturePageItem {Name=new UndertaleString("RU page "+font.Name.Content),TexturePage=texture,SourceX=0,SourceY=0,SourceWidth=w,SourceHeight=h,TargetX=0,TargetY=0,TargetWidth=w,TargetHeight=h,BoundingWidth=w,BoundingHeight=h};
    Data.TexturePageItems.Add(page);font.Texture=page;
    foreach(var g in meta["glyphs"].Where(g=>font.Name.Content=="fRUtitle" || (int)g["Character"]>127)) font.Glyphs.Add(new UndertaleFont.Glyph {Character=(ushort)g["Character"],SourceX=(ushort)g["SourceX"],SourceY=(ushort)g["SourceY"],SourceWidth=(ushort)g["SourceWidth"],SourceHeight=(ushort)g["SourceHeight"],Shift=(short)g["Shift"],Offset=(short)g["Offset"]});
    var ordered=font.Glyphs.OrderBy(g=>g.Character).ToList();font.Glyphs.Clear();foreach(var g in ordered)font.Glyphs.Add(g);
    font.RangeEnd=font.Glyphs.Max(g=>(uint)g.Character);
}
Console.WriteLine("Installed render hooks: "+calls+"; Cyrillic font atlases: "+Data.Fonts.Count);
foreach(var code in Data.Code) foreach(var ins in code.Instructions) if(ins.Kind==UndertaleInstruction.Opcode.Call && ins.ValueFunction==null) throw new Exception("Unresolved call in "+code.Name.Content);
File.WriteAllText(Path.Combine(root,"build-stats.json"),JsonConvert.SerializeObject(new{hooked_calls=calls,ui_art_hooked_calls=uiArtCalls,corrected_heading_literals=correctedHeadingLiterals,fonts=Data.Fonts.Count,strings=Data.Strings.Count,code_entries=Data.Code.Count},Formatting.Indented));
