#!/usr/bin/env python
"""
Test script to check how the --easy flag interacts with DDD retrieval for phone numbers.
"""

import sys
import json
from pathlib import Path
from loguru import logger

# Set up logger to show debug output
logger.remove()
logger.add(sys.stderr, level="DEBUG")

print("=" * 80)
print("TESTING DDD RETRIEVAL WITH --easy FLAG")
print("=" * 80)

# Step 1: Check DDD in cities_with_ceps.json
print("\n1. Checking DDDs in cities_with_ceps.json")
print("-" * 80)

cities_to_check = ['São Paulo', 'Cruz Alta', 'Pacatuba', 'Rio de Janeiro', 'Belém']

with open('ptbr_sampler/data/cities_with_ceps.json', 'r', encoding='utf-8') as f:
    cities_data = json.load(f)

for city_name in cities_to_check:
    found = False
    for key, data in cities_data.get('cities', {}).items():
        if data.get('city_name') == city_name:
            found = True
            print(f"{city_name}: Found with key '{key}', DDD: {data.get('ddd', 'MISSING')}")
            break
    
    if not found:
        print(f"{city_name}: NOT FOUND in cities_with_ceps.json")

# Step 2: Test direct DDD retrieval with BrazilianLocationSampler
print("\n2. Testing direct DDD retrieval with BrazilianLocationSampler")
print("-" * 80)

from ptbr_sampler.br_location_class import BrazilianLocationSampler
from ptbr_sampler.utils.phone import generate_phone_number

sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')

for city_name in cities_to_check:
    city_data = sampler.city_data_by_name.get(city_name, {})
    ddd = city_data.get('ddd', 'MISSING')
    
    print(f"{city_name}: DDD from sampler: {ddd}")
    
    if ddd != 'MISSING':
        try:
            phone = generate_phone_number(ddd)
            print(f"  Generated phone: {phone}")
        except Exception as e:
            print(f"  Error generating phone: {e}")

# Step 3: Test with CLI using the --easy flag
print("\n3. Testing CLI with --easy flag")
print("-" * 80)

import tempfile
import subprocess

# Create a temp file for the output
with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as temp:
    temp_file = temp.name

print(f"Temporary output file: {temp_file}")

# Run the CLI with --easy flag
cmd = f"./run_cli.py --easy 3 --save-to-jsonl {temp_file}"
print(f"Running command: {cmd}")

result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(f"Command exit code: {result.returncode}")

if result.returncode == 0:
    print("Command executed successfully")
else:
    print(f"Command failed: {result.stderr}")

# Check the output file
print("\n4. Analyzing output from --easy command")
print("-" * 80)

try:
    with open(temp_file, 'r') as f:
        results = [json.loads(line) for line in f]
    
    print(f"Found {len(results)} results in the output file")
    
    for i, result in enumerate(results):
        name = result.get('name', 'No name')
        city = result.get('city', 'No city')
        state = result.get('state', 'No state')
        state_abbr = result.get('state_abbr', '')
        phone = result.get('phone', 'No phone')
        
        print(f"\nSample {i+1}:")
        print(f"  Name: {name}")
        print(f"  Location: {city}, {state} ({state_abbr})")
        print(f"  Phone: {phone}")
        
        # Validate the DDD
        if phone != 'No phone':
            phone_ddd = phone.split('(')[1].split(')')[0].strip() if '(' in phone and ')' in phone else ''
            print(f"  Phone DDD: {phone_ddd}")
            
            # Try to find the expected DDD for this city
            city_data = sampler.city_data_by_name.get(city, {})
            expected_ddd = city_data.get('ddd', 'MISSING')
            
            if expected_ddd != 'MISSING':
                if phone_ddd == expected_ddd:
                    print(f"  ✅ DDD is correct for {city}")
                else:
                    print(f"  ❌ DDD mismatch for {city}: Expected {expected_ddd}, got {phone_ddd}")
            else:
                print(f"  ⚠️ No expected DDD found for {city}")
except Exception as e:
    print(f"Error analyzing output file: {e}")

# Clean up
import os
try:
    os.remove(temp_file)
    print(f"\nTemporary file {temp_file} removed")
except Exception as e:
    print(f"Error removing temporary file: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80) 