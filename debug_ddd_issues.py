#!/usr/bin/env python
"""
Debugging script to identify issues with DDD (area code) assignment in phone numbers.
Tests multiple hypotheses for why phone numbers might have incorrect DDDs.
"""

import json
import random
from pathlib import Path
import sys

from loguru import logger
from ptbr_sampler.br_location_class import BrazilianLocationSampler
from ptbr_sampler.utils.phone import generate_phone_number

# Set up logger to show more detailed output
logger.remove()
logger.add(sys.stderr, level="DEBUG")

print("=" * 80)
print("DEBUGGING DDD (AREA CODE) ISSUES IN PHONE NUMBER GENERATION")
print("=" * 80)

# Hypothesis 1: The cities_with_ceps.json file doesn't have DDDs for all cities
print("\n\nHYPOTHESIS 1: The cities_with_ceps.json file doesn't have DDDs for all cities")
print("-" * 80)

try:
    with open('ptbr_sampler/data/cities_with_ceps.json', 'r', encoding='utf-8') as f:
        ceps_data = json.load(f)
    
    total_cities = len(ceps_data.get('cities', {}))
    cities_with_ddd = sum(1 for city_data in ceps_data.get('cities', {}).values() 
                         if 'ddd' in city_data)
    
    print(f"Total cities in cities_with_ceps.json: {total_cities}")
    print(f"Cities with DDD: {cities_with_ddd}")
    print(f"Cities missing DDD: {total_cities - cities_with_ddd}")
    
    if cities_with_ddd == total_cities:
        print("RESULT: All cities have DDDs in cities_with_ceps.json - NOT the issue.")
    else:
        print(f"RESULT: {total_cities - cities_with_ddd} cities are missing DDDs - could be an issue!")
        # List a few examples of cities without DDDs
        cities_without_ddd = [city_name for city_name, city_data in ceps_data.get('cities', {}).items() 
                             if 'ddd' not in city_data]
        print(f"Sample cities without DDD: {cities_without_ddd[:5]}")
except Exception as e:
    print(f"Error checking cities_with_ceps.json: {e}")

# Hypothesis 2: The BrazilianLocationSampler is not correctly loading DDDs from the file
print("\n\nHYPOTHESIS 2: BrazilianLocationSampler is not correctly loading DDDs into memory")
print("-" * 80)

try:
    # Initialize sampler with cities_with_ceps.json
    sampler_ceps = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
    
    cities_in_sampler = len(sampler_ceps.city_data_by_name)
    cities_with_ddd_in_sampler = sum(1 for city_data in sampler_ceps.city_data_by_name.values() 
                                    if 'ddd' in city_data)
    
    print(f"Total cities loaded in sampler: {cities_in_sampler}")
    print(f"Cities with DDD in sampler: {cities_with_ddd_in_sampler}")
    print(f"Cities missing DDD in sampler: {cities_in_sampler - cities_with_ddd_in_sampler}")
    
    if cities_with_ddd_in_sampler == cities_in_sampler:
        print("RESULT: All cities in the sampler have DDDs - NOT the issue.")
    else:
        print(f"RESULT: {cities_in_sampler - cities_with_ddd_in_sampler} cities in the sampler are missing DDDs - could be an issue!")
        # List a few examples of cities without DDDs
        cities_without_ddd = [city_name for city_name, city_data in sampler_ceps.city_data_by_name.items() 
                             if 'ddd' not in city_data]
        print(f"Sample cities without DDD in sampler: {cities_without_ddd[:5]}")
except Exception as e:
    print(f"Error checking BrazilianLocationSampler: {e}")

# Hypothesis 3: Updating the sampler with locations_data.json overwrites DDDs
print("\n\nHYPOTHESIS 3: Updating the sampler with locations_data.json overwrites DDDs")
print("-" * 80)

