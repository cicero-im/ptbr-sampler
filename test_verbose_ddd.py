#!/usr/bin/env python
"""Test script to identify exactly where the DDD desynchronization happens."""

import sys
import json
import tempfile
import subprocess
from pathlib import Path
from loguru import logger

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg), level="DEBUG")

def run_test_with_debug():
    """Run a test with extensive debug output to trace the DDD flow."""
    logger.info("=" * 80)
    logger.info("VERBOSE DDD SYNCHRONIZATION TEST")
    logger.info("=" * 80)

    # First step: Make sure our logging is verbose enough to catch issues
    logger.info("Enabling debug logging for all relevant modules")
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # We'll create a temporary file for capturing the output
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as tmp:
        output_path = tmp.name

    logger.info(f"Using temporary output path: {output_path}")
    
    # Add a very invasive debug tracer for the sampler module
    debug_code = """
import sys
from pathlib import Path
import ptbr_sampler.sampler
from loguru import logger

# Add debug logger
logger.add("ddd_trace.log", level="DEBUG")

# Store the original sample function
original_sample = ptbr_sampler.sampler.sample

# Create a wrapper to log all the DDD related actions
def debug_sample_wrapper(*args, **kwargs):
    logger.debug(f"==== START SAMPLE CALL ====")
    logger.debug(f"Sample args: {args}")
    logger.debug(f"Sample kwargs: {kwargs}")
    
    results = original_sample(*args, **kwargs)
    
    # Log results (only focus on city and phone)
    logger.debug(f"Sample results summary:")
    for i, result in enumerate(results):
        name = result.get('name', '')
        city = result.get('city', '')
        state = result.get('state', '')
        phone = result.get('phone', '')
        logger.debug(f"Result {i+1}: {name} - {city}, {state} - Phone: {phone}")
        
        # If there's a phone, extract DDD
        if phone and '(' in phone and ')' in phone:
            ddd = phone.split('(')[1].split(')')[0].strip()
            logger.debug(f"  Phone DDD: {ddd}")
            
            # Import sampler to check expected DDD
            from ptbr_sampler.br_location_class import BrazilianLocationSampler
            try:
                sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
                city_data = sampler.city_data_by_name.get(city)
                if city_data:
                    expected_ddd = city_data.get('ddd', 'Unknown')
                    logger.debug(f"  Expected DDD for {city}: {expected_ddd}")
                    
                    if ddd == expected_ddd:
                        logger.debug(f"  ✅ DDD matches expected value")
                    else:
                        logger.debug(f"  ❌ DDD mismatch: {ddd} != {expected_ddd}")
                else:
                    logger.debug(f"  ⚠️ City {city} not found in city_data_by_name")
            except Exception as e:
                logger.error(f"Error checking DDD: {e}")
    
    logger.debug(f"==== END SAMPLE CALL ====")
    return results

# Replace the sample function with our debug wrapper
ptbr_sampler.sampler.sample = debug_sample_wrapper

logger.debug("Patched sample function with debug wrapper")
    """
    
    # Write the debug code to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as debug_file:
        debug_path = debug_file.name
        debug_file.write(debug_code.encode())
    
    # Run CLI command with the debug module preloaded
    cmd = f"python -c 'import sys; sys.path.insert(0, \".\"); exec(open(\"{debug_path}\").read()); from ptbr_sampler import run_cli; run_cli()' --easy 3 --save-to-jsonl {output_path}"
    
    logger.info(f"Running command: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True
        )
        logger.info("Command completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        return
    
    # Check the debug log
    debug_log = Path("ddd_trace.log")
    if debug_log.exists():
        logger.info("Reading debug log:")
        debug_content = debug_log.read_text()
        
        # Extract the most relevant parts
        ddd_lines = [line for line in debug_content.splitlines() 
                    if "DDD" in line and ("mismatch" in line or "matches" in line)]
        
        logger.info(f"Found {len(ddd_lines)} DDD check results")
        for line in ddd_lines:
            if "mismatch" in line:
                logger.error(f"  {line}")
            else:
                logger.info(f"  {line}")
    else:
        logger.warning("Debug log file not found")
    
    # Read the output file
    if Path(output_path).exists():
        logger.info(f"Reading output file: {output_path}")
        with open(output_path, 'r') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            try:
                data = json.loads(line)
                city = data.get('city', 'Unknown')
                phone = data.get('phone', 'Unknown')
                
                logger.info(f"Entry {i+1}: {city} - {phone}")
                
                if phone != 'Unknown' and '(' in phone and ')' in phone:
                    ddd = phone.split('(')[1].split(')')[0].strip()
                    
                    # Import sampler to check expected DDD
                    from ptbr_sampler.br_location_class import BrazilianLocationSampler
                    sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
                    city_data = sampler.city_data_by_name.get(city)
                    
                    if city_data:
                        expected_ddd = city_data.get('ddd', 'Unknown')
                        logger.info(f"  Used DDD: {ddd}, Expected DDD: {expected_ddd}")
                        
                        if ddd == expected_ddd:
                            logger.info(f"  ✅ DDD matches")
                        else:
                            logger.error(f"  ❌ DDD mismatch")
                    else:
                        logger.warning(f"  ⚠️ City {city} not found in city_data_by_name")
            except json.JSONDecodeError:
                logger.error(f"Could not parse line {i+1}")
    
    # Clean up temp files
    try:
        Path(output_path).unlink()
        Path(debug_path).unlink()
        logger.debug("Cleaned up temporary files")
    except Exception as e:
        logger.error(f"Error cleaning up temp files: {e}")

if __name__ == "__main__":
    run_test_with_debug() 