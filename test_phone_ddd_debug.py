#!/usr/bin/env python3
"""Debug script to trace phone DDD generation and city assignment."""

import sys
import json
from pathlib import Path
from loguru import logger

# Configure logger for detailed output
logger.remove()
logger.add(sys.stderr, level="DEBUG")

try:
    from ptbr_sampler.br_location_class import BrazilianLocationSampler
    from ptbr_sampler.utils.phone import generate_phone_number
    from ptbr_sampler.br_name_class import TimePeriod
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

def debug_phone_generation():
    """Debug the phone number generation process to understand DDD mismatch issues."""
    logger.info("=" * 80)
    logger.info("DEBUGGING PHONE DDD GENERATION")
    logger.info("=" * 80)
    
    # Initialize location sampler
    logger.info("Initializing location sampler...")
    city_data_path = Path("ptbr_sampler/data/cities_with_ceps.json")
    if not city_data_path.exists():
        logger.error(f"Cities data file not found: {city_data_path}")
        sys.exit(1)
    
    location_sampler = BrazilianLocationSampler(str(city_data_path))
    
    # Generate 5 random cities and check their DDDs
    logger.info("\nGenerating 5 random cities and checking their DDDs:")
    
    for i in range(5):
        # Get a random city
        state_name, state_abbr, city_name = location_sampler.get_state_and_city()
        logger.info(f"Random City {i+1}: {city_name}, {state_abbr}")
        
        # Get city data using the new method
        city_data = location_sampler.get_city_data_by_name(city_name, state_abbr)
        if not city_data:
            logger.error(f"  ❌ Failed to retrieve city data for {city_name}, {state_abbr}")
            continue
        
        # Check if DDD is present
        ddd = city_data.get('ddd')
        if not ddd:
            logger.error(f"  ❌ No DDD found for {city_name}, {state_abbr}")
            continue
            
        logger.info(f"  ✅ DDD for {city_name}, {state_abbr}: {ddd}")
        
        # Generate a phone number with this DDD
        try:
            phone = generate_phone_number(ddd)
            logger.info(f"  ✅ Generated phone: {phone}")
            
            # Verify the phone has the correct DDD
            phone_ddd = phone[1:phone.index(')')]
            if phone_ddd == ddd:
                logger.info(f"  ✅ Phone DDD matches: {phone_ddd} == {ddd}")
            else:
                logger.error(f"  ❌ Phone DDD mismatch: {phone_ddd} != {ddd}")
        except Exception as e:
            logger.error(f"  ❌ Error generating phone: {e}")
    
    # Test the original problematic scenario
    logger.info("\nTesting city-phone assignment in sampler.py:")
    
    # List a few cities with their expected DDDs for verification
    test_cities = [
        ("São Paulo", "SP", "11"),
        ("Rio de Janeiro", "RJ", "21"),
        ("Belo Horizonte", "MG", "31"),
        ("Belém", "PA", "91"),
        ("Recife", "PE", "81")
    ]
    
    for city, state, expected_ddd in test_cities:
        logger.info(f"Testing {city}, {state} (Expected DDD: {expected_ddd})")
        
        # Get city data using the new method
        city_data = location_sampler.get_city_data_by_name(city, state)
        if not city_data:
            logger.error(f"  ❌ Failed to retrieve city data")
            continue
            
        # Check if DDD is present and matches expected
        ddd = city_data.get('ddd')
        if not ddd:
            logger.error(f"  ❌ No DDD found in city data")
            continue
            
        if ddd != expected_ddd:
            logger.error(f"  ❌ DDD in city data ({ddd}) doesn't match expected ({expected_ddd})")
        else:
            logger.info(f"  ✅ DDD in city data matches expected: {ddd}")
            
        # Generate a phone number with this DDD
        try:
            phone = generate_phone_number(ddd)
            logger.info(f"  ✅ Generated phone: {phone}")
            
            # Check if the phone DDD matches
            phone_ddd = phone[1:phone.index(')')]
            if phone_ddd == ddd:
                logger.info(f"  ✅ Phone DDD matches: {phone_ddd} == {ddd}")
            else:
                logger.error(f"  ❌ Phone DDD mismatch: {phone_ddd} != {ddd}")
                
            # Create mock phone metadata that would be stored
            phone_metadata = {'original_city': city, 'ddd': ddd, 'state_abbr': state}
            logger.info(f"  📝 Phone metadata: {phone_metadata}")
        except Exception as e:
            logger.error(f"  ❌ Error generating phone: {e}")
    
    logger.info("\nDebug completed")

if __name__ == "__main__":
    debug_phone_generation() 