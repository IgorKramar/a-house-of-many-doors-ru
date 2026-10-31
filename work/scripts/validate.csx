using System;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using UndertaleModLib.Models;
var root=Directory.GetCurrentDirectory();
var original=JArray.Parse(File.ReadAllText(Path.Combine(root,"work","source","strings.json")));
foreach(var s in original) if(Data.Strings[(int)s["id"]].Content!=(string)s["text"]) throw new Exception("Original string changed: "+s["id"]);
var translationChars=JObject.Parse(File.ReadAllText(Path.Combine(root,"work","build","translations.json"))).Properties().SelectMany(p=>((string)p.Value).ToCharArray());
var templateChars=JArray.Parse(File.ReadAllText(Path.Combine(root,"work","build","templates.json"))).SelectMany(p=>((string)p["ru_prefix"]+(string)p["ru_suffix"]).ToCharArray());
var multiChars=JArray.Parse(File.ReadAllText(Path.Combine(root,"work","build","templates_multi.json"))).SelectMany(p=>p["ru_parts"].SelectMany(t=>((string)t).ToCharArray()));
var chars=translationChars.Concat(templateChars).Concat(multiChars).Distinct().ToList();
foreach(var f in Data.Fonts){
  foreach(char c in f.Name.Content=="fRUtitle" ? "ДОМ МНОГИХ ДВЕРЕЙ".Distinct() : chars) if(!f.Glyphs.Any(g=>g.Character==c)) throw new Exception("Missing glyph "+(int)c+" in "+f.Name.Content);
  if(f.Glyphs.Select(g=>g.Character).Distinct().Count()!=f.Glyphs.Count) throw new Exception("Duplicate glyph");
  foreach(var g in f.Glyphs) if(g.SourceX+g.SourceWidth>f.Texture.SourceWidth || g.SourceY+g.SourceHeight>f.Texture.SourceHeight) throw new Exception("Out of bounds glyph");
}
int calls=0;foreach(var c in Data.Code)foreach(var i in c.Instructions)if(i.Kind==UndertaleInstruction.Opcode.Call){if(i.ValueFunction==null)throw new Exception("Unresolved function in "+c.Name.Content);calls++;}
int correctedHeadings=0;
foreach(var fix in new[] {
    new {Code="gml_Script_LucettaDialogue",First="L",Rest="UCETTA QUETZL"},
    new {Code="gml_Script_DrDelgadoDialogue",First="D",Rest="R HENRY DELGADO"}
}) {
    var literals=Data.Code.Single(c=>c.Name.Content==fix.Code).Instructions.Where(i=>i.ValueString?.Resource!=null).Select(i=>i.ValueString.Resource.Content).ToList();
    if(literals.Contains("B") || literals.Contains("RADLEY BAGGS") || !literals.Contains(fix.First) || !literals.Contains(fix.Rest)) throw new Exception("Incorrect character heading in "+fix.Code);
    correctedHeadings++;
}
var ui=Data.Code.Single(c=>c.Name.Content=="gml_Script_homd_ru_draw_sprite_ext");
var uiWords=ui.Instructions.Where(i=>i.ValueString?.Resource!=null).Select(i=>i.ValueString.Resource.Content).ToList();
foreach(var word in new[]{"ДОМ","МНОГИХ","ДВЕРЕЙ","РАССУДОК","СЕРДЕЧНЫЙ СВЕТ","АБОРДАЖ","ЗАМЕТКИ","Кто вы?"})
    if(!uiWords.Contains(word)) throw new Exception("Missing native UI label: "+word);
var menu=Data.Code.Single(c=>c.Name.Content=="gml_Object_oStartMenu_Draw_64");
if(!menu.Instructions.Any(i=>i.ValueFunction?.Name.Content=="homd_ru_draw_sprite_ext"))throw new Exception("Main menu title hook missing");
var result=new {original_strings_preserved=original.Count,fonts_checked=Data.Fonts.Count,translated_characters_checked=chars.Count,calls_checked=calls,corrected_character_headings=correctedHeadings,native_ui_labels_checked=true,all_checks_passed=true};
File.WriteAllText(Path.Combine(root,"work","build","validation.json"),JsonConvert.SerializeObject(result,Formatting.Indented));
Console.WriteLine(JsonConvert.SerializeObject(result));
