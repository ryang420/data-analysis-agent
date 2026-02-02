#!/usr/bin/env python3
"""
Load project environment variables and output export statements for local runs.
Reads from .env in project root. Usage: eval $(python scripts/load_env.py)
Or: source <(python scripts/load_env.py)
"""
import os
import sys

# Look for .env: repo root (parent of backend) or backend dir
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
repo_root = os.path.dirname(backend_dir)
# Prefer .env at repo root, then backend
env_file = os.path.join(repo_root, ".env")
if not os.path.isfile(env_file):
    env_file = os.path.join(backend_dir, ".env")

# Load .env if present
if os.path.isfile(env_file):
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Remove leading export and any surrounding quotes
                if value:
                    value = value.replace("'", "'\\''")
                    print(f"export {key}='{value}'")
        print("# Loaded from .env", file=sys.stderr)
    except Exception as e:
        print(f"# Error loading .env: {e}", file=sys.stderr)
        sys.exit(1)
else:
    print("# No .env found at " + env_file, file=sys.stderr)
    sys.exit(0)
