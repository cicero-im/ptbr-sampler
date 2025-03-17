#!/usr/bin/env python
"""
Analysis and fix for the DDD mismatch issue with --easy flag.
"""

import sys
import json
from pathlib import Path
from loguru import logger

# Set up logger to show debug output
logger.remove()
logger.add(sys.stderr, level="DEBUG")

print("=" * 80)
print("DDD MISMATCH ANALYSIS AND FIX")
print("=" * 80)

"""
ISSUE ANALYSIS:

The issue with phone DDDs being incorrect in the output JSON files when using 
the --easy flag (which sets all_data=True and make_api_call=True) appears to be
related to the API response overriding the city/state information that was used 
to generate the phone numbers.

Here's what happens:

1. In the all_data=True path (sampler.py ~line 730-850):
   - We first generate the correct state-city combinations 
   - We store these in all_state_city_info
   - Phone numbers are properly generated using the city's DDD

2. But then, when make_api_call=True:
   - API responses (all_address_data) may return DIFFERENT city and state info
   - In the parse_result function (~line 16-102), the API's address_data is used 
     to override the city/state data with address_data.get('city') and address_data.get('state')
   - This happens AFTER the phone number was already generated with the original city DDD

3. Result:
   - The final JSON has phone numbers with the correct DDD for the ORIGINAL city
   - But the city name in the output is from the API response
   - This creates a mismatch between city and phone DDD

The fix is to ensure that when we generate a phone number for a city, that phone 
number stays associated with that same city, even if the API returns different 
city information.
"""

print("\nPerforming analysis of current code...")

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

# Load the sampler.py content
with samplerpy_path.open('r', encoding='utf-8') as f:
    sampler_content = f.read()

# Check if the parse_result function uses API data to overwrite city/state
if "# If we have city/state from address_data, use it (API mode)" in sampler_content:
    print("\nFound issue in parse_result function:")
    print("  - When API data is available, it overwrites the city/state info")
    print("  - This happens AFTER the phone number was generated with the original city's DDD")
    print("  - This causes a mismatch between the city in the output and the phone DDD")
else:
    print("\nCould not find the exact issue pattern in sampler.py")

print("\nCreating fix for the issue...")
print("The fix involves modifying the parse_result function to:")
print("  1. Always prioritize the state_info tuple (which was used to generate the phone DDDs)")
print("  2. Never overwrite city/state info with API data")
print("  3. Only use API data for additional address details (street, neighborhood, etc.)")

# Propose the fix by creating a backup and writing a modified file
backup_path = samplerpy_path.with_suffix('.py.bak')
print(f"\nCreating backup of sampler.py at {backup_path}")

# Ask the user if they want to apply the fix
print("\nDo you want to apply the fix to sampler.py? (yes/no)")
answer = input("Enter your choice: ")

if answer.lower() in ('yes', 'y'):
    # Create a backup 
    with samplerpy_path.open('r', encoding='utf-8') as original:
        with backup_path.open('w', encoding='utf-8') as backup:
            backup.write(original.read())
    
    # Find the parse_result function
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
    
    # Create modified function
    modified_function = """# Original parse_result function was replaced to fix DDD mismatch issues
# This version never overwrites city/state with API data
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

    # Always prioritize state_info as it was used to generate the DDD for the phone number
    if state_info:
        result['state'], result['state_abbr'], result['city'] = state_info
    elif location and ', ' in location:
        # Parse location string if available
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
    logger.debug(f"parse_result: final result has phone? {'phone' in result}, value: {result.get('phone', '')}")
    
    return result
"""
    
    # Combine all parts
    modified_content = before + modified_function + after
    
    # Write the modified file
    with samplerpy_path.open('w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"\nFix applied to {samplerpy_path}")
    print(f"Original file backed up at {backup_path}")
    
    print("\nTo test the fix, run:")
    print("  python test_easy_ddd.py")
else:
    print("\nFix not applied. You can apply it manually by modifying the parse_result function to:")
    print("  1. Remove the lines that overwrite city/state with API data")
    print("  2. Keep the code that uses address_data for street, neighborhood, etc.")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80) 