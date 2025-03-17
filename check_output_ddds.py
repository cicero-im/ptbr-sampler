#!/usr/bin/env python
"""
Script to check if the DDDs in the output.jsonl file match the expected DDDs for their cities.
"""

import json
import sys
from pathlib import Path

# Known city to DDD mappings for validation
KNOWN_DDDS = {
    'São Paulo': '11',
    'Guarulhos': '11',
    'Osasco': '11',
    'Santos': '13',
    'Campinas': '19',
    'Rio de Janeiro': '21',
    'Niterói': '21',
    'Belo Horizonte': '31',
    'Contagem': '31',
    'Uberlândia': '34',
    'Juiz de Fora': '32',
    'Curitiba': '41',
    'Londrina': '43',
    'Porto Alegre': '51',
    'Caxias do Sul': '54',
    'Salvador': '71',
    'Feira de Santana': '75',
    'Recife': '81',
    'João Pessoa': '83',
    'Natal': '84',
    'Fortaleza': '85',
    'Teresina': '86',
    'Brasília': '61',
    'Goiânia': '62',
    'Cuiabá': '65',
    'Campo Grande': '67',
    'Manaus': '92',
    'Belém': '91',
    'Macapá': '96',
    'Boa Vista': '95',
    'Palmas': '63',
    'Porto Velho': '69',
    'Rio Branco': '68',
    'Aracaju': '79',
    'Maceió': '82',
    'Florianópolis': '48',
    'Vitória': '27',
    'São Luís': '98',
}

def check_ddds_in_file(file_path):
    """Check if the DDDs in the JSONL file match the expected DDDs for their cities."""
    print(f"Checking DDDs in {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if not lines:
            print(f"File {file_path} is empty.")
            return
            
        mismatches = []
        correct = []
        unknown = []
        
        for i, line in enumerate(lines):
            try:
                data = json.loads(line)
                
                # Extract city and phone
                city = data.get('city', 'Unknown')
                phone = data.get('phone', 'No Phone')
                
                # Extract DDD from phone
                ddd = None
                if phone and '(' in phone and ')' in phone:
                    ddd = phone.split('(')[1].split(')')[0].strip()
                
                # Check if city has a known DDD
                expected_ddd = KNOWN_DDDS.get(city)
                
                if expected_ddd:
                    if ddd == expected_ddd:
                        correct.append((i+1, city, ddd))
                    else:
                        mismatches.append((i+1, city, ddd, expected_ddd))
                else:
                    unknown.append((i+1, city, ddd))
            
            except json.JSONDecodeError:
                print(f"Error parsing JSON on line {i+1}")
                continue
        
        # Print results
        print("\nRESULTS:")
        print(f"Total entries: {len(lines)}")
        print(f"Correct DDDs: {len(correct)}")
        print(f"Unknown cities (no mapping): {len(unknown)}")
        print(f"DDD mismatches: {len(mismatches)}")
        
        if correct:
            print("\nCORRECT MATCHES:")
            for i, city, ddd in correct:
                print(f"  Line {i}: {city} - DDD {ddd}")
        
        if unknown:
            print("\nUNKNOWN CITIES (no mapping):")
            for i, city, ddd in unknown:
                print(f"  Line {i}: {city} - DDD {ddd}")
        
        if mismatches:
            print("\nDDD MISMATCHES:")
            for i, city, actual, expected in mismatches:
                print(f"  Line {i}: {city} - Expected DDD {expected}, Got DDD {actual}")
    
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    file_path = "output/output.jsonl" if len(sys.argv) < 2 else sys.argv[1]
    check_ddds_in_file(file_path) 