#!/usr/bin/env python
"""
Diagnostic test for phone number output.
This script directly manipulates the phone number generation to track what's happening.
"""

import sys
from pathlib import Path

from loguru import logger
from ptbr_sampler.br_location_class import BrazilianLocationSampler
from ptbr_sampler.sampler import parse_result
from ptbr_sampler.utils.phone import generate_phone_number
from ptbr_sampler.br_name_class import NameComponents

# Set up detailed logging
logger.remove()
logger.add(sys.stderr, level="DEBUG", format="{time} | {level} | {module}:{function}:{line} | {message}")

print("=" * 80)
print("DIAGNOSING PHONE NUMBER OUTPUT ISSUES")
print("=" * 80)

# Initialize location sampler
location_sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')

# Test cities with known DDDs
test_cities = {
    'São Paulo': '11', 
    'Rio de Janeiro': '21',
    'Brasília': '61'
}

# Create test results
test_results = []
print("\nGenerating test data with explicit phone numbers...")

for city_name, expected_ddd in test_cities.items():
    # Create a simple name components object
    name = NameComponents("Test", "Middle", "User")
    
    # Get state info for this city
    state_abbr = None
    state_name = None
    for key, data in location_sampler.city_data_by_name.items():
        if key == city_name:
            state_abbr = data.get('city_uf')
            # Find state name from abbreviation
            for state, state_data in location_sampler.data['states'].items():
                if state_data.get('state_abbr') == state_abbr:
                    state_name = state
                    break
            break
    
    if not state_name or not state_abbr:
        print(f"Could not find state info for {city_name}, skipping")
        continue
        
    # Create location string
    location = f"{city_name}, {state_name} ({state_abbr})"
    
    # Generate a phone number directly
    ddd = location_sampler.city_data_by_name.get(city_name, {}).get('ddd')
    if not ddd:
        print(f"No DDD found for {city_name}")
        continue
        
    phone = generate_phone_number(ddd)
    print(f"Generated phone for {city_name}: {phone} (DDD: {ddd})")
    
    # Create documents dictionary with phone
    documents = {'phone': phone}
    
    # Add to test results
    test_results.append((location, name, documents, (state_name, state_abbr, city_name)))

# Now parse these results
print("\nParsing results and checking phone preservation...")
for i, (location, name, documents, state_info) in enumerate(test_results):
    # Check if phone is in documents
    phone_in_docs = 'phone' in documents
    phone_value = documents.get('phone', 'MISSING')
    print(f"Result {i+1} - Documents has phone? {phone_in_docs}, value: {phone_value}")
    
    # Call parse_result to see if it preserves the phone
    result = parse_result(location, name, documents, state_info)
    
    # Check if phone is in the parsed result
    phone_in_result = 'phone' in result
    result_phone = result.get('phone', 'MISSING')
    print(f"Result {i+1} - Parsed result has phone? {phone_in_result}, value: {result_phone}")
    print(f"  Name: {result['name']}")
    print(f"  City: {result['city']}, {result['state']} ({result['state_abbr']})")
    print("-" * 50)

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80) 