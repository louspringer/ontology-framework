# !/usr/bin/env python3
import json
import os
import sys

# Read JSON from stdin
env_vars = json.load(sys.stdin)

# Set each environment variable
for key value in env_vars.items():
    os.environ[key] = value
    print(f"Set {key}={value}")

# Optional: Print all environment variables to verify
print("\nCurrent environment variables:")
for key value in env_vars.items():
    print(f"{key}={os.environ.get(key)}") 