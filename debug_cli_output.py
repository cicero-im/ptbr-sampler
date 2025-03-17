#!/usr/bin/env python
"""
Debug script to identify where DDDs get lost in the CLI output process.
This script traces the full path from city data to final output.
"""

import json
import sys
from pathlib import Path

from loguru import logger
from ptbr_sampler.br_location_class import BrazilianLocationSampler
from ptbr_sampler.sampler import sample
from ptbr_sampler.utils.phone import generate_phone_number

# Set up logger with more detailed formatting
logger.remove()
logger.add(sys.stderr, level="DEBUG", format="{time} | {level} | {module}:{function}:{line} | {message}")

print("=" * 80)
print("DEBUGGING DDD TRANSMISSION IN CLI OUTPUT")
print("=" * 80)

# 1. Test direct DDD retrieval and phone generation
print("\n1. DIRECT RETRIEVAL OF DDDs AND PHONE GENERATION")
print("-" * 80)

sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')

# List of cities to test (with expected DDDs)
test_cities = {
    'São Paulo': '11',
    'Rio de Janeiro': '21',
    'Niterói': '21',
    'Curitiba': '41',
    'Porto Alegre': '51',
    'Salvador': '71',
    'Brasília': '61'
}

print("Testing direct DDD retrieval and phone generation:")
for city_name, expected_ddd in test_cities.items():
    # Get the DDD from city data
    city_data = sampler.city_data_by_name.get(city_name, {})
    ddd = city_data.get('ddd', 'MISSING')
    
    # Generate a phone number with this DDD
    if ddd != 'MISSING':
        phone = generate_phone_number(ddd)
        print(f"{city_name}: DDD in data = {ddd}, Expected = {expected_ddd}, Phone = {phone}")
    else:
        print(f"{city_name}: No DDD found in city data")

# 2. Create a test output file to verify JSONL saving
print("\n2. TESTING OUTPUT TO JSONL FILE")
print("-" * 80)

output_file = "debug_output.jsonl"
print(f"Generating a sample and saving to {output_file}...")

# Run the sample function with the --save-to-jsonl parameter
results = sample(
    qty=5,
    q=None,
    city_only=False,
    state_abbr_only=False,
    state_full_only=False,
    only_cep=False,
    cep_without_dash=False,
    make_api_call=False,
    time_period="any",
    return_only_name=False,
    name_raw=False,
    json_path="ptbr_sampler/data/cities_with_ceps.json",
    names_path="ptbr_sampler/data/names.json",
    middle_names_path="ptbr_sampler/data/middle_names.json",
    only_surname=False,
    top_40=False,
    with_only_one_surname=False,
    always_middle=False,
    only_middle=False,
    always_cpf=False,
    always_pis=False,
    always_cnpj=False,
    always_cei=False,
    always_rg=False,
    always_phone=True,
    only_cpf=False,
    only_pis=False,
    only_cnpj=False,
    only_cei=False,
    only_rg=False,
    only_fone=False,
    include_issuer=False,
    only_document=False,
    surnames_path="ptbr_sampler/data/surnames.json",
    locations_path="ptbr_sampler/data/locations_data.json",
    save_to_jsonl=output_file,
    all_data=True,
    progress_callback=None,
    append_to_jsonl=False,
)

# 3. Inspect what's saved vs what's returned
print("\n3. COMPARING RETURNED RESULTS VS SAVED JSONL")
print("-" * 80)

# Read the saved JSONL file
print(f"Reading saved JSONL file {output_file}...")
saved_results = []
try:
    with open(output_file, 'r', encoding='utf-8') as f:
        for line in f:
            saved_results.append(json.loads(line))
    
    print(f"Successfully loaded {len(saved_results)} results from JSONL file")
except Exception as e:
    print(f"Error reading JSONL file: {e}")

# Compare the results (returned vs saved)
print("\nComparing phone numbers in returned results vs saved JSONL:")
for i, (returned, saved) in enumerate(zip(results, saved_results)):
    returned_name = returned.get('name', 'No name')
    returned_city = returned.get('city', 'No city')
    returned_phone = returned.get('phone', 'No phone')
    returned_ddd = "None" if returned_phone == "No phone" else returned_phone.split('(')[1].split(')')[0].strip()
    
    saved_name = saved.get('name', 'No name')
    saved_city = saved.get('city', 'No city')
    saved_phone = saved.get('phone', 'No phone')
    saved_ddd = "None" if saved_phone == "No phone" else saved_phone.split('(')[1].split(')')[0].strip()
    
    print(f"\nSample {i+1}:")
    print(f"  Returned: {returned_name} - {returned_city} - Phone: {returned_phone} (DDD: {returned_ddd})")
    print(f"  Saved:    {saved_name} - {saved_city} - Phone: {saved_phone} (DDD: {saved_ddd})")
    
    if returned_phone != saved_phone:
        print(f"  *** MISMATCH: Phone numbers differ! ***")

# 4. Check the CLI execution path
print("\n4. TRACING THE CLI EXECUTION PATH")
print("-" * 80)

print("To further debug, modify run_cli.py to add additional logging at key points:")
print("1. When city data is retrieved")
print("2. When DDD is extracted from city data")
print("3. When phone number is generated")
print("4. Before writing output to JSONL")
print("5. Use --debug flag to enable this enhanced logging")

print("\n" + "=" * 80)
print("DEBUGGING COMPLETE")
print("=" * 80) 