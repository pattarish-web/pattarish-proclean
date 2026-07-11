# Restore agent skills (cleaning-seo-website)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "==> Installing external skills"

npx --yes skills add https://github.com/ulpi-io/skills --skill browse-seo -a cursor -y
npx --yes skills add AsyrafHussin/agent-skills --skill seo-best-practices -a cursor -y
npx --yes skills add https://github.com/ulpi-io/skills --skill nodejs -a cursor -y

Write-Host "==> Syncing custom Sangkan skills to ~/.cursor/skills"
$src = Join-Path (Get-Location) ".cursor\skills"
$dst = Join-Path $env:USERPROFILE ".cursor\skills"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
Get-ChildItem $src -Directory -Filter "sangkan-*" | ForEach-Object {
  $target = Join-Path $dst $_.Name
  if (Test-Path $target) { Remove-Item -Recurse -Force $target }
  Copy-Item $_.FullName $target -Recurse -Force
  Write-Host "  synced $($_.Name)"
}

Write-Host "==> Done. Reload Cursor Window."
