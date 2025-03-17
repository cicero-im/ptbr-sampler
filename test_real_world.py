#!/usr/bin/env python
"""Test the real world scenario of the CLI command."""

import json
import subprocess
import os
from pathlib import Path
from loguru import logger
import tempfile

logger.remove()
logger.add(lambda msg: print(msg), level="DEBUG")

# First step: Run the CLI command with --easy flag and save output to a temporary file
def test_cli_with_easy_flag():
    """Test the CLI with the --easy flag."""
    
    logger.info("Testing CLI with --easy flag")
    
    # Create a temporary file to save the output
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as tmp:
        tmp_path = tmp.name
    
    # Run the CLI command
    cmd = f"./run_cli.py --easy 3 --save-to-jsonl {tmp_path}"
    logger.info(f"Executing command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        logger.info(f"Command executed successfully with exit code: {result.returncode}")
        
        if result.stdout:
            logger.info(f"Command output: {result.stdout}")
        
        # Now read the saved output
        logger.info(f"Reading results from {tmp_path}")
        results = []
        with open(tmp_path, 'r', encoding='utf-8') as f:
            for line in f:
                results.append(json.loads(line))
        
        # Analyze each result for the phone number
        for i, result in enumerate(results):
            logger.info(f"\nResult {i+1}:")
            name = result.get('name', 'Unknown')
            city = result.get('city', 'Unknown')
            state = result.get('state', 'Unknown')
            phone = result.get('phone', 'Unknown')
            
            logger.info(f"  Name: {name}")
            logger.info(f"  City/State: {city}, {state}")
            logger.info(f"  Phone: {phone}")
            
            # Check if the phone field is present
            if phone == 'Unknown':
                logger.error("  Phone field is missing in the result!")
            
            # Extract DDD from phone and check if it's valid
            if phone != 'Unknown' and '(' in phone and ')' in phone:
                ddd = phone.split('(')[1].split(')')[0].strip()
                logger.info(f"  DDD extracted from phone: {ddd}")
                
                # Import the BrazilianLocationSampler to check expected DDD
                try:
                    from ptbr_sampler.br_location_class import BrazilianLocationSampler
                    sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
                    
                    # Get city data and expected DDD
                    city_data = sampler.city_data_by_name.get(city)
                    if city_data:
                        expected_ddd = city_data.get('ddd', 'Unknown')
                        logger.info(f"  Expected DDD for {city}: {expected_ddd}")
                        
                        if ddd == expected_ddd:
                            logger.info("  ✅ DDD matches expected value")
                        else:
                            logger.error(f"  ❌ DDD mismatch: {ddd} != {expected_ddd}")
                    else:
                        logger.warning(f"  ⚠️ City {city} not found in sampler data")
                except Exception as e:
                    logger.error(f"  Error checking DDD: {e}")
            else:
                logger.error(f"  Invalid phone format: {phone}")
        
        return results
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e}")
        logger.error(f"Exit code: {e.returncode}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr}")
        return None
    finally:
        # Clean up the temporary file
        try:
            os.unlink(tmp_path)
            logger.debug(f"Temporary file {tmp_path} removed")
        except Exception as e:
            logger.error(f"Error removing temporary file: {e}")

if __name__ == "__main__":
    test_cli_with_easy_flag() 