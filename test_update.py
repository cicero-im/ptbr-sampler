import json
from pathlib import Path
from ptbr_sampler.br_location_class import BrazilianLocationSampler

print("Starting test to check DDD preservation...")

# Initialize with cities_with_ceps.json
print("\n1. Initialize with cities_with_ceps.json:")
sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')

# Check a few cities before update
cities_to_check = ['São Paulo', 'Curitiba', 'Niterói', 'Isaías Coelho']
print("\nDDDs before update:")
for city in cities_to_check:
    if city in sampler.city_data_by_name:
        ddd = sampler.city_data_by_name[city].get('ddd', 'NO DDD')
        print(f"{city}: {ddd}")
    else:
        print(f"{city}: Not found")

# Load locations_data.json
print("\n2. Loading locations_data.json:")
try:
    with Path('ptbr_sampler/data/locations_data.json').open() as f:
        locations_data = json.load(f)
    print(f"Successfully loaded locations_data.json with {len(locations_data.get('cities', {}))} cities")
    
    # Check if locations_data has DDDs
    ddd_count = sum(1 for city_data in locations_data.get('cities', {}).values() 
                      if 'ddd' in city_data)
    print(f"DDDs in locations_data.json: {ddd_count}/{len(locations_data.get('cities', {}))}")
    
    # Check the same cities in locations_data
    print("\nDDDs in locations_data.json:")
    for city in cities_to_check:
        found = False
        for city_key, city_data in locations_data.get('cities', {}).items():
            if city_data.get('city_name') == city:
                ddd = city_data.get('ddd', 'NO DDD')
                print(f"{city}: {ddd}")
                found = True
                break
        if not found:
            print(f"{city}: Not found")
    
    # Update sampler with locations_data
    print("\n3. Updating sampler with locations_data.json:")
    if 'cities' in locations_data:
        sampler.update_cities(locations_data['cities'])
        print(f"Updated with {len(locations_data['cities'])} cities")
        
    # Check the same cities after update
    print("\nDDDs after update:")
    for city in cities_to_check:
        if city in sampler.city_data_by_name:
            ddd = sampler.city_data_by_name[city].get('ddd', 'NO DDD')
            print(f"{city}: {ddd}")
        else:
            print(f"{city}: Not found")
    
except Exception as e:
    print(f"Error: {e}") 