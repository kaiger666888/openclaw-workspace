#!/usr/bin/env python3
"""Initialize a project-crew skill project."""
import os, sys, json

def main():
    if len(sys.argv) < 2:
        print("Usage: init_skill.py <project-name> [--dir <path>]")
        sys.exit(1)
    
    name = sys.argv[1]
    base_dir = "."
    if "--dir" in sys.argv:
        idx = sys.argv.index("--dir")
        base_dir = sys.argv[idx + 1]
    
    workdir = os.path.join(base_dir, f"crew-{name}")
    os.makedirs(workdir, exist_ok=True)
    
    crew_file = os.path.join(workdir, "crew.js")
    if not os.path.exists(crew_file):
        with open(crew_file, "w") as f:
            f.write(f"""module.exports = {{
  name: "{name}",
  steps: [
    // Add your steps here
  ]
}};
""")
        print(f"Created {crew_file}")
    
    print(f"Project '{name}' initialized at {workdir}")
    print(f"Edit crew.js to define your workflow, then run the orchestrator.")

if __name__ == "__main__":
    main()
