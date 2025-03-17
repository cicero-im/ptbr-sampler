#!/usr/bin/env python3
"""Debug script to trace DDD issues in parse_result function."""

import sys
import json
import tempfile
from pathlib import Path
from loguru import logger

# Configure logger for detailed output
logger.remove()
logger.add(sys.stderr, level="DEBUG")

try:
    from ptbr_sampler.sampler import sample, parse_result
    from ptbr_sampler.br_location_class import BrazilianLocationSampler
    from ptbr_sampler.br_name_class import TimePeriod, NameComponents
    from ptbr_sampler.utils.phone import generate_phone_number
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

def debug_parse_result():
    """Debug the parse_result function to see if it's maintaining city-DDD consistency."""
    logger.info("=" * 80)
    logger.info("DEBUGGING PARSE_RESULT FUNCTION")
    logger.info("=" * 80)
    
    # Test the parse_result function directly with controlled inputs
    logger.info("\nTesting parse_result with controlled inputs:")
    
    # Initialize location sampler
    city_data_path = Path("ptbr_sampler/data/cities_with_ceps.json")
    location_sampler = BrazilianLocationSampler(str(city_data_path))
    
    # Test with a few major cities
    test_cities = [
        ("São Paulo", "SP", "11"),
        ("Rio de Janeiro", "RJ", "21"),
        ("Belo Horizonte", "MG", "31")
    ]
    
    for city_name, state_abbr, expected_ddd in test_cities:
        # Build mock inputs for parse_result
        logger.info(f"\nTesting parse_result with {city_name}, {state_abbr} (Expected DDD: {expected_ddd})")
        
        # Create a fake location string
        location_str = f"{city_name} - 00000-000, São Paulo (SP)"
        
        # Create fake name components
        name_components = NameComponents(first_name="Test", middle_name=None, surname="User")
        
        # Use real city data to get the DDD
        city_data = location_sampler.get_city_data_by_name(city_name, state_abbr)
        if not city_data:
            logger.error(f"  ❌ City data not found for {city_name}, {state_abbr}")
            continue
        
        ddd = city_data.get('ddd')
        if not ddd:
            logger.error(f"  ❌ No DDD found for {city_name}, {state_abbr}")
            continue
        
        # Generate a real phone with the right DDD
        phone = generate_phone_number(ddd)
        logger.info(f"  ✅ Generated phone with DDD {ddd}: {phone}")
        
        # Create documents dictionary with phone and metadata
        documents = {
            'phone': phone,
            '_phone_metadata': {
                'original_city': city_name,
                'ddd': ddd,
                'state_abbr': state_abbr
            }
        }
        
        # Set up state_info to override the location string
        state_info = ("São Paulo", "SP", city_name)
        
        # Call parse_result
        logger.info("  📝 Calling parse_result with these inputs...")
        result = parse_result(
            location=location_str,
            name_components=name_components,
            documents=documents,
            state_info=state_info,
            address_data=None
        )
        
        # Check what we got
        logger.info(f"  📋 parse_result output:")
        logger.info(f"    - City: {result.get('city', 'N/A')}")
        logger.info(f"    - State: {result.get('state', 'N/A')} ({result.get('state_abbr', 'N/A')})")
        logger.info(f"    - Phone: {result.get('phone', 'N/A')}")
        
        # Verify the DDD in the phone matches what we expect
        phone_from_result = result.get('phone', '')
        if phone_from_result and '(' in phone_from_result and ')' in phone_from_result:
            phone_ddd = phone_from_result[1:phone_from_result.index(')')]
            if phone_ddd == ddd:
                logger.info(f"  ✅ Phone DDD in result matches expected: {phone_ddd} == {ddd}")
            else:
                logger.error(f"  ❌ Phone DDD mismatch in result: {phone_ddd} != {ddd}")
        else:
            logger.error(f"  ❌ Invalid phone format in result: {phone_from_result}")
    
    # Now test with a full sample generation to see what happens in the real scenario
    logger.info("\nTesting with full sample generation:")
    
    # Create a temporary output file
    temp_output = tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False, dir='/tmp')
    output_path = temp_output.name
    temp_output.close()
    
    try:
        # Generate a small sample
        sample(
            qty=3,
            q=None,
            city_only=False,
            state_abbr_only=False,
            state_full_only=False,
            only_cep=False,
            cep_without_dash=False,
            make_api_call=False,  # Skip API call to speed up testing
            time_period=TimePeriod.UNTIL_2010,
            return_only_name=False,
            name_raw=False,
            json_path="ptbr_sampler/data/cities_with_ceps.json",
            names_path="ptbr_sampler/data/names_data.json",
            middle_names_path="ptbr_sampler/data/middle_names.json",
            only_surname=False,
            top_40=False,
            with_only_one_surname=False,
            always_middle=True,
            only_middle=False,
            always_cpf=True,
            always_pis=False,
            always_cnpj=False,
            always_cei=False,
            always_rg=True,
            always_phone=True,
            only_cpf=False,
            only_pis=False,
            only_cnpj=False,
            only_cei=False,
            only_rg=False,
            only_fone=False,
            include_issuer=False,
            only_document=False,
            surnames_path="ptbr_sampler/data/surnames_data.json",
            locations_path="ptbr_sampler/data/locations_data.json",
            save_to_jsonl=output_path,
            all_data=True,
            append_to_jsonl=False
        )
        
        # Read the generated samples
        with open(output_path, 'r', encoding='utf-8') as f:
            samples = [json.loads(line) for line in f]
        
        # Check each sample
        for i, sample_data in enumerate(samples):
            city = sample_data.get('city', '')
            state_abbr = sample_data.get('state_abbr', '')
            phone = sample_data.get('phone', '')
            
            logger.info(f"\nSample {i+1}:")
            logger.info(f"  - City: {city}, {state_abbr}")
            logger.info(f"  - Phone: {phone}")
            
            # Extract DDD from phone
            if phone and '(' in phone and ')' in phone:
                phone_ddd = phone[1:phone.index(')')]
                logger.info(f"  - Phone DDD: {phone_ddd}")
                
                # Get expected DDD for this city
                city_data = location_sampler.get_city_data_by_name(city, state_abbr)
                if city_data:
                    expected_ddd = city_data.get('ddd')
                    if expected_ddd:
                        logger.info(f"  - Expected DDD: {expected_ddd}")
                        if phone_ddd == expected_ddd:
                            logger.info(f"  ✅ DDD match: {phone_ddd} == {expected_ddd}")
                        else:
                            logger.error(f"  ❌ DDD mismatch: {phone_ddd} != {expected_ddd}")
                    else:
                        logger.error(f"  ❌ No DDD found in city data")
                else:
                    logger.error(f"  ❌ City data not found for {city}, {state_abbr}")
            else:
                logger.error(f"  ❌ Invalid phone format: {phone}")
        
    except Exception as e:
        logger.error(f"Error generating samples: {e}")
    finally:
        # Clean up
        try:
            Path(output_path).unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Error cleaning up temporary file: {e}")
    
    logger.info("\nDebug completed")

if __name__ == "__main__":
    debug_parse_result() 