using System;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
var root=Path.Combine(Directory.GetCurrentDirectory(),"work");
var names=new[]{"sEngineChangeButton","sHelpWanted","sHelpWantedIcon"};
var report=names.Select(name=>{
    var sprite=Data.Sprites.Single(s=>s.Name.Content==name);
    var index=Data.Sprites.IndexOf(sprite);
    var objects=Data.GameObjects.Where(o=>o.Sprite==sprite).Select(o=>o.Name.Content).ToList();
    var sources=Directory.GetFiles(Path.Combine(root,"source","CodeEntries"),"*.gml")
        .Where(p=>System.Text.RegularExpressions.Regex.IsMatch(File.ReadAllText(p),@"\b"+name+@"\b"))
        .Select(Path.GetFileName).ToList();
    return new {name,index,objects,sources};
}).ToList();
File.WriteAllText(Path.Combine(root,"build","additional-ui-asset-usage.json"),JsonConvert.SerializeObject(report,Formatting.Indented));
Console.WriteLine(JsonConvert.SerializeObject(report));
