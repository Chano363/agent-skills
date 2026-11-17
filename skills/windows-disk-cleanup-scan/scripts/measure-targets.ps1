param(
    [switch]$SkipDrives
)

# Measure the usual cleanable locations on a Windows box.
# Read-only: nothing is deleted.
# NOTE: keep this file ASCII-only; Windows PowerShell 5.1 parses BOM-less UTF-8 as ANSI.

$ErrorActionPreference = 'SilentlyContinue'

Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.IO;

public class QS3
{
    public static long Dir(string path)
    {
        long sum = 0;
        var stack = new Stack<string>();
        stack.Push(path);
        while (stack.Count > 0)
        {
            string dir = stack.Pop();
            try
            {
                foreach (string f in Directory.EnumerateFiles(dir))
                {
                    try { sum += new FileInfo(f).Length; } catch { }
                }
            }
            catch { }
            try
            {
                foreach (string d in Directory.EnumerateDirectories(dir))
                {
                    bool skip = false;
                    try {
                        if ((File.GetAttributes(d) & FileAttributes.ReparsePoint) != 0) skip = true;
                    } catch { skip = true; }
                    if (!skip) stack.Push(d);
                }
            }
            catch { }
        }
        return sum;
    }
}
"@

$L = $env:LOCALAPPDATA
$R = $env:APPDATA
$U = $env:USERPROFILE
$T = $env:TEMP

$targets = @(
    @{ n = 'User TEMP';                       p = $T },
    @{ n = 'Windows TEMP (needs admin)';      p = 'C:\Windows\Temp' },
    @{ n = 'Windows Update download';         p = 'C:\Windows\SoftwareDistribution\Download' },
    @{ n = 'Windows Prefetch';                p = 'C:\Windows\Prefetch' },
    @{ n = 'WinRE update leftovers';          p = 'C:\$WinREAgent' },
    @{ n = 'Windows Installer cache (KEEP)';  p = 'C:\Windows\Installer' },
    @{ n = 'WinSxS (reported, hardlinked)';   p = 'C:\Windows\WinSxS' },
    @{ n = 'Windows.old';                     p = 'C:\Windows.old' },
    @{ n = 'WER crash reports';               p = 'C:\ProgramData\Microsoft\Windows\WER' },
    @{ n = 'Package Cache';                   p = 'C:\ProgramData\Package Cache' },
    @{ n = 'Downloads';                       p = "$U\Downloads" },
    @{ n = 'npm cache';                       p = "$L\npm-cache" },
    @{ n = 'pip cache';                       p = "$L\pip\cache" },
    @{ n = 'uv cache';                        p = "$L\uv\cache" },
    @{ n = 'NuGet cache';                     p = "$L\NuGet\v3-cache" },
    @{ n = 'Playwright browsers';             p = "$L\ms-playwright" },
    @{ n = 'vscode-cpptools index';           p = "$L\Microsoft\vscode-cpptools" },
    @{ n = 'NVIDIA DXCache';                  p = "$L\NVIDIA\DXCache" },
    @{ n = 'NVIDIA GLCache';                  p = "$L\NVIDIA\GLCache" },
    @{ n = 'Edge cache';                      p = "$L\Microsoft\Edge\User Data\Default\Cache" },
    @{ n = 'Chrome cache';                    p = "$L\Google\Chrome\User Data\Default\Cache" },
    @{ n = 'JetBrains caches';                p = "$L\JetBrains" },
    @{ n = 'Arduino15 staging';               p = "$L\Arduino15\staging" },
    @{ n = 'Crash dumps';                     p = "$L\CrashDumps" },
    @{ n = 'D3D shader cache';                p = "$L\D3DSCache" },
    @{ n = 'VS Code data';                    p = "$R\Code" },
    @{ n = 'Recycle Bin C:';                  p = 'C:\$Recycle.Bin' },
    @{ n = 'Recycle Bin D:';                  p = 'D:\$RECYCLE.BIN' },
    @{ n = 'WindowsApps (needs admin)';       p = 'C:\Program Files\WindowsApps' }
)

if (-not $SkipDrives) {
    "=== Drives ==="
    Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
        "{0}  total {1,7:N1} GB  free {2,7:N1} GB  used {3,5:N1}%" -f `
            $_.DeviceID, ($_.Size / 1GB), ($_.FreeSpace / 1GB), ((($_.Size - $_.FreeSpace) / $_.Size) * 100)
    }
    ""
    "=== Page / hibernation files ==="
    foreach ($f in 'C:\pagefile.sys', 'C:\hiberfil.sys', 'C:\swapfile.sys') {
        $i = Get-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue
        if ($i) { "{0,10:N2} GB  {1}" -f ($i.Length / 1GB), $f }
        else { "{0,10}  {1}" -f 'missing', $f }
    }
    ""
    "=== Cleanup targets ==="
}

$rows = @()
foreach ($t in $targets) {
    if (Test-Path -LiteralPath $t.p) {
        $b = [QS3]::Dir($t.p)
        $rows += [pscustomobject]@{ GB = [math]::Round($b / 1GB, 2); Name = $t.n; Path = $t.p }
    } else {
        $rows += [pscustomobject]@{ GB = -1; Name = $t.n; Path = $t.p }
    }
}

$rows | Sort-Object GB -Descending | ForEach-Object {
    if ($_.GB -lt 0) { "{0,10}  {1,-38} {2}" -f 'missing', $_.Name, $_.Path }
    else { "{0,10:N2} GB  {1,-38} {2}" -f $_.GB, $_.Name, $_.Path }
}
