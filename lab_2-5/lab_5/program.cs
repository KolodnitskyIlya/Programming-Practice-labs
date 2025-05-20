using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json;

class Program
{
    static void RunScript(string scriptPath, string csvData)
    {
        var psi = new ProcessStartInfo
        {
            FileName = "python3",
            Arguments = scriptPath,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            RedirectStandardInput = true,
            UseShellExecute = false
        };

        using (var process = Process.Start(psi))
        {
            process.StandardInput.Write(csvData);
            process.StandardInput.Close();

            string output = process.StandardOutput.ReadToEnd();
            string error = process.StandardError.ReadToEnd();
            process.WaitForExit();

            Console.WriteLine($"▶ {Path.GetFileName(scriptPath)} завершён:");
            if (!string.IsNullOrEmpty(output))
            {
                var json = System.Text.Json.JsonDocument.Parse(output.Trim());
                string model = json.RootElement.GetProperty("model").GetString();
                double acc = json.RootElement.GetProperty("accuracy").GetDouble();
                double time = json.RootElement.GetProperty("time").GetDouble();
                Console.WriteLine($"  Модель: {model}");
                Console.WriteLine($"  Accuracy: {acc:F4}");
                Console.WriteLine($"  Time: {time:F2} сек.");
            }

            if (!string.IsNullOrEmpty(error))
            {
                Console.WriteLine("Ошибки:\n" + error);
            }
        }
    }


    static void Main()
    {
        string csvData = File.ReadAllText("input/data.csv");

        string[] scripts = {
            "scripts/script1.py", "scripts/script2.py", "scripts/script3.py",
            "scripts/script4.py", "scripts/script5.py", "scripts/script6.py"
        };

        foreach (var script in scripts)
        {
            RunScript(script, csvData);
        }
    }

    class ModelResult
    {
        public string Model { get; set; }
        public double Accuracy { get; set; }
        public double Time { get; set; }
    }
}