try:
    # First check if locations_data.json has DDDs
    with open('ptbr_sampler/data/locations_data.json', 'r', encoding='utf-8') as f:
        locations_data = json.load(f)
    
    total_cities_locations = len(locations_data.get('cities', {}))
    cities_with_ddd_locations = sum(1 for city_data in locations_data.get('cities', {}).values() 
                                  if 'ddd' in city_data)
    
    print(f"Total cities in locations_data.json: {total_cities_locations}")
    print(f"Cities with DDD in locations_data.json: {cities_with_ddd_locations}")
    
    # Now test if updating overwrites DDDs
    sampler_before = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
    
    # Sample a few cities to compare before and after
    test_cities = []
    for _ in range(5):
        _, _, city_name = sampler_before.get_state_and_city()
        test_cities.append(city_name)
    
    print("\nSample cities before update:")
    for city in test_cities:
        if city in sampler_before.city_data_by_name:
            ddd = sampler_before.city_data_by_name[city].get('ddd', 'MISSING')
            print(f"{city}: DDD {ddd}")
    
    # Update with locations_data
    sampler_before.update_cities(locations_data.get('cities', {}))
    
    print("\nSame cities after update:")
    for city in test_cities:
        if city in sampler_before.city_data_by_name:
            ddd = sampler_before.city_data_by_name[city].get('ddd', 'MISSING')
            print(f"{city}: DDD {ddd}")
    
    print("\nRESULT: Check if DDDs changed or went missing after the update.")
except Exception as e:
    print(f"Error testing hypothesis 3: {e}")

# Hypothesis 4: get_state_and_city() is not returning cities that exist in city_data_by_name
print("\n\nHYPOTHESIS 4: get_state_and_city() is returning cities not in city_data_by_name")
print("-" * 80)

try:
    sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
    
    cities_found_count = 0
    cities_missing_count = 0
    
    print("Testing 10 random cities from get_state_and_city():")
    for i in range(10):
        state_name, state_abbr, city_name = sampler.get_state_and_city()
        
        if city_name in sampler.city_data_by_name:
            ddd = sampler.city_data_by_name[city_name].get('ddd', 'MISSING')
            print(f"{i+1}. {city_name} ({state_abbr}): Found in city_data_by_name with DDD {ddd}")
            cities_found_count += 1
        else:
            print(f"{i+1}. {city_name} ({state_abbr}): NOT FOUND in city_data_by_name!")
            cities_missing_count += 1
    
    if cities_missing_count == 0:
        print("\nRESULT: All cities from get_state_and_city() exist in city_data_by_name - NOT the issue.")
    else:
        print(f"\nRESULT: {cities_missing_count}/10 cities from get_state_and_city() are missing from city_data_by_name - could be an issue!")
except Exception as e:
    print(f"Error testing hypothesis 4: {e}")

# Hypothesis 5: The city keys in city_data_by_name don't match the city_name values
print("\n\nHYPOTHESIS 5: City dictionary keys don't match city_name values")
print("-" * 80)

try:
    # Check the structure of city_data_by_name and how it's being populated
    sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
    
    # Get a sample of cities from the dictionary
    sample_cities = list(sampler.city_data_by_name.items())[:5]
    
    print("Checking if dictionary keys match city_name values:")
    for city_key, city_data in sample_cities:
        city_name_value = city_data.get('city_name', 'MISSING')
        if city_key == city_name_value:
            print(f"{city_key}: Key MATCHES city_name value")
        else:
            print(f"{city_key}: Key DOES NOT MATCH city_name value '{city_name_value}'")
    
    # Get a few cities using get_state_and_city and verify how the lookup works
    print("\nTesting city lookup with get_state_and_city():")
    for i in range(5):
        _, _, city_name = sampler.get_state_and_city()
        
        # Try to lookup the city two ways
        direct_lookup = city_name in sampler.city_data_by_name
        alternate_lookup = False
        alternate_key = None
        
        # Try to find a key that has this city_name value
        for key, data in sampler.city_data_by_name.items():
            if data.get('city_name') == city_name and key != city_name:
                alternate_lookup = True
                alternate_key = key
                break
        
        print(f"{i+1}. {city_name}: Direct lookup {'SUCCESSFUL' if direct_lookup else 'FAILED'}, " + 
              f"{'Alternate key found: '+alternate_key if alternate_lookup else 'No alternate key found'}")
    
    print("\nRESULT: Check if there are mismatches between city keys and city_name values.")
except Exception as e:
    print(f"Error testing hypothesis 5: {e}")

# Hypothesis 6: generate_phone_number() is not correctly using the provided DDD
print("\n\nHYPOTHESIS 6: generate_phone_number() is not correctly using the provided DDD")
print("-" * 80)

