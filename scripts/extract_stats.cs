using AssetsTools.NET;
using AssetsTools.NET.Extra;
using System.Text.Json;

var assetPath = args.Length > 0 ? args[0] : "data/raw/_apk_decompiled_assets/assets/bin/Data";
var outputPath = args.Length > 1 ? args[1] : "data/raw/_extracted_assets";

Directory.CreateDirectory(outputPath);

var manager = new AssetsManager();
try
{
    // Load all asset files from the Unity data directory
    foreach (var file in Directory.GetFiles(assetPath))
    {
        try
        {
            var inst = manager.LoadAssetsFile(file, false);
            Console.WriteLine($"  Loaded: {Path.GetFileName(file)} ({inst.file.AssetFileInfos.Count} assets)");
        }
        catch { /* skip non-asset files */ }
    }

    Console.WriteLine($"\nTotal files loaded: {manager.Files.Count}");
    
    // Dump asset type inventory
    var typeCount = new Dictionary<string, int>();
    foreach (var afile in manager.Files)
    {
        foreach (var info in afile.file.AssetFileInfos)
        {
            var typeName = info.TypeId.ToString();
            if (!typeCount.ContainsKey(typeName))
                typeCount[typeName] = 0;
            typeCount[typeName]++;
        }
    }
    
    File.WriteAllText(Path.Combine(outputPath, "asset_inventory.json"), 
        JsonSerializer.Serialize(typeCount, new JsonSerializerOptions { WriteIndented = true }));
    
    Console.WriteLine("\nAsset inventory:");
    foreach (var kv in typeCount.OrderByDescending(x => x.Value))
        Console.WriteLine($"  {kv.Key}: {kv.Value}");
}
finally
{
    manager.UnloadAll();
}
