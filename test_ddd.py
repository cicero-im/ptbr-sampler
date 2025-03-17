from ptbr_sampler.br_location_class import BrazilianLocationSampler

# Initialize the sampler
sampler = BrazilianLocationSampler('ptbr_sampler/data/cities_with_ceps.json')

# Check number of cities loaded
print(f'Total cities in city_data_by_name: {len(sampler.city_data_by_name)}')

# Check how many cities have DDDs
ddd_count = sum(1 for city_data in sampler.city_data_by_name.values() if 'ddd' in city_data)
print(f'Cities with DDD in city_data_by_name: {ddd_count}')

# Display a few sample cities and their DDDs
print('\nSample city DDDs:')
for city_name, city_data in list(sampler.city_data_by_name.items())[:5]:
    print(f'{city_name}: {city_data.get("ddd", "NO DDD")}')

# Check specific cities mentioned in the issues
print('\nChecking specific cities:')
cities_to_check = ['São Paulo', 'Cruz Alta', 'Pacatuba', 'Niterói', 'Marília', 'Codó', 'Curitiba', 'Isaías Coelho']
for city_name in cities_to_check:
    if city_name in sampler.city_data_by_name:
        ddd = sampler.city_data_by_name[city_name].get('ddd', 'NO DDD')
        print(f'{city_name}: {ddd}')
    else:
        print(f'{city_name}: Not found in city_data_by_name')

# Test get_state_and_city for a few iterations
print('\nTesting get_state_and_city():')
for i in range(5):
    state_name, state_abbr, city_name = sampler.get_state_and_city()
    ddd = sampler.city_data_by_name[city_name].get('ddd', 'NO DDD')
    print(f'{city_name} ({state_abbr}): DDD {ddd}') 