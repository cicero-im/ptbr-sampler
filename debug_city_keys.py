#!/usr/bin/env python
"""
Debug script to identify how cities are keyed in different data files.
"""

import json
from pathlib import Path
import sys

from loguru import logger
from ptbr_sampler.br_location_class import BrazilianLocationSampler

# Set up logger to show debug output
logger.remove()
logger.add(sys.stderr, level="DEBUG")

print("=" * 80)
print("DEBUGGING CITY KEYS IN DATA FILES")
print("=" * 80)

# Known cities to check
cities_to_check = [
    'São Paulo', 
    'Rio de Janeiro', 
    'Niterói', 
    'Cruz Alta', 
    'Marília', 
    'Codó', 
    'Pacatuba'
]

# Load cities_with_ceps.json
print("\n1. Examining cities_with_ceps.json")
print("-" * 80)

with open('ptbr_sampler/data/cities_with_ceps.json', 'r', encoding='utf-8') as f:
    ceps_data = json.load(f)

# Find the city keys in ceps_data
print("Looking for cities in cities_with_ceps.json:")
for city_name in cities_to_check:
    found = False
    for key, data in ceps_data.get('cities', {}).items():
        if data.get('city_name') == city_name:
            found = True
            print(f"{city_name}: Found with key '{key}', city_uf: {data.get('city_uf')}, DDD: {data.get('ddd', 'MISSING')}")
            break
    
    if not found:
        # Try to find with partial match (key might contain the city name)
        for key, data in ceps_data.get('cities', {}).items():
            if city_name in key:
                found = True
                print(f"{city_name}: Found with partial key match '{key}', city_name: {data.get('city_name')}, DDD: {data.get('ddd', 'MISSING')}")
                break
    
    if not found:
        print(f"{city_name}: NOT FOUND in cities_with_ceps.json")

# Load locations_data.json
print("\n2. Examining locations_data.json")
print("-" * 80)

with open('ptbr_sampler/data/locations_data.json', 'r', encoding='utf-8') as f:
    locations_data = json.load(f)

# Find the city keys in locations_data
print("Looking for cities in locations_data.json:")
for city_name in cities_to_check:
    found = False
    for key, data in locations_data.get('cities', {}).items():
        if data.get('city_name') == city_name:
            found = True
            print(f"{city_name}: Found with key '{key}', city_uf: {data.get('city_uf')}, DDD: {data.get('ddd', 'MISSING')}")
            break
    
    if not found:
        # Try to find with partial match (key might contain the city name)
        for key, data in locations_data.get('cities', {}).items():
            if city_name in key:
                found = True
                print(f"{city_name}: Found with partial key match '{key}', city_name: {data.get('city_name')}, DDD: {data.get('ddd', 'MISSING')}")
                break
    
    if not found:
        print(f"{city_name}: NOT FOUND in locations_data.json")

# Now check how the BrazilianLocationSampler processes these
print("\n3. Examining how BrazilianLocationSampler processes city keys")
print("-" * 80)

# Initialize with cities_with_ceps.json
sampler_ceps = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')

print("City data in sampler after loading cities_with_ceps.json:")
for city_name in cities_to_check:
    if city_name in sampler_ceps.city_data_by_name:
        city_data = sampler_ceps.city_data_by_name[city_name]
        print(f"{city_name}: Found with DDD {city_data.get('ddd', 'MISSING')}")
    else:
        print(f"{city_name}: NOT FOUND in sampler's city_data_by_name")

# Update with locations_data
print("\nUpdating sampler with locations_data...")
sampler_ceps.update_cities(locations_data.get('cities', {}))

print("\nCity data in sampler after update:")
for city_name in cities_to_check:
    if city_name in sampler_ceps.city_data_by_name:
        city_data = sampler_ceps.city_data_by_name[city_name]
        print(f"{city_name}: Found with DDD {city_data.get('ddd', 'MISSING')}")
    else:
        print(f"{city_name}: NOT FOUND in sampler's city_data_by_name")

print("\n" + "=" * 80)
print("DEBUGGING COMPLETE")
print("=" * 80) 