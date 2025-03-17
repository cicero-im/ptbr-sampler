#!/usr/bin/env python3
"""Final test script to verify the DDD fix."""

import sys
import json
import tempfile
from pathlib import Path
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")

def test_ddd_consistency():
    """Test if the phone DDD matches the city DDD."""
    logger.info("Starting final DDD consistency test")
    
    try:
        from ptbr_sampler.sampler import sample
        from ptbr_sampler.br_location_class import BrazilianLocationSampler
        from ptbr_sampler.br_name_class import TimePeriod
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return
    
    # Create a temporary file for output
    temp_output = tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False, dir='/tmp')
    output_path = temp_output.name
    temp_output.close()
    
    logger.info(f"Generating 10 samples to {output_path}")
    
    try:
        # Generate samples
        sample(
            qty=10,
            q=None,
            city_only=False,
            state_abbr_only=False,
            state_full_only=False,
            only_cep=False,
            cep_without_dash=False,
            make_api_call=True,
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
        
        # Initialize location sampler for DDD lookup
        location_sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')
        
        # Read generated samples
        with open(output_path, 'r', encoding='utf-8') as f:
            samples = [json.loads(line) for line in f]
        
        matches = 0
        mismatches = 0
        
        for i, sample in enumerate(samples):
            name = sample.get('name', '')
            city = sample.get('city', '')
            state = sample.get('state_abbr', '')
            phone = sample.get('phone', '')
            
            logger.info(f"Sample {i+1}: {name} from {city}, {state}")
            logger.info(f"  Phone: {phone}")
            
            if not phone or not isinstance(phone, str) or len(phone) < 5:
                logger.warning(f"  Invalid phone format: {phone}")
                continue
            
            # Extract DDD from phone
            phone_ddd = None
            if phone.startswith('(') and ')' in phone:
                phone_ddd = phone[1:phone.index(')')]
            
            if not phone_ddd:
                logger.warning(f"  Could not extract DDD from phone: {phone}")
                continue
            
            logger.info(f"  Phone DDD: {phone_ddd}")
            
            # Get expected DDD for city using the new method
            expected_ddd = None
            try:
                # Use the new method with both city name and state
                city_data = location_sampler.get_city_data_by_name(city, state)
                if city_data:
                    expected_ddd = city_data.get('ddd')
                    logger.info(f"  Expected DDD for {city}, {state}: {expected_ddd}")
                else:
                    logger.warning(f"  City data not found for {city}, {state}")
            except Exception as e:
                logger.error(f"  Error getting expected DDD: {e}")
            
            if expected_ddd and phone_ddd:
                if expected_ddd == phone_ddd:
                    logger.info(f"  ✅ DDD match: {phone_ddd} == {expected_ddd}")
                    matches += 1
                else:
                    logger.error(f"  ❌ DDD mismatch: {phone_ddd} != {expected_ddd}")
                    mismatches += 1
        
        total = matches + mismatches
        success_rate = (matches / total * 100) if total > 0 else 0
        
        logger.info(f"DDD Consistency Results:")
        logger.info(f"  Total samples checked: {total}")
        logger.info(f"  Matches: {matches}")
        logger.info(f"  Mismatches: {mismatches}")
        logger.info(f"  Success rate: {success_rate:.2f}%")
        
    except Exception as e:
        logger.error(f"Error generating samples: {e}")
    finally:
        # Clean up
        try:
            Path(output_path).unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"Error cleaning up temporary file: {e}")

if __name__ == "__main__":
    test_ddd_consistency() 