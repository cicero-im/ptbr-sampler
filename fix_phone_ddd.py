#!/usr/bin/env python
"""
Comprehensive fix for the DDD mismatch issue with phone numbers.
"""

import sys
import json
from pathlib import Path
from loguru import logger

# Set up logger to show debug output
logger.remove()
logger.add(sys.stderr, level="DEBUG")

print("=" * 80)
print("COMPREHENSIVE DDD MISMATCH FIX")
print("=" * 80)

# Examine the sampler.py file structure
samplerpy_path = Path('ptbr_sampler/sampler.py')
if samplerpy_path.exists():
    print(f"\nFound sampler.py at {samplerpy_path}")
else:
    print(f"\nERROR: Could not find {samplerpy_path}")
    sys.exit(1)

# Import the required modules for testing
print("\nImporting required modules for testing...")
try:
    from ptbr_sampler.br_location_class import BrazilianLocationSampler
    from ptbr_sampler.utils.phone import generate_phone_number
    print("Successfully imported required modules")
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)

print("\nThe issue has multiple potential sources:")
print("1. The API response may return a different city/state than what we originally used for DDD")
print("2. When multiple random cities are generated, there could be inconsistencies")
print("3. The 'parse_result' function overwrites the original city with API data")

print("\nComprehensive solution overview:")
print("1. Store the DDD alongside the phone number in a structured format")
print("2. Modify the 'parse_result' function to prioritize state_info over API data")
print("3. Ensure the phone generation only happens with valid DDDs")

print("\nDo you want to apply the comprehensive fix? (yes/no)")
answer = input("Enter your choice: ")

