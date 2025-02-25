#!/usr/bin/env python3
"""
Test script to demonstrate the save_to_jsonl parameter.
"""

import json
import os

from sample import sample

# Number of samples to generate
num_samples = 5
output_file = 'samples.jsonl'

# Remove the output file if it already exists
if os.path.exists(output_file):
    os.remove(output_file)
    print(f'Removed existing file: {output_file}')

# Generate samples and save to JSONL
print(f'Generating {num_samples} samples and saving to {output_file}...')
sample(q=num_samples, save_to_jsonl=output_file, all_data=True)

# Verify the file was created
if os.path.exists(output_file):
    print(f'\nFile {output_file} was created successfully.')

    # Count the number of lines in the file
    with open(output_file, encoding='utf-8') as f:
        lines = f.readlines()
        print(f'The file contains {len(lines)} samples.')

    # Read and print the first sample
    if lines:
        first_sample = json.loads(lines[0])
        print('\nFirst sample from the file:')
        print(f'Name: {first_sample["name"]} {first_sample["middle_name"]} {first_sample["surnames"]}')
        print(f'Location: {first_sample["city"]}, {first_sample["state"]} ({first_sample["state_abbr"]})')
        print(f'Documents: CPF={first_sample["cpf"]}, RG={first_sample["rg"]}')
else:
    print(f'Error: File {output_file} was not created.')
