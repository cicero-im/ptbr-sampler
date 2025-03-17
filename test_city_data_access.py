#!/usr/bin/env python
"""Test script to examine how city_data_by_name is populated and accessed."""

import sys
import json
from pathlib import Path
from loguru import logger

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg), level="DEBUG")

try:
    from ptbr_sampler.br_location_class import BrazilianLocationSampler
    from ptbr_sampler.utils.phone import generate_phone_number
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

def test_city_data_access():
    """Test how city_data_by_name is populated and accessed."""
    logger.info("=" * 80)
    logger.info("TESTING CITY DATA ACCESS")
    logger.info("=" * 80)
    
    # Initialize sampler with proper paths
    cities_path = Path("ptbr_sampler/data/cities_with_ceps.json")
    if not cities_path.exists():
        logger.error(f"Cities data file not found: {cities_path}")
        sys.exit(1)
        
    logger.info(f"Loading city data from: {cities_path}")
    sampler = BrazilianLocationSampler(str(cities_path))
    
    # Check basic stats about the city_data_by_name dictionary
    total_cities = len(sampler.city_data_by_name)
    logger.info(f"Total cities in city_data_by_name: {total_cities}")
    
    cities_with_ddd = sum(1 for city_data in sampler.city_data_by_name.values() if 'ddd' in city_data)
    logger.info(f"Cities with DDD in city_data_by_name: {cities_with_ddd} ({cities_with_ddd/total_cities:.2%})")
    
    # Sample city key examination
    sample_city_keys = list(sampler.city_data_by_name.keys())[:10]
    logger.info(f"Sample city keys: {sample_city_keys}")
    
    # Test some known cities
    test_cities = ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Curitiba"]
    logger.info("\nTesting access for known major cities:")
    
    for city in test_cities:
        if city in sampler.city_data_by_name:
            city_data = sampler.city_data_by_name[city]
            ddd = city_data.get('ddd', 'NO DDD')
            logger.info(f"✅ {city}: Found - DDD = {ddd}")
        else:
            logger.error(f"❌ {city}: Not found in city_data_by_name")
            
            # Try to find similar keys
            similar_keys = [k for k in sampler.city_data_by_name.keys() if city.lower() in k.lower()]
            if similar_keys:
                logger.info(f"   Similar keys: {similar_keys}")
    
    # Test the full city generation flow
    logger.info("\nTesting city generation flow:")
    
    for i in range(5):
        # Generate a city
        state_name, state_abbr, city_name = sampler.get_state_and_city()
        logger.info(f"Generated: {city_name}, {state_name} ({state_abbr})")
        
        # Check if we can access the city data
        if city_name in sampler.city_data_by_name:
            city_data = sampler.city_data_by_name[city_name]
            ddd = city_data.get('ddd', 'NO DDD')
            logger.info(f"  City data access: Success - DDD = {ddd}")
            
            # Generate a phone number if DDD is available
            if ddd != 'NO DDD':
                try:
                    phone = generate_phone_number(ddd)
                    logger.info(f"  Generated phone: {phone}")
                except Exception as e:
                    logger.error(f"  Phone generation error: {e}")
        else:
            logger.error(f"  City data access: Failed - '{city_name}' not found in city_data_by_name")
            
            # Check if there's a similar key
            similar_keys = [k for k in sampler.city_data_by_name.keys() if city_name.lower() in k.lower() or k.lower() in city_name.lower()]
            if similar_keys:
                logger.info(f"  Similar keys: {similar_keys}")
                
                # Check the first similar key
                first_similar = similar_keys[0]
                similar_data = sampler.city_data_by_name[first_similar]
                similar_ddd = similar_data.get('ddd', 'NO DDD')
                logger.info(f"  Similar city '{first_similar}' has DDD = {similar_ddd}")
    
    # Test a specific problematic case from previous tests
    problem_cases = [
        ("Sarandi", "11", "54"),
        ("Brasília", "84", "61"),
        ("Jandira", "14", "11")
    ]
    
    logger.info("\nTesting problem cases:")
    
    for city, wrong_ddd, correct_ddd in problem_cases:
        logger.info(f"Problem case: {city} (wrong DDD {wrong_ddd}, should be {correct_ddd})")
        
        if city in sampler.city_data_by_name:
            city_data = sampler.city_data_by_name[city]
            actual_ddd = city_data.get('ddd', 'NO DDD')
            logger.info(f"  City data access: Success - DDD = {actual_ddd}")
            
            if actual_ddd == correct_ddd:
                logger.info(f"  ✅ City data has correct DDD: {actual_ddd}")
            else:
                logger.error(f"  ❌ City data has incorrect DDD: {actual_ddd} (should be {correct_ddd})")
        else:
            logger.error(f"  ❌ City '{city}' not found in city_data_by_name")
            
            # Look for similar keys
            similar_keys = [k for k in sampler.city_data_by_name.keys() if city.lower() in k.lower() or k.lower() in city.lower()]
            if similar_keys:
                logger.info(f"  Similar keys: {similar_keys}")
                
                # Check all similar keys for the correct DDD
                for similar in similar_keys:
                    similar_data = sampler.city_data_by_name[similar]
                    similar_ddd = similar_data.get('ddd', 'NO DDD')
                    logger.info(f"  Similar city '{similar}' has DDD = {similar_ddd}")
    
    logger.info("\nTest completed.")

if __name__ == "__main__":
    test_city_data_access() 