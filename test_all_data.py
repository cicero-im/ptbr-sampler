#!/usr/bin/env python3
"""
Test script to demonstrate the all_data parameter.
"""

from sample import sample

# Generate a sample with all data
result = sample(q=1, all_data=True)

print('Generated sample with all data:')
print('-' * 50)

# Print all keys and values
for key, value in result.items():
    print(f'{key}: {value}')

print('-' * 50)

# Print specific document values
print('\nDocument values:')
print(f'CPF: {result["cpf"]}')
print(f'RG: {result["rg"]}')
print(f'PIS: {result["pis"]}')
print(f'CNPJ: {result["cnpj"]}')
print(f'CEI: {result["cei"]}')

# Print name values
print('\nName values:')
print(f'First name: {result["name"]}')
print(f'Middle name: {result["middle_name"]}')
print(f'Surnames: {result["surnames"]}')

# Print location values
print('\nLocation values:')
print(f'City: {result["city"]}')
print(f'State: {result["state"]}')
print(f'State abbreviation: {result["state_abbr"]}')
print(f'CEP: {result["cep"]}')
