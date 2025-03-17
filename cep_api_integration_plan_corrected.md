# Corrected Implementation Plan: CEP API Integration

## Overview

The task is to enhance the CLI tool to support two modes of address data retrieval:

1. **API Mode** (`--make_api_call=True`): Use `cep_wrapper.py` to make real API calls to retrieve CEP data, and supplement missing information (neighborhood, street, building number) with generated data from `address_for_offline.py`.

2. **Offline Mode** (`--make_api_call=False`, default): Use `address_for_offline.py` to generate synthetic address data (street, neighborhood, building number) based on the CEP obtained from the weighted random process.

## API Response Format

The `cep_wrapper.py` functions return data in the following format:

```
[
  {
    "cep": "36335000",
    "state": "MG",
    "city": "Ritápolis",
    "neighborhood": "",
    "street": "",
    "service": "viacep"
  }
]
```

Key points:
- The response is a list of dictionaries or a single dictionary
- Sometimes the `neighborhood` and `street` fields are empty
- The CEP in the result should always include the dash ("-"), regardless of how it was passed to the API

## Current System Flow

1. The CLI (`ptbr_sampler/cli.py`) processes command-line arguments and calls the `sample` function in `ptbr_sampler/sampler.py`.
2. The `sample` function uses `BrazilianLocationSampler` to get location data (city, state, CEP).
3. Currently, it doesn't use `cep_wrapper.py` or `address_for_offline.py` for detailed address information.

## Implementation Steps

### 1. Add New CLI Parameter

Add a new parameter `--make_api_call` to the CLI in `ptbr_sampler/cli.py`:

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

Update the `sample` function in `ptbr_sampler/sampler.py` to:
- Accept the new `make_api_call` parameter
- Implement logic to handle both API and offline modes
- Pass the parameter to the appropriate functions

### 3. Implement Address Data Retrieval Logic

Create a new function in `ptbr_sampler/sampler.py` to handle address data retrieval for multiple CEPs:

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
        from ptbr_sampler.utils.cep_wrapper import workers_for_multiple_cep

        # Format CEPs to remove dashes before API call
        formatted_ceps = [cep.replace('-', '') for cep in ceps]

        # Get data from API
        cep_data_list = await workers_for_multiple_cep(formatted_ceps)

        # Process each CEP result
        for cep_data in cep_data_list:
            address_data = {
                'street': '',
                'neighborhood': '',
                'building_number': '',
                'cep': cep_data.get('cep', ''),  # This will have the dash format from the API
                'state': cep_data.get('state', ''),
                'city': cep_data.get('city', '')
            }

            # Extract data from API response if no error
            if 'error' not in cep_data:
                address_data['street'] = cep_data.get('street', '')
                address_data['neighborhood'] = cep_data.get('neighborhood', '')

            # If neighborhood is empty, use address_for_offline
            if not address_data['neighborhood']:
                from ptbr_sampler.utils.address_for_offline import AddressProvider_for_offline
                address_provider = AddressProvider_for_offline()
                address_data['neighborhood'] = address_provider.bairro()

            # If street is empty, use address_for_offline
            if not address_data['street']:
                from ptbr_sampler.utils.address_for_offline import AddressProvider_for_offline
                address_provider = AddressProvider_for_offline()
                address_data['street'] = address_provider.street_prefix() + ' ' + address_provider.last_name()

            # Always get building number from address_for_offline
            from ptbr_sampler.utils.address_for_offline import AddressProvider_for_offline
            address_provider = AddressProvider_for_offline()
            address_data['building_number'] = address_provider.building_number()

            address_data_list.append(address_data)
    else:
        # Use address_for_offline to generate all data for each CEP
        from ptbr_sampler.utils.address_for_offline import AddressProvider_for_offline

        for cep in ceps:
            # Ensure CEP has dash format
            formatted_cep = cep
            if '-' not in formatted_cep and len(formatted_cep) == 8:
                formatted_cep = f"{formatted_cep[:5]}-{formatted_cep[5:]}"

            address_provider = AddressProvider_for_offline()
            address_data = {
                'street': address_provider.street_prefix() + ' ' + address_provider.last_name(),
                'neighborhood': address_provider.bairro(),
                'building_number': address_provider.building_number(),
                'cep': formatted_cep
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

Modify the `parse_result` function in `ptbr_sampler/sampler.py` to include the new address fields:

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

        # If we have city/state from address_data, use it (API mode)
        if address_data.get('city'):
            result['city'] = address_data.get('city', '')
        if address_data.get('state'):
            result['state'] = address_data.get('state', '')
        if address_data.get('cep'):
            result['cep'] = address_data.get('cep', '')

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
    formatted_cep = location_sampler._format_cep(cep, True)  # Always include dash
    all_ceps.append(formatted_cep)

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
   - API returns empty street
   - API returns error
   - Invalid CEP

## Implementation Considerations

1. **Error Handling**: Ensure robust error handling for API calls, with fallback to synthetic data generation
2. **Performance**: API calls will be slower than synthetic data generation, so consider caching or batching
3. **Data Consistency**: Ensure generated data is consistent with real data format
4. **CEP Formatting**: Always ensure CEPs have the dash format in the final output
5. **Batch Processing**: Process multiple CEPs in a single API call when possible to improve performance
