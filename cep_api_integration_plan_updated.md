# Updated Implementation Plan: CEP API Integration

## Overview

The task is to enhance the CLI tool to support two modes of address data retrieval:

1. **API Mode** (`--make_api_call=True`): Use `cep_wrapper.py` to make real API calls to retrieve CEP data, and supplement missing information (neighborhood, street, building number) with generated data from `address_for_offline.py`.

2. **Offline Mode** (`--make_api_call=False`, default): Use `address_for_offline.py` to generate synthetic address data (street, neighborhood, building number) based on the CEP obtained from the weighted random process.

## Important Consideration for Multiple CEPs

When handling multiple CEPs, we need to ensure that:
- The implementation can process a list of CEPs
- Each CEP is processed appropriately (via API or offline generation)
- The results are returned as a list of dictionaries

The `cep_wrapper.py` module already has functionality for this:
- `get_cep_data(cep: str)` returns a list of dictionaries for a single CEP
- `workers_for_multiple_cep(ceps: list[str])` handles multiple CEPs and returns a list of dictionaries

## Current System Flow

1. The CLI (`src/cli.py`) processes command-line arguments and calls the `sample` function in `src/sampler.py`.
2. The `sample` function uses `BrazilianLocationSampler` to get location data (city, state, CEP).
3. Currently, it doesn't use `cep_wrapper.py` or `address_for_offline.py` for detailed address information.

## Implementation Steps

### 1. Add New CLI Parameter

Add a new parameter `--make_api_call` to the CLI in `src/cli.py`:

```python
MAKE_API_CALL = typer.Option(
    False, 
    '--make-api-call', 
    '-mac', 
    help='Make API calls to retrieve real CEP data instead of generating synthetic address data',
    rich_help_panel='Location Options'
)
```

And update the `sample` function signature to include this parameter.

### 2. Modify the Sampler Module

Update the `sample` function in `src/sampler.py` to:
- Accept the new `make_api_call` parameter
- Implement logic to handle both API and offline modes
- Pass the parameter to the appropriate functions

### 3. Implement Address Data Retrieval Logic

Create a new function in `src/sampler.py` to handle address data retrieval for multiple CEPs:

```python
async def get_address_data_batch(ceps: list[str], make_api_call: bool = False) -> list[dict]:
    """
    Get address data for multiple CEPs, either from API or generated.
    
    Args:
        ceps: List of CEPs to get address data for
        make_api_call: Whether to make API calls or generate data
        
    Returns:
        List of dictionaries with address data (street, neighborhood, building_number)
    """
    address_data_list = []
    
    if make_api_call:
        # Use cep_wrapper to get real data for multiple CEPs
        from src.utils.cep_wrapper import workers_for_multiple_cep
        
        address_from_api = await workers_for_multiple_cep(ceps)
        
        # Process each CEP result
        for cep_data in address_from_api:
            address_data = {
                'street': '',
                'neighborhood': '',
                'building_number': '',
                'cep': cep_data.get('cep', '')
            }
            
            # Extract data from API response
            if not 'error' in cep_data:
                address_data['street'] = cep_data.get('street', '')
                address_data['neighborhood'] = cep_data.get('neighborhood', '')
                
            # If neighborhood is empty or we need a building number, use address_for_offline
            if not address_data['neighborhood'] or not address_data['street']:
                from src.utils.address_for_offline import AddressProvider_for_offline
                address_provider = AddressProvider_for_offline()
                
                if not address_data['neighborhood']:
                    address_data['neighborhood'] = address_provider.bairro()
                if not address_data['street']:
                    address_data['street'] = address_provider.street_prefix() + ' ' + address_provider.last_name()
            
            # Always get building number from address_for_offline
            from src.utils.address_for_offline import AddressProvider_for_offline
            address_provider = AddressProvider_for_offline()
            address_data['building_number'] = address_provider.building_number()
            
            address_data_list.append(address_data)
    else:
        # Use address_for_offline to generate all data for each CEP
        from src.utils.address_for_offline import AddressProvider_for_offline
        
        for cep in ceps:
            address_provider = AddressProvider_for_offline()
            address_data = {
                'street': address_provider.street_prefix() + ' ' + address_provider.last_name(),
                'neighborhood': address_provider.bairro(),
                'building_number': address_provider.building_number(),
                'cep': cep
            }
            address_data_list.append(address_data)
    
    return address_data_list
```

Also create a single-CEP version for convenience:

```python
async def get_address_data(cep: str, make_api_call: bool = False) -> dict:
    """
    Get address data for a single CEP, either from API or generated.
    
    Args:
        cep: The CEP to get address data for
        make_api_call: Whether to make API calls or generate data
        
    Returns:
        Dictionary with address data (street, neighborhood, building_number)
    """
    result = await get_address_data_batch([cep], make_api_call)
    return result[0] if result else {}
```

### 4. Integrate Address Data into Results

Modify the `parse_result` function in `src/sampler.py` to include the new address fields:

```python
def parse_result(
    location: str, 
    name_components: NameComponents, 
    documents: dict[str, str], 
    state_info: tuple[str, str, str] | None = None,
    address_data: dict | None = None
) -> dict:
    # Existing code...
    
    result = {
        # Existing fields...
        'street': '',
        'neighborhood': '',
        'building_number': '',
    }
    
    # Add address data if available
    if address_data:
        result['street'] = address_data.get('street', '')
        result['neighborhood'] = address_data.get('neighborhood', '')
        result['building_number'] = address_data.get('building_number', '')
    
    # Existing code...
    
    return result
```

### 5. Update the Sample Function Flow

Modify the main flow in the `sample` function to:
1. Collect all CEPs that will be used in the samples
2. Call the new `get_address_data_batch` function to get address details for all CEPs at once
3. Include the address data in the results

```python
# In the sample function:
# Collect all CEPs that will be used
all_ceps = []
for i in range(actual_qty):
    # Get state and city
    state_name, state_abbr, city_name = location_sampler.get_state_and_city()
    
    # Get a random CEP for the city
    cep = location_sampler._get_random_cep_for_city(city_name)
    all_ceps.append(cep)

# Get address data for all CEPs at once
address_data_list = asyncio.run(get_address_data_batch(all_ceps, make_api_call))

# Use the address data in the results
for i, address_data in enumerate(address_data_list):
    # Use address_data[i] for the i-th sample
    # ...
```

### 6. Handle Asynchronous API Calls

Since `cep_wrapper.py` uses async functions, we need to ensure proper async handling:
1. Make the `get_address_data_batch` function async
2. Use asyncio to run this function from the synchronous `sample` function

```python
import asyncio

# In the sample function where address data is needed:
address_data_list = asyncio.run(get_address_data_batch(all_ceps, make_api_call))
```

## Testing Plan

1. Test with `--make-api-call=False` (default) to ensure synthetic address generation works correctly
2. Test with `--make-api-call=True` to verify API integration works
3. Test with multiple samples to ensure batch processing works correctly
4. Test edge cases:
   - API returns empty neighborhood
   - API returns error
   - Invalid CEP

## Implementation Considerations

1. **Error Handling**: Ensure robust error handling for API calls, with fallback to synthetic data generation
2. **Performance**: API calls will be slower than synthetic data generation, so consider caching or batching
3. **Data Consistency**: Ensure generated data is consistent with real data format
4. **Batch Processing**: Process multiple CEPs in a single API call when possible to improve performance