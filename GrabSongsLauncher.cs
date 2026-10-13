using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;

[assembly: AssemblyTitle("GrabSongs")]
[assembly: AssemblyProduct("GrabSongs")]
[assembly: AssemblyDescription("GrabSongs Music Downloader Service")]
[assembly: AssemblyCompany("GrabSongs")]
[assembly: AssemblyCopyright("Copyright © 2026 Samarth Rajesh Lad")]

namespace GrabSongsLauncher
{
    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            string dir = AppDomain.CurrentDomain.BaseDirectory;
            string scriptPath = Path.Combine(dir, "app.py");

            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = "pythonw.exe";
            psi.Arguments = "\"" + scriptPath + "\"";
            psi.WorkingDirectory = dir;
            psi.UseShellExecute = true;

            try
            {
                Process p = Process.Start(psi);
                if (p != null)
                {
                    p.WaitForExit();
                }
            }
            catch
            {
                psi.FileName = "python.exe";
                Process p = Process.Start(psi);
                if (p != null)
                {
                    p.WaitForExit();
                }
            }
        }
    }
}
