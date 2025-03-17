#!/usr/bin/env python
"""Script to locate and fix the DDD issue in the ptbr-sampler codebase."""

import re
import sys
from pathlib import Path
from loguru import logger

logger.remove()
logger.add(lambda msg: print(msg), level="DEBUG")

def find_phone_generation_logic():
    """Find all files that might contain phone number generation logic."""
    logger.info("Searching for files with phone number generation logic...")
    
    potential_files = []
    base_dir = Path(__file__).parent
    
    # Look for Python files that might contain phone generation
    for py_file in base_dir.glob("**/*.py"):
        if py_file.name == "fix_ddd_issue.py" or py_file.name == "test_real_world.py":
            continue
            
        content = py_file.read_text(encoding="utf-8")
        
        # Check for phone-related terms
        if any(term in content.lower() for term in ["phone", "ddd", "telefone", "fone"]):
            potential_files.append(py_file)
            logger.info(f"Found potential file: {py_file.relative_to(base_dir)}")
    
    return potential_files

def check_file_for_ddd_issue(file_path):
    """Check if the file might contain the DDD issue."""
    content = file_path.read_text(encoding="utf-8")
    
    # Look for phone generation patterns
    phone_generation_patterns = [
        r"def\s+generate_(?:phone|telefone|fone)",  # Function definitions
        r"phone\s*=\s*['\"]?\(\d+\)",  # Phone assignments
        r"ddd\s*=",  # DDD assignments
        r"phone_format",  # Phone formatting
    ]
    
    matches = []
    line_numbers = []
    
    for pattern in phone_generation_patterns:
        for match in re.finditer(pattern, content):
            line_number = content[:match.start()].count('\n') + 1
            matches.append(match.group())
            line_numbers.append(line_number)
            logger.info(f"  Found in {file_path.name}:{line_number} - {match.group()}")
    
    return bool(matches), matches, line_numbers

def check_all_potential_files():
    """Check all potential files for DDD issues."""
    potential_files = find_phone_generation_logic()
    
    if not potential_files:
        logger.warning("No potential files found with phone generation logic")
        return []
    
    issue_files = []
    
    for file_path in potential_files:
        logger.info(f"\nChecking {file_path.name} for DDD issues...")
        has_issue, matches, line_numbers = check_file_for_ddd_issue(file_path)
        
        if has_issue:
            logger.info(f"Potential DDD issue found in {file_path}")
            issue_files.append((file_path, matches, line_numbers))
        else:
            logger.info(f"No DDD issues found in {file_path}")
    
    return issue_files

def fix_ddd_issue_in_sampler(file_path):
    """Fix the DDD issue in the sampler.py file."""
    content = file_path.read_text(encoding="utf-8")
    
    # Look for phone generation in the sample function
    phone_generation_pattern = re.compile(
        r'(phone\s*=\s*["\']?\(\s*)\d+(\s*\)\s*[\d\-]+["\']?)',
        re.MULTILINE
    )
    
    # Count potential matches
    matches = list(phone_generation_pattern.finditer(content))
    logger.info(f"Found {len(matches)} potential phone generation patterns")
    
    if not matches:
        logger.warning("No phone generation pattern found to fix")
        return False
    
    # This is the core fix: replace hardcoded DDD with the city's DDD
    new_content = content
    
    # First approach: Simple pattern replacement
    # Replace "phone = f"(11) ..." with "phone = f"({ddd}) ..."
    new_content = re.sub(
        r'(phone\s*=\s*f?["\']?\()\s*\d+(\s*\)\s*)',
        r'\1{ddd}\2',
        new_content
    )
    
    # Second approach: If there's a DDD variable extracted from city data
    # Look for where DDD might be set from city_info and ensure it's used
    ddd_assignment_pattern = r'ddd\s*=\s*city_info\.get\(["\']ddd["\']\s*(?:,\s*["\']?\d+["\']?)?\)'
    if not re.search(ddd_assignment_pattern, new_content):
        # If there's no DDD extraction from city data, add it before phone generation
        # Find where city_info is set
        city_info_pattern = r'(city_info\s*=\s*.*?\n)'
        city_info_match = re.search(city_info_pattern, new_content)
        
        if city_info_match:
            # Add DDD extraction after city_info setting
            ddd_extraction = city_info_match.group(0) + "    ddd = city_info.get('ddd', '11')  # Default to 11 if no DDD found\n"
            new_content = new_content.replace(city_info_match.group(0), ddd_extraction)
    
    # Save the modified content
    if new_content != content:
        logger.info(f"Fixing DDD issue in {file_path.name}")
        file_path.write_text(new_content, encoding="utf-8")
        return True
    else:
        logger.warning("No changes made to fix DDD issue")
        return False

def main():
    """Main function to find and fix DDD issues."""
    logger.info("Starting DDD issue detection and fixing...")
    
    issue_files = check_all_potential_files()
    
    if not issue_files:
        logger.info("No files with potential DDD issues found")
        return
    
    logger.info(f"Found {len(issue_files)} files with potential DDD issues")
    
    for file_path, matches, line_numbers in issue_files:
        if "sampler.py" in str(file_path):
            logger.info(f"\nAttempting to fix DDD issue in {file_path}")
            fixed = fix_ddd_issue_in_sampler(file_path)
            
            if fixed:
                logger.info(f"✅ Successfully fixed DDD issue in {file_path}")
            else:
                logger.warning(f"⚠️ Could not fix DDD issue in {file_path}")
        else:
            logger.info(f"Skipping fix for {file_path} (not sampler.py)")
    
    logger.info("\nDDD issue detection and fixing completed")

if __name__ == "__main__":
    main() 