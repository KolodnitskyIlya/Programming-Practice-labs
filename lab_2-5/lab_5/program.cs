using Python.Runtime;

class Program
{
    static void Main()
    {
        PythonEngine.Initialize();

        string[] scripts = {
            "scripts/script1.py",
            "scripts/script2.py",
            "scripts/script3.py",
            "scripts/script4.py",
            "scripts/script5.py",
            "scripts/script6.py"
        };

        foreach (string script in scripts)
        {
            using (Py.GIL())
            {
                dynamic builtins = Py.Import("builtins");
                dynamic runpy = Py.Import("runpy");

                Console.WriteLine($"Running {script}...");
                runpy.run_path(script);
            }
        }

        PythonEngine.Shutdown();
        Console.WriteLine("✅ Все скрипты выполнены.");

        // ---------- Стратегия коллизий (голосование) ----------
        var allPreds = new List<int[]>();
        for (int i = 1; i <= 6; i++)
        {
            var path = $"output/predictions_script{i}.csv";
            Console.WriteLine($"📄 Загрузка предсказаний: {path}");
            var lines = File.ReadAllLines(path).Skip(1).ToArray();
            allPreds.Add(lines.Select(int.Parse).ToArray());
        }

        int rowCount = allPreds[0].Length;
        var final = new List<int>();

        for (int i = 0; i < rowCount; i++)
        {
            var votes = allPreds.Select(p => p[i]);
            int majority = votes.GroupBy(x => x).OrderByDescending(g => g.Count()).First().Key;
            final.Add(majority);
        }

        File.WriteAllLines("output/final_predictions.csv", new[] { "prediction" }.Concat(final.Select(x => x.ToString())));
        Console.WriteLine("✅ Голосование завершено. Результаты сохранены в output/final_predictions.csv");
    }
}