try:
    # Test if generate_phone_number() is correctly using the provided DDD
    sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
    
    # Get several specific DDDs to test
    test_ddds = ['11', '21', '41', '83', '55']
    
    print("Testing if generate_phone_number() correctly uses the provided DDDs:")
    for ddd in test_ddds:
        try:
            phone = generate_phone_number(ddd)
            used_ddd = phone.split('(')[1].split(')')[0].strip()
            
            if used_ddd == ddd:
                print(f"DDD {ddd}: Correctly used in phone number {phone}")
            else:
                print(f"DDD {ddd}: NOT USED! Generated phone number {phone} has DDD {used_ddd}")
        except Exception as e:
            print(f"DDD {ddd}: Error generating phone number - {e}")
    
    # Test with random cities
    print("\nTesting phone generation with random cities:")
    for i in range(5):
        _, _, city_name = sampler.get_state_and_city()
        city_data = sampler.city_data_by_name.get(city_name, {})
        ddd = city_data.get('ddd', 'MISSING')
        
        if ddd != 'MISSING':
            try:
                phone = generate_phone_number(ddd)
                used_ddd = phone.split('(')[1].split(')')[0].strip()
                
                print(f"{i+1}. {city_name}: DDD {ddd}, Generated phone {phone}, Used DDD {used_ddd} - " +
                      f"{'CORRECT' if used_ddd == ddd else 'INCORRECT'}")
            except Exception as e:
                print(f"{i+1}. {city_name}: DDD {ddd}, Error generating phone number - {e}")
        else:
            print(f"{i+1}. {city_name}: DDD {ddd}, Cannot generate phone number")
    
    print("\nRESULT: Check if generate_phone_number() is using the provided DDDs correctly.")
except Exception as e:
    print(f"Error testing hypothesis 6: {e}")

# Hypothesis 7: Different initialization orders produce different results
print("\n\nHYPOTHESIS 7: Different initialization orders produce different results")
print("-" * 80)

try:
    # Test loading in different orders to see if it affects DDD availability
    
    # Approach 1: cities_with_ceps.json first, then update with locations_data.json
    sampler1 = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
    with open('ptbr_sampler/data/locations_data.json', 'r', encoding='utf-8') as f:
        locations_data = json.load(f)
    sampler1.update_cities(locations_data.get('cities', {}))
    
    # Approach 2: locations_data.json first, then update with cities_with_ceps.json
    sampler2 = BrazilianLocationSampler('ptbr_sampler/data/locations_data.json')
    with open('ptbr_sampler/data/cities_with_ceps.json', 'r', encoding='utf-8') as f:
        ceps_data = json.load(f)
    sampler2.update_cities(ceps_data.get('cities', {}))
    
    test_cities = ['São Paulo', 'Curitiba', 'Niterói', 'Cruz Alta', 'Isaías Coelho']
    
    print("Testing whether load order affects DDD availability:")
    for city in test_cities:
        ddd1 = sampler1.city_data_by_name.get(city, {}).get('ddd', 'MISSING')
        ddd2 = sampler2.city_data_by_name.get(city, {}).get('ddd', 'MISSING')
        
        print(f"{city}: " +
              f"Approach 1 (ceps→locations) DDD: {ddd1}, " +
              f"Approach 2 (locations→ceps) DDD: {ddd2} - " +
              f"{'MATCH' if ddd1 == ddd2 else 'DIFFER'}")
    
    print("\nRESULT: Check if initialization order affects DDD availability.")
except Exception as e:
    print(f"Error testing hypothesis 7: {e}")

# Hypothesis 8: The city keys are formatted differently in different files
print("\n\nHYPOTHESIS 8: City keys have different formats in different files")
print("-" * 80)

try:
    # Check if the city keys are formatted differently in different files
    with open('ptbr_sampler/data/cities_with_ceps.json', 'r', encoding='utf-8') as f:
        ceps_data = json.load(f)
    
    with open('ptbr_sampler/data/locations_data.json', 'r', encoding='utf-8') as f:
        locations_data = json.load(f)
    
    # Get some sample keys from each file
    ceps_keys = list(ceps_data.get('cities', {}).keys())[:5]
    locations_keys = list(locations_data.get('cities', {}).keys())[:5]
    
    print("Sample keys from cities_with_ceps.json:")
    for key in ceps_keys:
        city_name = ceps_data['cities'][key].get('city_name', 'MISSING')
        print(f"Key: '{key}', city_name: '{city_name}'")
    
    print("\nSample keys from locations_data.json:")
    for key in locations_keys:
        city_name = locations_data['cities'][key].get('city_name', 'MISSING')
        print(f"Key: '{key}', city_name: '{city_name}'")
    
    # Check if the formatting pattern is consistent
    print("\nChecking key format patterns:")
    ceps_key_pattern = "Contains '_' and state code" if any('_' in key for key in ceps_keys) else "No '_' or state code"
    locations_key_pattern = "Contains '_' and state code" if any('_' in key for key in locations_keys) else "No '_' or state code"
    
    print(f"cities_with_ceps.json key pattern: {ceps_key_pattern}")
    print(f"locations_data.json key pattern: {locations_key_pattern}")
    
    print("\nRESULT: Check if key format differences could cause lookup issues.")
