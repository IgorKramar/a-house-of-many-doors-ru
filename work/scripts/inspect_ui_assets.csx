using System;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using UndertaleModLib.Util;
var root=Path.Combine(Directory.GetCurrentDirectory(),"work","source","ui-assets");
Directory.CreateDirectory(root);
var sprites=Data.Sprites.Select((s,i)=>new {id=i,name=s.Name.Content,s.Width,s.Height,s.OriginX,s.OriginY,frames=s.Textures.Count}).ToList();
File.WriteAllText(Path.Combine(root,"sprites.json"),JsonConvert.SerializeObject(sprites,Formatting.Indented));
using(var worker=new TextureWorker())
foreach(var s in Data.Sprites.Where(s=>Data.Sprites.IndexOf(s)<110 || System.Text.RegularExpressions.Regex.IsMatch(s.Name.Content,"HUD|WhoAre|Title|OpeningScreen|Tab|GUI|Underpanel|Button|Label|Text|Cargo|Logbook|HelpWanted",System.Text.RegularExpressions.RegexOptions.IgnoreCase))) {
 for(int i=0;i<s.Textures.Count;i++) {
  if(s.Textures[i].Texture!=null) worker.ExportAsPNG(s.Textures[i].Texture,Path.Combine(root,s.Name.Content+"_"+i+".png"));
 }
}
Console.WriteLine("Indexed "+sprites.Count+" sprites; exported UI candidates.");
File.WriteAllText(Path.Combine(root,"frames.json"),JsonConvert.SerializeObject(Data.Sprites.SelectMany(s=>s.Textures.Select((f,i)=>new {sprite=s.Name.Content,frame=i,page=f.Texture==null?null:new {f.Texture.TargetX,f.Texture.TargetY,f.Texture.SourceWidth,f.Texture.SourceHeight,f.Texture.TargetWidth,f.Texture.TargetHeight,f.Texture.BoundingWidth,f.Texture.BoundingHeight}})),Formatting.Indented));
File.WriteAllText(Path.Combine(root,"font-properties.txt"),string.Join("\n",Data.Fonts[0].GetType().GetProperties().Select(p=>p.Name+": "+p.PropertyType.Name)));
