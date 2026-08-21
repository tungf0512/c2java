# One-command demo of the C2Java pipeline.
#
#   .\demo.ps1            run the whole story straight through
#   .\demo.ps1 -Pause     stop between sections so you can talk
#
# Reads artifacts produced by an earlier `rustprint migrate` run. Does not call
# the LLM API and does not consume quota.

param([switch]$Pause)

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$out  = Join-Path $root '.docker-data\output\dummy_c_project'
$docs = Join-Path $root '.docker-data\cache\dummy_c_project\c_docs\version_0\dummy_c_project\docs'

function Section($n, $title) {
    Write-Host ""
    Write-Host ("=" * 74) -ForegroundColor DarkGray
    Write-Host "  $n. $title" -ForegroundColor Cyan
    Write-Host ("=" * 74) -ForegroundColor DarkGray
    Write-Host ""
}

function Show-File($path, $label, $first = 0) {
    Write-Host "--- $label" -ForegroundColor Yellow
    if (Test-Path $path) {
        if ($first -gt 0) { $lines = Get-Content $path -TotalCount $first } else { $lines = Get-Content $path }
        foreach ($l in $lines) { Write-Host $l }
    } else {
        Write-Host "  (not found: $path)" -ForegroundColor Red
    }
    Write-Host ""
}

function Wait-Step {
    if ($Pause) {
        Write-Host "   [Enter to continue]" -ForegroundColor DarkGray
        $null = Read-Host
    }
}

if (-not (Test-Path $out)) {
    Write-Host "No generated output found at $out" -ForegroundColor Red
    Write-Host "Run the migration first - see DEMO.md" -ForegroundColor Red
    exit 1
}

Section 1 "The input: a C project of three files"
Show-File (Join-Path $root 'dummy_c_project\include\geometry.h') 'geometry.h'
Show-File (Join-Path $root 'dummy_c_project\src\geometry.c') 'geometry.c'
Wait-Step

Section 2 "Step one - the pipeline reads the C and writes documentation"
Show-File (Join-Path $docs 'overview.md') 'overview.md (first 22 lines, LLM-written)' 22
Write-Host "   (full file under .docker-data\cache\...\docs\)" -ForegroundColor DarkGray
Wait-Step

Section 3 "Step two - it writes an API README for the Java it is about to produce"
Show-File (Join-Path $out 'README.md') 'README.md (generated, first 20 lines)' 20
Wait-Step

Section 4 "Step three - the generated Java"
$src = Join-Path $out 'src\main\java\com\migration\generated\dummy_c_project\geometry'
Show-File (Join-Path $src 'Point.java')    'Point.java   (C struct -> Java record)'
Show-File (Join-Path $src 'Geometry.java') 'Geometry.java (C function -> static method)'
Wait-Step

Section 5 "Proof: compile from clean and run the original C assertions"
Write-Host "Building inside the container and checking behaviour..." -ForegroundColor DarkGray
Write-Host ""
$drive   = $root.Substring(0, 1).ToLower()
$wslRoot = '/mnt/' + $drive + $root.Substring(2).Replace('\', '/')
wsl -d Ubuntu-24.04 -e bash -lc "cd '$wslRoot' && docker compose run --rm --no-TTY c2java bash /workspace/c2java/docker/validate-output.sh"

Write-Host ""
Write-Host "Everything above is on disk at .docker-data\ - open it in VS Code." -ForegroundColor Green
