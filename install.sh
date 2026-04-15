#!/bin/bash
# Install Shaner Consulting skills into ~/.claude/skills/
# Usage: ./install.sh
#
# Creates symlinks from ~/.claude/skills/ to the cloned repo files.
# Re-run after git pull to pick up new skills automatically.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"

# Skills to install (repo filename → skill directory name)
declare -A SKILLS=(
  ["shaner-consulting.md"]="shaner-consulting/SKILL.md"
  ["process-mapping.md"]="shaner-consulting/process-mapping.md"
  ["first-run.md"]="first-run/SKILL.md"
  ["bootup.md"]="bootup/SKILL.md"
  ["deploy.md"]="deploy/SKILL.md"
)

echo "Installing Shaner Consulting skills..."
echo "Source: $SCRIPT_DIR"
echo "Target: $SKILLS_DIR"
echo ""

for src_file in "${!SKILLS[@]}"; do
  target_path="${SKILLS[$src_file]}"
  target_dir="$SKILLS_DIR/$(dirname "$target_path")"
  target_file="$SKILLS_DIR/$target_path"
  src_path="$SCRIPT_DIR/$src_file"

  # Create target directory
  mkdir -p "$target_dir"

  # Remove existing file/symlink
  if [ -e "$target_file" ] || [ -L "$target_file" ]; then
    echo "  Replacing: $target_path"
    rm "$target_file"
  else
    echo "  Installing: $target_path"
  fi

  # Create symlink
  ln -s "$src_path" "$target_file"
done

echo ""
echo "Done. Installed ${#SKILLS[@]} skills."
echo ""
echo "Skills available:"
echo "  /shaner-consulting  — AI consulting framework (Process + Context)"
echo "  /process-mapping    — Extract and structure processes"
echo "  /first-run          — Post-implementation validation"
echo "  /bootup             — Morning centering ritual (needs customization)"
echo "  /deploy             — End-of-session wrap-up (needs customization)"
echo ""
echo "Note: bootup.md and deploy.md have [bracketed-placeholders] you need to"
echo "customize for your environment. See the README for details."
