# Install Shaner Consulting skills into ~/.claude/skills/
# Usage: powershell -ExecutionPolicy Bypass -File install.ps1
#
# Creates symlinks from ~/.claude/skills/ to the cloned repo files.
# Re-run after git pull to pick up new skills automatically.
# Requires: Run as Administrator (symlinks need elevated privileges on Windows)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsDir = Join-Path $env:USERPROFILE ".claude" "skills"

# Skills to install: source filename -> target relative path
$Skills = @{
    "shaner-consulting.md" = "shaner-consulting\SKILL.md"
    "process-mapping.md"   = "shaner-consulting\process-mapping.md"
    "first-run.md"         = "first-run\SKILL.md"
    "bootup.md"            = "bootup\SKILL.md"
    "deploy.md"            = "deploy\SKILL.md"
}

Write-Host "Installing Shaner Consulting skills..."
Write-Host "Source: $ScriptDir"
Write-Host "Target: $SkillsDir"
Write-Host ""

foreach ($srcFile in $Skills.Keys) {
    $targetPath = $Skills[$srcFile]
    $targetFull = Join-Path $SkillsDir $targetPath
    $targetDir  = Split-Path -Parent $targetFull
    $srcFull    = Join-Path $ScriptDir $srcFile

    # Create target directory
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }

    # Remove existing file/symlink
    if (Test-Path $targetFull) {
        Write-Host "  Replacing: $targetPath"
        Remove-Item $targetFull -Force
    } else {
        Write-Host "  Installing: $targetPath"
    }

    # Create symlink (requires elevated privileges)
    try {
        New-Item -ItemType SymbolicLink -Path $targetFull -Target $srcFull | Out-Null
    } catch {
        Write-Host "  ERROR: Symlink failed. Copying instead (updates won't auto-propagate)."
        Copy-Item $srcFull $targetFull
    }
}

Write-Host ""
Write-Host "Done. Installed $($Skills.Count) skills."
Write-Host ""
Write-Host "Skills available:"
Write-Host "  /shaner-consulting  -- AI consulting framework (Process + Context)"
Write-Host "  /process-mapping    -- Extract and structure processes"
Write-Host "  /first-run          -- Post-implementation validation"
Write-Host "  /bootup             -- Morning centering ritual (needs customization)"
Write-Host "  /deploy             -- End-of-session wrap-up (needs customization)"
Write-Host ""
Write-Host "Note: bootup.md and deploy.md have [bracketed-placeholders] you need to"
Write-Host "customize for your environment. See the README for details."
