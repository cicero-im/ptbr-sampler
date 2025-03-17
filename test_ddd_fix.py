#!/usr/bin/env python
"""
Test script to verify DDD preservation and phone number generation with correct DDDs.
"""

import json
from pathlib import Path
import sys

from loguru import logger
from ptbr_sampler.br_location_class import BrazilianLocationSampler
from ptbr_sampler.utils.phone import generate_phone_number

# Set up logger to show debug output
logger.remove()
logger.add(sys.stderr, level="DEBUG")

print("=" * 80)
print("TESTING DDD FIXES")
print("=" * 80)

# Test 1: Load cities_with_ceps.json and verify DDDs for specific cities
print("\nTEST 1: Verify initial DDDs for specific cities")
print("-" * 80)

# Known cities with their correct DDDs
known_cities = {
    'São Paulo': '11',
    'Rio de Janeiro': '21',
    'Niterói': '21',
    'Cruz Alta': '55',
    'Marília': '14', 
    'Codó': '99',
    'Pacatuba': '85',  # Assuming Pacatuba CE here (there's one in SE with 79)
}

sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')

print("Checking known cities and their DDDs:")
for city_name, expected_ddd in known_cities.items():
    if city_name in sampler.city_data_by_name:
        actual_ddd = sampler.city_data_by_name[city_name].get('ddd', 'MISSING')
        result = "MATCH" if actual_ddd == expected_ddd else f"MISMATCH (expected {expected_ddd})"
        print(f"{city_name}: DDD {actual_ddd} - {result}")
    else:
        print(f"{city_name}: NOT FOUND in city data")

# Test 2: Update with locations_data.json and verify DDDs are preserved
print("\nTEST 2: Update with locations_data.json and verify DDDs are preserved")
print("-" * 80)

# Load locations_data.json
with open('ptbr_sampler/data/locations_data.json', 'r', encoding='utf-8') as f:
    locations_data = json.load(f)

# Check if locations_data already has DDDs
cities_with_ddd = sum(1 for city_data in locations_data.get('cities', {}).values() if 'ddd' in city_data)
print(f"Cities with DDD in locations_data.json: {cities_with_ddd}/{len(locations_data.get('cities', {}))}")

# Create a modified version of locations_data with some DDDs removed
test_cities = {}
for city_name in known_cities.keys():
    # Find the city in locations_data
    for key, data in locations_data.get('cities', {}).items():
        if data.get('city_name') == city_name:
            modified_data = data.copy()
            if 'ddd' in modified_data:
                del modified_data['ddd']  # Remove DDD to test preservation
                test_cities[key] = modified_data
                print(f"Created test entry for {city_name} with DDD removed")
                break

# Update sampler with modified locations_data
print("\nDDDs before update:")
for city_name in known_cities.keys():
    if city_name in sampler.city_data_by_name:
        ddd = sampler.city_data_by_name[city_name].get('ddd', 'MISSING')
        print(f"{city_name}: DDD {ddd}")

# Update with the test cities (some with missing DDDs)
print("\nUpdating with test cities (with DDDs removed)...")
sampler.update_cities(test_cities)

# Check the results after update
print("\nDDDs after update:")
for city_name, expected_ddd in known_cities.items():
    if city_name in sampler.city_data_by_name:
        actual_ddd = sampler.city_data_by_name[city_name].get('ddd', 'MISSING')
        result = "PRESERVED" if actual_ddd == expected_ddd else "LOST"
        print(f"{city_name}: DDD {actual_ddd} - {result}")

# Test 3: Phone number generation with the correct DDDs
print("\nTEST 3: Generate phone numbers for cities and verify correct DDDs are used")
print("-" * 80)

# Test for each known city
for city_name, expected_ddd in known_cities.items():
    if city_name in sampler.city_data_by_name:
        city_data = sampler.city_data_by_name[city_name]
        ddd = city_data.get('ddd', 'MISSING')
        
        if ddd != 'MISSING':
            try:
                phone = generate_phone_number(ddd)
                used_ddd = phone.split('(')[1].split(')')[0].strip()
                
                if used_ddd == ddd and ddd == expected_ddd:
                    result = "CORRECT"
                elif used_ddd == ddd and ddd != expected_ddd:
                    result = f"WRONG DDD IN DATA (using {ddd}, expected {expected_ddd})"
                else:
                    result = f"WRONG DDD IN PHONE (using {used_ddd}, expected {ddd})"
                    
                print(f"{city_name}: Generated phone {phone} - {result}")
            except Exception as e:
                print(f"{city_name}: Error generating phone - {e}")
        else:
            print(f"{city_name}: Missing DDD in city data")
    else:
        print(f"{city_name}: City not found in data")

print("\n" + "=" * 80)
print("TESTING COMPLETE")
print("=" * 80) 