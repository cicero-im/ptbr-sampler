# Plan to Fix Brazilian Data Sampler Issues

## Issues Identified

1. **CEP Selection Process Clarification**: 
   - The correct process should be a two-step random selection:
     1. First, select a city using weighted random selection based on population (already implemented)
     2. Then, select a CEP randomly from the city's "ceps" array (already implemented with `random.choice()`)
   - This part of the logic is actually correct in the current implementation

2. **Multiple Samples Per Turn Issue**:
   - The script is generating all samples at once rather than generating a new sample for each "turn"
   - This is happening because the location sampler is being reinitialized multiple times in the `sample()` function in `sampler.py`

## Detailed Fix Plan

### 1. Confirm the CEP Selection Process

The current implementation in `_get_random_cep_for_city()` in `br_location_class.py` is actually correct:

```python
def _get_random_cep_for_city(self, city_name: str) -> str:
    """Generate random CEP from city's available CEPs or CEP range."""
    if city_name not in self.city_data_by_name:
        raise ValueError(f'City not found: {city_name}')

    city_data = self.city_data_by_name[city_name]

    # Try using specific CEPs first
    if city_data.get('ceps'):
        return random.choice(city_data['ceps'])

    # Fall back to generating from CEP range if available
    if city_data.get('cep_range_begins') and city_data.get('cep_range_ends'):
        range_start = int(city_data['cep_range_begins'].replace('-', ''))
        range_end = int(city_data['cep_range_ends'].replace('-', ''))
        return str(random.randint(range_start, range_end))
```

This follows the two-step process:
1. The city is selected using weighted random selection elsewhere in the code
2. Then a CEP is randomly selected from the city's "ceps" array

No changes are needed to this part of the code.

### 2. Fix the Multiple Samples Per Turn Issue

The issue is that the location sampler is being initialized multiple times in the `sample()` function. We need to ensure that:
- The location sampler is initialized only once
- The data is loaded only once
- Each call to generate a sample uses a fresh random selection

Looking at the code in `sampler.py`, there are multiple places where the location sampler is initialized:

1. Lines 188-189:
```python
# Initialize samplers separately
location_sampler = BrazilianLocationSampler(json_path)
```

2. Lines 225-226:
```python
# Initialize samplers separately and load location data if provided
location_sampler = BrazilianLocationSampler(json_path)
```

3. And similar initializations in other conditional blocks.

**Proposed fix:**

1. Move the initialization of the location sampler to the beginning of the `sample()` function, before any conditional blocks
2. Remove all duplicate initializations in the conditional blocks
3. Keep the data loading code in one place at the beginning of the function

```python
def sample(...):
    # Handle q parameter alias (takes precedence over qty)
    actual_qty = q if q is not None else qty
    
    # If all_data is True, override other flags to include everything
    if all_data:
        # (existing code)
    
    try:
        # Initialize samplers only once
        location_sampler = BrazilianLocationSampler(json_path)
        doc_sampler = DocumentSampler()
        
        # Load location data if provided - do this only once
        if locations_path:
            try:
                with Path(locations_path).open(encoding='utf-8') as f:
                    locations_data = json.load(f)
                    # Use locations data if available
                    if 'cities' in locations_data:
                        location_sampler.update_cities(locations_data['cities'])
                    if 'states' in locations_data:
                        location_sampler.update_states(locations_data['states'])
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                # Log but continue with default data
                print(f'Warning: Could not use locations_path data: {e}')
        
        # Load name data only once
        with Path(surnames_path).open(encoding='utf-8') as f:
            surnames_data = json.load(f)
        
        # Create complete data for name sampler
        name_data = {'surnames': surnames_data['surnames']}
        if names_path:
            with Path(names_path).open(encoding='utf-8') as f:
                names_data = json.load(f)
                name_data.update(names_data)
        
        name_sampler = BrazilianNameSampler(
            name_data,  # Pass the combined data
            middle_names_path,
            None,  # No need for names_path as we've already loaded it
        )
        
        # Initialize results list
        results: list[tuple[str, NameComponents, dict[str, str]]] = []
        
        # Now proceed with the conditional blocks, but without reinitializing the samplers
        if only_document:
            # (existing code, but remove sampler initialization)
        elif any([only_cpf, only_pis, only_cnpj, only_cei, only_rg]):
            # (existing code, but remove sampler initialization)
        elif return_only_name or only_surname or only_middle:
            # (existing code, but remove sampler initialization)
        else:
            # (existing code, but remove sampler initialization)
        
        # Rest of the function remains the same
        # ...
    
    except Exception as e:
        # Re-raise the exception with more context
        raise RuntimeError(f'Error generating samples: {e}') from e
```

This change ensures that the samplers are initialized only once and that each sample generation uses a fresh random selection, which should fix the issue of generating multiple samples per turn.

## Implementation Steps

1. Confirm that the CEP selection process is already correctly implemented
2. Fix the duplicate initialization of the location sampler in `sampler.py`
3. Test the changes with the command: `uv run src/cli.py -q 10 --all --save-to-jsonl teste.jsonl`
4. Verify that each sample has a different CEP and that each turn generates a new sample