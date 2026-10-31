using System;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
var dir=Path.Combine(Directory.GetCurrentDirectory(),"work","source");
Directory.CreateDirectory(dir);
File.WriteAllText(Path.Combine(dir,"strings.json"),JsonConvert.SerializeObject(Data.Strings.Select((s,i)=>new {id=i,text=s.Content}),Formatting.Indented));
Console.WriteLine("Exported original string metadata: "+Data.Strings.Count);