except Exception as e:
    print(f"Error testing hypothesis 8: {e}")

# Hypothesis 9: The update_cities method is not correctly merging DDD data
print("\n\nHYPOTHESIS 9: update_cities method loses DDD data during merge")
print("-" * 80)

try:
    # Test if the update_cities method preserves DDDs
    sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
    
    # Create test data with specific cities and DDDs
    test_cities = {}
    for i, city_name in enumerate(['São Paulo', 'Curitiba', 'Niterói', 'Cruz Alta', 'Isaías Coelho']):
        if city_name in sampler.city_data_by_name:
            original_data = sampler.city_data_by_name[city_name].copy()
            original_ddd = original_data.get('ddd', 'MISSING')
            
            # Modify some data but remove the DDD to see if it gets preserved
            modified_data = original_data.copy()
            modified_data['population_percentage_total'] = 0.123456789
            if 'ddd' in modified_data:
                del modified_data['ddd']
            
            test_cities[city_name] = modified_data
            
            print(f"{city_name}: Original DDD: {original_ddd}, DDD in test data: {'REMOVED'}")
    
    # Check DDDs before update
    print("\nDDDs before update:")
    for city_name in test_cities.keys():
        ddd = sampler.city_data_by_name.get(city_name, {}).get('ddd', 'MISSING')
        print(f"{city_name}: DDD {ddd}")
    
    # Update with test data
    print("\nUpdating with test data (without DDDs)...")
    sampler.update_cities(test_cities)
    
    # Check DDDs after update
    print("\nDDDs after update:")
    for city_name in test_cities.keys():
        ddd = sampler.city_data_by_name.get(city_name, {}).get('ddd', 'MISSING')
        print(f"{city_name}: DDD {ddd}")
    
    print("\nRESULT: Check if DDDs are lost during updates.")
except Exception as e:
    print(f"Error testing hypothesis 9: {e}")

# Hypothesis 10: The get_state_and_city() method is selecting cities without DDDs
print("\n\nHYPOTHESIS 10: get_state_and_city() is preferentially selecting cities without DDDs")
print("-" * 80)

try:
    # Test if get_state_and_city() tends to select cities without DDDs
    sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
    
    cities_selected = 100
    cities_with_ddd_count = 0
    city_appearances = {}
    
    print(f"Selecting {cities_selected} random cities and checking DDD availability:")
    for i in range(cities_selected):
        _, _, city_name = sampler.get_state_and_city()
        
        # Track how often each city appears
        if city_name not in city_appearances:
            city_appearances[city_name] = 0
        city_appearances[city_name] += 1
        
        # Check if the city has a DDD
        ddd = sampler.city_data_by_name.get(city_name, {}).get('ddd')
        if ddd:
            cities_with_ddd_count += 1
    
    print(f"Cities with DDDs: {cities_with_ddd_count}/{cities_selected} ({(cities_with_ddd_count/cities_selected)*100:.1f}%)")
    
    # Check most frequently selected cities
    sorted_cities = sorted(city_appearances.items(), key=lambda x: x[1], reverse=True)
    print("\nTop 10 most frequently selected cities:")
    for i, (city_name, count) in enumerate(sorted_cities[:10]):
        ddd = sampler.city_data_by_name.get(city_name, {}).get('ddd', 'MISSING')
        print(f"{i+1}. {city_name}: Selected {count} times, DDD: {ddd}")
    
    print("\nRESULT: Check if there's a pattern in city selection that might affect DDD availability.")
except Exception as e:
    print(f"Error testing hypothesis 10: {e}")

print("\n" + "=" * 80)
print("DEBUGGING COMPLETE")
print("=" * 80)
print("\nReview the results to identify the most likely causes of DDD issues.") 