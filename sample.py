#!/usr/bin/env python3
"""
Sample module that provides a clean API for the Brazilian Name and Location generator.

This module wraps the src.sampler.sample function and makes it easier to use programmatically.
"""

from src.br_name_class import TimePeriod
from src.sampler import sample as sampler_function


def sample(q: int = 1, save_to_jsonl: str = None | None, all_data: bool = False, **kwargs) -> dict | list[dict]:
    """
    Generate random Brazilian name, location, and document samples.

    Args:
        q: Number of samples to generate (same as qty parameter in cli.sample)
        save_to_jsonl: Path to save generated samples as JSONL
        all_data: Include all possible data in the generated samples
        **kwargs: Additional parameters passed directly to cli.sample

    Common keyword arguments:
        time_period: TimePeriod enum for name generation era
        city_only: Return only city names
        state_abbr_only: Return only state abbreviations
        state_full_only: Return only full state names
        only_cep: Return only CEP (Brazilian postal code)
        cep_without_dash: Format CEP without dash
        return_only_name: Return only names without location
        name_raw: Return names in raw format (all caps)
        only_surname: Return only surnames
        top_40: Use only top 40 surnames
        with_only_one_surname: Use single surname
        always_middle: Always include middle name
        only_middle: Return only middle names
        always_cpf: Include CPF in documents
        always_pis: Include PIS in documents
        always_cnpj: Include CNPJ in documents
        always_cei: Include CEI in documents
        always_rg: Include RG in documents
        only_cpf: Generate only CPF
        only_pis: Generate only PIS
        only_cnpj: Generate only CNPJ
        only_cei: Generate only CEI
        only_rg: Generate only RG
        include_issuer: Include issuing state in RG

    Returns:
        A dictionary with the generated sample if q=1, or a list of dictionaries if q>1.
        Each dictionary contains the following keys:
        - name: First name
        - middle_name: Middle name (if generated)
        - surnames: Last names
        - city: City name
        - state: State name
        - state_abbr: State abbreviation
        - cep: CEP (Brazilian postal code)
        - cpf: CPF number (Brazilian ID)
        - rg: RG number (Brazilian ID)
        - pis: PIS number (if requested)
        - cnpj: CNPJ number (if requested)
        - cei: CEI number (if requested)
    """
    # Map the 'q' parameter to 'qty' expected by cli_sample
    if 'q' in kwargs:
        # If both q and qty are provided, use qty
        pass
    elif q != 1:
        # Only set qty if q is different from default
        kwargs['qty'] = q

    # Handle save_to_jsonl parameter
    if save_to_jsonl:
        kwargs['save_to_jsonl'] = save_to_jsonl

    # Handle all_data parameter
    if all_data:
        kwargs['all_data'] = all_data

    # Call the underlying sample function
    return sampler_function(q=q, **kwargs)


# Export the TimePeriod enum for convenience
__all__ = ['TimePeriod', 'sample']
