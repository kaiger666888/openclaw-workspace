#!/usr/bin/env python3
"""Validate and package a project-crew skill for distribution."""
import os, sys, ast, re

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = ["SKILL.md"]
OPTIONAL_DIRS = ["scripts", "references", "assets"]

def validate_crew_js(filepath):
    """Basic validation of crew.js structure."""
    with open(filepath) as f:
        content = f.read()
    
    errors = []
    # Check module.exports exists
    if "module.exports" not in content:
        errors.append("Missing module.exports")
    # Check name field
    if not re.search(r'name\s*:\s*["\']', content):
        errors.append("Missing 'name' field")
    # Check steps array
    if "steps" not in content:
        errors.append("Missing 'steps' array")
    return errors

def main():
    print(f"Validating skill at: {SKILL_DIR}")
    
    # Check required files
    for f in REQUIRED:
        path = os.path.join(SKILL_DIR, f)
        if not os.path.exists(path):
            print(f"❌ Missing required file: {f}")
            sys.exit(1)
        print(f"✅ {f}")
    
    # Check optional dirs
    for d in OPTIONAL_DIRS:
        path = os.path.join(SKILL_DIR, d)
        if os.path.exists(path):
            count = len(os.listdir(path))
            print(f"✅ {d}/ ({count} files)")
        else:
            print(f"⚠️  {d}/ (missing, optional)")
    
    # Validate SKILL.md frontmatter
    skill_md = os.path.join(SKILL_DIR, "SKILL.md")
    with open(skill_md) as f:
        content = f.read()
    
    if not content.startswith("---"):
        print("❌ SKILL.md missing YAML frontmatter")
        sys.exit(1)
    
    if "name:" not in content.split("---")[1]:
        print("❌ SKILL.md missing 'name' in frontmatter")
        sys.exit(1)
    
    if "description:" not in content.split("---")[1]:
        print("❌ SKILL.md missing 'description' in frontmatter")
        sys.exit(1)
    
    lines = content.split("\n")
    if len(lines) > 500:
        print(f"⚠️  SKILL.md is {len(lines)} lines (recommend < 500)")
    else:
        print(f"✅ SKILL.md length: {len(lines)} lines")
    
    # Check scripts
    scripts_dir = os.path.join(SKILL_DIR, "scripts")
    if os.path.exists(scripts_dir):
        for f in os.listdir(scripts_dir):
            if f.endswith(".py"):
                os.chmod(os.path.join(scripts_dir, f), 0o755)
                print(f"✅ {f} (made executable)")
    
    # Check references
    refs_dir = os.path.join(SKILL_DIR, "references")
    if os.path.exists(refs_dir):
        for f in os.listdir(refs_dir):
            if f.endswith(".md"):
                print(f"✅ references/{f}")
    
    total_files = sum(len(files) for _, _, files in os.walk(SKILL_DIR))
    print(f"\n✅ Skill '{SKILL_DIR}' validated successfully!")
    print(f"   Files: {total_files}")
    print(f"   Ready for installation via clawhub publish")

if __name__ == "__main__":
    main()
