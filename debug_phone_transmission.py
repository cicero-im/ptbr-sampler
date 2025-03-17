#!/usr/bin/env python
"""
Simplified debug script for phone number transmission issues.
Directly executes the CLI command and analyzes the JSONL output.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from loguru import logger
from ptbr_sampler.utils.phone import generate_phone_number

# Set up logger
logger.remove()
logger.add(sys.stderr, level="DEBUG")

print("=" * 80)
print("DEBUGGING PHONE NUMBER TRANSMISSION ISSUES")
print("=" * 80)

# 1. Direct testing of phone number generation
print("\n1. DIRECT PHONE NUMBER GENERATION")
print("-" * 80)
test_ddds = ["11", "21", "41", "51"]
print("Testing direct phone number generation with hardcoded DDDs:")
for ddd in test_ddds:
    phone = generate_phone_number(ddd)
    print(f"DDD {ddd} → Phone: {phone}")

# 2. Direct execution of CLI command with output to JSONL
output_file = "direct_output.jsonl"
print(f"\n2. EXECUTING CLI COMMAND WITH OUTPUT TO {output_file}")
print("-" * 80)

# Build the CLI command - using a minimal set of parameters
cli_command = [
    "./run_cli.py", 
    "--qty", "3",
    "--always-phone",
    "--save-to-jsonl", output_file
]

print(f"Executing command: {' '.join(cli_command)}")
try:
    result = subprocess.run(cli_command, capture_output=True, text=True)
    print(f"Exit code: {result.returncode}")
    if result.stdout:
        print("Command stdout:")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    if result.stderr:
        print("Command stderr:")
        print(result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
except Exception as e:
    print(f"Error executing command: {e}")

# 3. Analyze the output JSONL file
print(f"\n3. ANALYZING OUTPUT JSONL FILE: {output_file}")
print("-" * 80)

if os.path.exists(output_file):
    try:
        results = []
        with open(output_file, 'r', encoding='utf-8') as f:
            for line in f:
                results.append(json.loads(line))
        
        print(f"Successfully loaded {len(results)} results from JSONL file")
        
        # Analyze each result for phone numbers and DDDs
        for i, result in enumerate(results):
            name = result.get('name', 'No name')
            city = result.get('city', 'No city')
            state = result.get('state', 'No state')
            phone = result.get('phone', 'No phone')
            
            # Extract DDD from phone if present
            ddd = "None"
            if phone != 'No phone' and '(' in phone and ')' in phone:
                ddd = phone.split('(')[1].split(')')[0].strip()
            
            print(f"\nSample {i+1}:")
            print(f"  Person: {name}")
            print(f"  Location: {city}, {state}")
            print(f"  Phone: {phone}")
            print(f"  Extracted DDD: {ddd}")
            
            # Verify if city and DDD match known patterns
            if city in ["São Paulo", "Sao Paulo"] and ddd != "11":
                print(f"  *** WARNING: São Paulo should have DDD 11 but has {ddd} ***")
            elif city == "Rio de Janeiro" and ddd != "21":
                print(f"  *** WARNING: Rio de Janeiro should have DDD 21 but has {ddd} ***")
    except Exception as e:
        print(f"Error analyzing JSONL file: {e}")
else:
    print(f"Output file {output_file} does not exist")

print("\n" + "=" * 80)
print("DEBUGGING COMPLETE")
print("=" * 80) 