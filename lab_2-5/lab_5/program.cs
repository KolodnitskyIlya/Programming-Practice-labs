using System;
using System.Diagnostics;
using System.IO;

class Program
{
    static void RunScript(string scriptPath)
    {
        var psi = new ProcessStartInfo
        {
            FileName = "python3",
            Arguments = scriptPath,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false
        };

        using (var process = Process.Start(psi))
        {
            string output = process.StandardOutput.ReadToEnd();
            string error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            Console.WriteLine($"▶ {Path.GetFileName(scriptPath)} завершён.");
            if (!string.IsNullOrEmpty(output)) Console.WriteLine("Вывод:\n" + output);
            if (!string.IsNullOrEmpty(error)) Console.WriteLine("Ошибки:\n" + error);
        }
    }

    static void Main()
    {
        string[] scripts = {
            "scripts/script1.py", "scripts/script2.py", "scripts/script3.py",
            "scripts/script4.py", "scripts/script5.py", "scripts/script6.py"
        };

        foreach (var script in scripts)
        {
            RunScript(script);
        }

        Console.WriteLine("✅ Все скрипты Python выполнены.");
    }
}
