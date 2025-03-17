#!/usr/bin/env python
"""
Debug script to trace the exact flow of city, DDD, and phone number generation.
"""

import sys
import json
import asyncio
from pathlib import Path
from loguru import logger
import os

# Add path resolution logic to ensure we can find the correct file paths
current_dir = Path(__file__).parent
os.chdir(current_dir)  # Set working directory to script location

# Import sampler module with correct paths
from ptbr_sampler.sampler import sample
from ptbr_sampler.br_location_class import BrazilianLocationSampler
from ptbr_sampler.utils.phone import generate_phone_number

# Configure logger
logger.remove()
logger.add(sys.stderr, level="DEBUG")

# Define paths relative to script location
CITIES_PATH = current_dir / "ptbr_sampler" / "data" / "cities_with_ceps.json"

async def test_direct_flow():
    """Test the direct flow of city, DDD, and phone generation."""
    print("=" * 80)
    print("DEBUGGING PHONE NUMBER GENERATION FLOW")
    print("=" * 80)
    
    print("\n1. TRACING FUNCTION CALLS FOR CITY/DDD/PHONE GENERATION")
    print("-" * 80)
    
    # Initialize location sampler
    location_sampler = BrazilianLocationSampler(str(CITIES_PATH))
    
    # Generate 5 samples of city and state
    for i in range(5):
        # Get state and city
        state, state_abbr, city = location_sampler.get_state_and_city()
        
        # Get city data directly from the location sampler's cache
        city_data = location_sampler.city_data_by_name.get(city, None)
        
        print(f"\nSample {i+1}:")
        print(f"  Generated city: {city}, {state} ({state_abbr})")
        print(f"  City data available: {city_data is not None}")
        if city_data:
            print(f"  City data: {city_data}")
            
            # Get DDD from city data
            ddd = city_data.get('ddd')
            print(f"  Retrieved DDD: {ddd}")
            
            # Generate phone number if DDD is available
            if ddd:
                phone = generate_phone_number(ddd)
                print(f"  Generated phone: {phone}")
            else:
                print(f"  ERROR: No DDD found for {city}, {state}")
        else:
            print(f"  ERROR: No city data found for {city}")
            
    print("\n2. TESTING THE SAMPLE FUNCTION WITH DEBUG")
    print("-" * 80)
    
    # Test with fixed parameters to isolate DDD issues
    try:
        results = sample(
            qty=3,
            make_api_call=True,
            all_data=True,
            always_phone=True,
            save_to_jsonl="phone_generation_debug.jsonl"
        )
        
        print("\nResults from sample function:")
        for i, result in enumerate(results):
            print(f"Sample {i+1}:")
            print(f"  Name: {result.get('name')}")
            print(f"  City: {result.get('city')}")
            print(f"  State: {result.get('state')}")
            print(f"  Phone: {result.get('phone')}")
            print()
            
        # Analyze saved results
        with open("phone_generation_debug.jsonl", 'r', encoding='utf-8') as f:
            saved_results = [json.loads(line) for line in f]
            
        print("\nSaved results analysis:")
        for i, result in enumerate(saved_results):
            print(f"Saved Sample {i+1}:")
            print(f"  Name: {result.get('name')}")
            print(f"  City: {result.get('city')}")
            print(f"  State: {result.get('state')}")
            print(f"  Phone: {result.get('phone')}")
            
            # If we have phone number and city, check DDD match
            phone = result.get('phone', '')
            city = result.get('city', '')
            
            if phone and city and '(' in phone and ')' in phone:
                # Extract DDD from phone
                phone_ddd = phone.split('(')[1].split(')')[0].strip()
                
                # Get expected DDD
                city_data = location_sampler.city_data_by_name.get(city)
                expected_ddd = city_data.get('ddd') if city_data else None
                
                print(f"  Phone DDD: {phone_ddd}")
                print(f"  Expected DDD: {expected_ddd}")
                
                if expected_ddd and phone_ddd == expected_ddd:
                    print("  ✅ DDD matches expected value")
                elif expected_ddd:
                    print(f"  ❌ DDD mismatch: {phone_ddd} != {expected_ddd}")
                else:
                    print(f"  ⚠️ No expected DDD found for {city}")
            print()
    except Exception as e:
        print(f"Error during sample function test: {e}")

if __name__ == "__main__":
    asyncio.run(test_direct_flow()) 