if answer.lower() in ('yes', 'y'):
    # Create a backup 
    backup_path = samplerpy_path.with_suffix('.py.bak2')
    print(f"\nCreating backup of sampler.py at {backup_path}")
    
    with samplerpy_path.open('r', encoding='utf-8') as original:
        with backup_path.open('w', encoding='utf-8') as backup:
            backup.write(original.read())
    
    # Read the file content
    with samplerpy_path.open('r', encoding='utf-8') as f:
        sampler_content = f.read()
    
    # 1. Update the phone number generation to include DDD info
    
    # Find the pattern for phone number generation
    phone_gen_pattern = "documents['phone'] = generate_phone_number(ddd)"
    enhanced_phone_gen = "documents['phone'] = generate_phone_number(ddd)\n                    # Store the original city and DDD used for the phone number\n                    documents['_phone_metadata'] = {'original_city': city_name, 'ddd': ddd}"
    
    sampler_content = sampler_content.replace(phone_gen_pattern, enhanced_phone_gen)
    
    # 2. Update the parse_result function to use the metadata
    
    # Find the parse_result function
    start_marker = "# Original parse_result function was replaced to fix DDD mismatch issues"
    if start_marker not in sampler_content:
        start_marker = "def parse_result("
    
    start_idx = sampler_content.find(start_marker)
    if start_idx == -1:
        print("ERROR: Could not find parse_result function in sampler.py")
        sys.exit(1)
    
    end_marker = "    return result"
    end_idx = sampler_content.find(end_marker, start_idx)
    if end_idx == -1:
        print("ERROR: Could not find end of parse_result function in sampler.py")
        sys.exit(1)
    
    # Get the end of the function (including return statement)
    end_idx = sampler_content.find("\n", end_idx) + 1
    
    # Extract sections before and after the function
    before = sampler_content[:start_idx]
    after = sampler_content[end_idx:]
    
    # Create modified function with enhanced phone metadata handling
    modified_function = """# Enhanced parse_result function with DDD consistency improvements
def parse_result(
    location: str,
    name_components: NameComponents,
    documents: dict[str, str],
    state_info: tuple[str, str, str] | None = None,
    address_data: dict | None = None,
) -> dict:
    \"\"\"Parse sample results into a standardized dictionary format.

    Args:
        location: Full location string
        name_components: Named tuple with name components
        documents: Dictionary of document numbers
        state_info: Optional tuple of (state_name, state_abbr, city_name)
        address_data: Optional dictionary with address data (street, neighborhood, building_number)

    Returns:
        dict: Structured dictionary with parsed components
    \"\"\"
    # Debug the documents dictionary to see if phone is present
    has_phone = 'phone' in documents
    phone_value = documents.get('phone', '')
    logger.debug(f"parse_result: documents contains phone? {has_phone}, value: {phone_value}")
    
    # Check if we have phone metadata
    has_phone_metadata = '_phone_metadata' in documents
    if has_phone and has_phone_metadata:
        phone_meta = documents.get('_phone_metadata', {})
        logger.debug(f"Phone was generated for city: {phone_meta.get('original_city', 'unknown')} with DDD: {phone_meta.get('ddd', 'unknown')}")
    
    result = {
        'name': name_components.first_name if name_components else '',
        'middle_name': name_components.middle_name if name_components else '',
        'surnames': name_components.surname if name_components else '',
        'city': '',
        'state': '',
        'state_abbr': '',
        'cep': '',
        'street': '',
        'neighborhood': '',
        'building_number': '',
        'cpf': documents.get('cpf', ''),
        'rg': documents.get('rg', ''),
        'pis': documents.get('pis', ''),
        'cnpj': documents.get('cnpj', ''),
        'cei': documents.get('cei', ''),
        'phone': documents.get('phone', ''),  # Ensure phone is included
    }

    # Important: If we have phone_metadata, use that city for consistency with the phone DDD
    if has_phone and has_phone_metadata and documents.get('_phone_metadata', {}).get('original_city'):
        # Prioritize phone metadata if available and we need to set the city
        if state_info:
            # Keep the original state information but use the city from phone metadata
            # to ensure the phone DDD matches the city
            state_name, state_abbr, _ = state_info
            city_name = documents.get('_phone_metadata', {}).get('original_city')
            result['state'], result['state_abbr'], result['city'] = state_name, state_abbr, city_name
            logger.debug(f"Using city from phone metadata: {city_name} (to match DDD)")
        else:
            # If no state_info, still try to use the city from phone metadata
            result['city'] = documents.get('_phone_metadata', {}).get('original_city')
            logger.debug(f"Using city from phone metadata without state info: {result['city']}")
    elif state_info:
        # Second priority: use state_info if no phone metadata
        result['state'], result['state_abbr'], result['city'] = state_info
        logger.debug(f"Using city from state_info: {result['city']}")
    elif location and ', ' in location:
        # Last priority: parse location string if available
        try:
            city_part, state_part = location.split(', ')
            if ' - ' in city_part:
                result['city'], cep = city_part.split(' - ')
                result['cep'] = cep
            else:
                result['city'] = city_part

            if '(' in state_part:
                result['state'], abbr = state_part.split(' (')
                result['state_abbr'] = abbr.rstrip(')')
            else:
                result['state'] = state_part
                
            logger.debug(f"Using city from location string: {result['city']}")
        except ValueError:
            pass

    # Add address data if available, but NEVER override city/state that was used for DDD
    if address_data:
        result['street'] = address_data.get('street', '')
        result['neighborhood'] = address_data.get('neighborhood', '')
        result['building_number'] = address_data.get('building_number', '')
        
        # Only set CEP from address_data if it's not already set
        if not result['cep'] and address_data.get('cep'):
            result['cep'] = address_data.get('cep', '')
            
    # Log the final result structure
    logger.debug(f"parse_result: final result city: {result['city']}, phone: {result.get('phone', '')}")
    
    return result
"""
    
    # Combine all parts
    modified_content = before + modified_function + after
    
    # Write the modified file
    with samplerpy_path.open('w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"\nEnhanced fix applied to {samplerpy_path}")
    print(f"Original file backed up at {backup_path}")
    
    print("\nTo test the fix, run:")
    print("  python test_easy_ddd.py")
else:
    print("\nFix not applied.")

print("\n" + "=" * 80)
print("FIX PROCESS COMPLETE")
print("=" * 80) 