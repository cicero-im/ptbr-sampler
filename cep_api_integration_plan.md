# Implementation Plan: CEP API Integration

## Overview

The task is to enhance the CLI tool to support two modes of address data retrieval:

1. **API Mode** (`--make_api_call=True`): Use `cep_wrapper.py` to make real API calls to retrieve CEP data, and supplement missing information (neighborhood, street, building number) with generated data from `address_for_offline.py`.

2. **Offline Mode** (`--make_api_call=False`, default): Use `address_for_offline.py` to generate synthetic address data (street, neighborhood, building number) based on the CEP obtained from the weighted random process.

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

Create a new function in `ptbr_sampler/sampler.py` to handle address data retrieval:

```python
async def get_address_data(cep: str | list, make_api_call: bool = False) -> dict:
    """
    Get address data for a CEP, either from API or generated.

    Args:
        cep: The CEP to get address data for
        make_api_call: Whether to make API calls or generate data

    Returns:
        Dictionary with address data (street, neighborhood, building_number)
    """
    address_data = {
        'street': '',
        'neighborhood': '',
        'building_number': ''
    }

    if make_api_call:
        # Use cep_wrapper to get real data
        cep_data = await get_cep_data(cep)

        # Extract data from API response
        if cep_data and not 'error' in cep_data[0]:
            address_data['street'] = cep_data[0].get('street', '')
            address_data['neighborhood'] = cep_data[0].get('neighborhood', '')

        # If neighborhood is empty or we need a building number, use address_for_offline
        if not address_data['neighborhood'] or not address_data['street']:
            address_provider = AddressProvider_for_offline()
            if not address_data['neighborhood']:
                address_data['neighborhood'] = address_provider.bairro()
            if not address_data['street']:
                address_data['street'] = address_provider.street_prefix() + ' ' + address_provider.last_name()

        # Always get building number from address_for_offline
        address_provider = AddressProvider_for_offline()
        address_data['building_number'] = address_provider.building_number()
    else:
        # Use address_for_offline to generate all data
        address_provider = AddressProvider_for_offline()
        address_data['street'] = address_provider.street_prefix() + ' ' + address_provider.last_name()
        address_data['neighborhood'] = address_provider.bairro()
        address_data['building_number'] = address_provider.building_number()

    return address_data
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

    # Existing code...

    return result
```

### 5. Update the Sample Function Flow

Modify the main flow in the `sample` function to:
1. Get CEP data as it currently does
2. Call the new `get_address_data` function to get address details
3. Include the address data in the results

### 6. Handle Asynchronous API Calls

Since `cep_wrapper.py` uses async functions, we need to ensure proper async handling:
1. Make the `get_address_data` function async
2. Use asyncio to run this function from the synchronous `sample` function

```python
import asyncio

# In the sample function where address data is needed:
address_data = asyncio.run(get_address_data(cep, make_api_call))
```

## Testing Plan

1. Test with `--make-api-call=False` (default) to ensure synthetic address generation works correctly
2. Test with `--make-api-call=True` to verify API integration works
3. Test edge cases:
   - API returns empty neighborhood
   - API returns error
   - Invalid CEP

## Implementation Considerations

1. **Error Handling**: Ensure robust error handling for API calls, with fallback to synthetic data generation
2. **Performance**: API calls will be slower than synthetic data generation, so consider caching or batching
3. **Data Consistency**: Ensure generated data is consistent with real data format
