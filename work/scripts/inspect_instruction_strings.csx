using System;
using System.Linq;
using UndertaleModLib.Models;
foreach(var member in typeof(UndertaleInstruction).GetMembers().Where(m=>m.Name.Contains("Value") || m.Name.Contains("String"))) Console.WriteLine(member);
var code=Data.Code.First(c=>c.Name.Content=="gml_Script_LucettaDialogue");
foreach(var ins in code.Instructions) {
    var p=typeof(UndertaleInstruction).GetProperty("ValueString");
    if(p!=null) {var value=p.GetValue(ins);if(value!=null) {Console.WriteLine("String reference type: "+value.GetType());break;}}
}
