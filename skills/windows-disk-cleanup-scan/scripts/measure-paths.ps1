param(
    [Parameter(Mandatory = $true)][string[]]$Paths,
    [switch]$Children,
    [int]$TopN = 0
)

# Measure the size of one or more paths.
# -Children: measure every immediate child directory instead of the path itself.
# NOTE: keep this file ASCII-only; Windows PowerShell 5.1 parses BOM-less UTF-8 as ANSI.

$ErrorActionPreference = 'SilentlyContinue'

Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.IO;

public class QS
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

$rows = New-Object System.Collections.ArrayList

foreach ($p in $Paths) {
    if (-not (Test-Path -LiteralPath $p)) {
        [void]$rows.Add([pscustomobject]@{ GB = -1; Path = $p; Note = 'not-exist' })
        continue
    }
    if ($Children) {
        Get-ChildItem -LiteralPath $p -Force -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $b = [QS]::Dir($_.FullName)
            [void]$rows.Add([pscustomobject]@{ GB = [math]::Round($b / 1GB, 2); Path = $_.FullName; Note = '' })
        }
    } else {
        $b = [QS]::Dir($p)
        [void]$rows.Add([pscustomobject]@{ GB = [math]::Round($b / 1GB, 2); Path = $p; Note = '' })
    }
}

$sorted = $rows | Sort-Object GB -Descending
if ($TopN -gt 0) { $sorted = $sorted | Select-Object -First $TopN }

$sorted | ForEach-Object {
    if ($_.GB -lt 0) {
        "{0,10}  {1}" -f 'missing', $_.Path
    } else {
        "{0,10:N2} GB  {1}" -f $_.GB, $_.Path
    }
}
