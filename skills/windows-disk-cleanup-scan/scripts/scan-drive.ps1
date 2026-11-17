param(
    [Parameter(Mandatory = $true)][string]$Root,
    [Parameter(Mandatory = $true)][string]$OutFile,
    [long]$LargeThresholdMB = 300
)

# Single-pass disk scanner.
# Produces: total size, per-top-level-directory sizes, root files, and large files.
# Skips reparse points (junctions / symlinks) to avoid loops and double counting.
# NOTE: keep this file ASCII-only; Windows PowerShell 5.1 parses BOM-less UTF-8 as ANSI.

$ErrorActionPreference = 'SilentlyContinue'

Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.IO;

public class ScanOut
{
    public long Total;
    public Dictionary<string, long> Dirs = new Dictionary<string, long>();
    public List<object[]> Large = new List<object[]>();
    public List<object[]> RootFiles = new List<object[]>();
}

public class DiskScanner
{
    private static void Walk(string path, ScanOut o, long threshold)
    {
        var stack = new Stack<string>();
        stack.Push(path);
        while (stack.Count > 0)
        {
            string dir = stack.Pop();
            try
            {
                foreach (string f in Directory.EnumerateFiles(dir))
                {
                    try
                    {
                        long len = new FileInfo(f).Length;
                        o.Total += len;
                        if (len >= threshold) o.Large.Add(new object[] { f, len });
                    }
                    catch { }
                }
            }
            catch { }
            try
            {
                foreach (string d in Directory.EnumerateDirectories(dir))
                {
                    bool skip = false;
                    try
                    {
                        if ((File.GetAttributes(d) & FileAttributes.ReparsePoint) != 0) skip = true;
                    }
                    catch { skip = true; }
                    if (!skip) stack.Push(d);
                }
            }
            catch { }
        }
    }

    public static ScanOut Run(string root, long threshold)
    {
        var o = new ScanOut();

        try
        {
            foreach (string f in Directory.EnumerateFiles(root))
            {
                try
                {
                    long len = new FileInfo(f).Length;
                    o.Total += len;
                    o.RootFiles.Add(new object[] { Path.GetFileName(f), len });
                    if (len >= threshold) o.Large.Add(new object[] { f, len });
                }
                catch { }
            }
        }
        catch { }

        try
        {
            foreach (string d in Directory.EnumerateDirectories(root))
            {
                bool skip = false;
                try
                {
                    if ((File.GetAttributes(d) & FileAttributes.ReparsePoint) != 0) skip = true;
                }
                catch { skip = true; }
                if (skip) continue;

                long before = o.Total;
                Walk(d, o, threshold);
                o.Dirs[Path.GetFileName(d)] = o.Total - before;
            }
        }
        catch { }

        return o;
    }
}
"@

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$threshold = $LargeThresholdMB * 1MB
$o = [DiskScanner]::Run($Root, $threshold)

$result = [ordered]@{
    root       = $Root
    scannedAt  = (Get-Date).ToString('s')
    totalGB    = [math]::Round($o.Total / 1GB, 2)
    topDirs    = @($o.Dirs.GetEnumerator() | ForEach-Object {
                     [pscustomobject]@{ name = $_.Key; gb = [math]::Round($_.Value / 1GB, 2) }
                 } | Sort-Object gb -Descending)
    rootFiles  = @($o.RootFiles | ForEach-Object {
                     [pscustomobject]@{ name = $_[0]; gb = [math]::Round($_[1] / 1GB, 2) }
                 } | Sort-Object gb -Descending)
    largeFiles = @($o.Large | ForEach-Object {
                     [pscustomobject]@{ path = $_[0]; gb = [math]::Round($_[1] / 1GB, 2) }
                 } | Sort-Object gb -Descending | Select-Object -First 80)
    elapsedSec = [math]::Round($sw.Elapsed.TotalSeconds, 1)
}

$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $OutFile -Encoding UTF8
"$($result.root) DONE in $($result.elapsedSec)s total=$($result.totalGB)GB"
