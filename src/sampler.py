"""
Brazilian Sample Generator

Core functionality for generating Brazilian name, location, and document samples.
"""

import json
from pathlib import Path

from .br_location_class import BrazilianLocationSampler
from .br_name_class import BrazilianNameSampler, NameComponents, TimePeriod
from .document_sampler import DocumentSampler


def parse_result(
    location: str, name_components: NameComponents, documents: dict[str, str], state_info: tuple[str, str, str] | None = None
) -> dict:
    """Parse sample results into a standardized dictionary format.

    Args:
        location: Full location string
        name_components: Named tuple with name components
        documents: Dictionary of document numbers
        state_info: Optional tuple of (state_name, state_abbr, city_name)

    Returns:
        dict: Structured dictionary with parsed components
    """
    result = {
        'name': name_components.first_name if name_components else '',
        'middle_name': name_components.middle_name if name_components else '',
        'surnames': name_components.surname if name_components else '',
        'city': '',
        'state': '',
        'state_abbr': '',
        'cep': '',
        'cpf': documents.get('cpf', ''),
        'rg': documents.get('rg', ''),
        'pis': documents.get('pis', ''),
        'cnpj': documents.get('cnpj', ''),
        'cei': documents.get('cei', ''),
    }

    if state_info:
        result['state'], result['state_abbr'], result['city'] = state_info
    elif location and ', ' in location:
        # Parse location string if available
        try:
            city_part, state_part = location.split(', ')
            if ' - ' in city_part:
                result['city'], cep = city_part.split(' - ')
                result['cep'] = cep
            else:
                result['city'] = city_part

            if '(' in state_part:
                result['state'], abbr = state_part.split(' (')
                result['state_abbr'] = abbr.rstrip(')')
            else:
                result['state'] = state_part
        except ValueError:
            pass

    return result


def sample(
    qty: int = 1,
    q: int | None = None,
    city_only: bool = False,
    state_abbr_only: bool = False,
    state_full_only: bool = False,
    only_cep: bool = False,
    cep_without_dash: bool = False,
    time_period: TimePeriod = TimePeriod.UNTIL_2010,
    return_only_name: bool = False,
    name_raw: bool = False,
    json_path: str | Path = 'src/data/cities_with_ceps.json',
    names_path: str | Path = 'src/data/names_data.json',
    middle_names_path: str | Path = 'src/data/middle_names.json',
    only_surname: bool = False,
    top_40: bool = False,
    with_only_one_surname: bool = False,
    always_middle: bool = False,
    only_middle: bool = False,
    always_cpf: bool = True,
    always_pis: bool = False,
    always_cnpj: bool = False,
    always_cei: bool = False,
    always_rg: bool = True,
    only_cpf: bool = False,
    only_pis: bool = False,
    only_cnpj: bool = False,
    only_cei: bool = False,
    only_rg: bool = False,
    include_issuer: bool = True,
    only_document: bool = False,
    surnames_path: str | Path = 'src/data/surnames_data.json',
    locations_path: str | Path = 'src/data/locations_data.json',
    all_data: bool = False,
) -> dict | list[dict]:
    """Generate random Brazilian samples with comprehensive information.

    This function generates random Brazilian location, name, and document samples
    based on the provided parameters. It handles various combinations of output
    formats and ensures proper state handling for document generation.

    Args:
        qty: Number of samples to generate
        q: Alias for qty parameter (takes precedence if provided)
        city_only: Return only city names
        state_abbr_only: Return only state abbreviations
        state_full_only: Return only full state names
        only_cep: Return only CEP
        cep_without_dash: Format CEP without dash
        time_period: Time period for name sampling
        return_only_name: Return only names without location
        name_raw: Return names in raw format (all caps)
        json_path: Path to city/state data JSON file
        names_path: Path to first names data file
        middle_names_path: Path to middle names data file
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
        only_document: Return only documents
        surnames_path: Path to surnames data file
        locations_path: Path to locations data JSON file
        all_data: Include all possible data in the generated samples
    Returns:
        A dictionary with the generated sample if qty=1, or a list of dictionaries if qty>1.
        Each dictionary contains keys for name, location, and document information.
    """
    # Handle q parameter alias (takes precedence over qty)
    actual_qty = q if q is not None else qty

    # If all_data is True, override other flags to include everything
    if all_data:
        always_cpf = True
        always_pis = True
        always_cnpj = True
        always_cei = True
        always_rg = True
        always_middle = True
        only_cpf = False
        only_pis = False
        only_cnpj = False
        only_cei = False
        only_rg = False
        only_surname = False
        only_middle = False
        only_cep = False
        city_only = False
        state_abbr_only = False
        state_full_only = False
        return_only_name = False
        only_document = False

    try:
        # Initialize samplers separately
        location_sampler = BrazilianLocationSampler(json_path)
        doc_sampler = DocumentSampler()

        # Load surnames data for name sampler
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

        if return_only_name or only_surname or only_middle:
            # Name-only generation
            for _ in range(actual_qty):
                documents = {}
                name_components = None

                if only_surname:
                    name_components = NameComponents(
                        '', None, name_sampler.get_random_surname(top_40=top_40, raw=name_raw, with_only_one_surname=with_only_one_surname)
                    )
                elif only_middle:
                    name_components = name_sampler.get_random_name(raw=name_raw, only_middle=True, return_components=True)
                else:
                    name_components = name_sampler.get_random_name(
                        time_period=time_period,
                        raw=name_raw,
                        include_surname=True,
                        top_40=top_40,
                        with_only_one_surname=with_only_one_surname,
                        always_middle=always_middle,
                        return_components=True,
                    )

                    # Add documents for full names
                    if always_cpf:
                        documents['cpf'] = doc_sampler.generate_cpf()
                    if always_pis:
                        documents['pis'] = doc_sampler.generate_pis()
                    if always_cnpj:
                        documents['cnpj'] = doc_sampler.generate_cnpj()
                    if always_cei:
                        documents['cei'] = doc_sampler.generate_cei()
                    if always_rg:
                        # Use SP as default state for name-only results
                        documents['rg'] = f'{doc_sampler.generate_rg("SP", include_issuer)}'

                results.append((None, name_components, documents))

        elif any([only_cpf, only_pis, only_cnpj, only_cei, only_rg]):
            # Handle document-only generation with proper state handling
            for _ in range(actual_qty):
                documents = {}
                # Generate location first to get proper state for RG
                state_name, state_abbr, city_name = location_sampler.get_state_and_city()

                if only_cpf:
                    documents['cpf'] = doc_sampler.generate_cpf()
                if only_pis:
                    documents['pis'] = doc_sampler.generate_pis()
                if only_cnpj:
                    documents['cnpj'] = doc_sampler.generate_cnpj()
                if only_cei:
                    documents['cei'] = doc_sampler.generate_cei()
                if only_rg:
                    documents['rg'] = f'{doc_sampler.generate_rg(state_abbr, include_issuer)}'

                results.append((None, None, documents))

        else:
            # Full sample generation with location, name, and documents
            for _ in range(actual_qty):
                documents = {}

                # Generate location first to ensure proper state handling
                state_name, state_abbr, city_name = location_sampler.get_state_and_city()

                # Format location string
                if city_only:
                    location = city_name
                elif state_abbr_only:
                    location = state_abbr
                elif state_full_only:
                    location = state_name
                elif only_cep:
                    location = location_sampler._get_random_cep_for_city(city_name)
                    location = location_sampler._format_cep(location, not cep_without_dash)
                else:
                    location = location_sampler.format_full_location(
                        city_name, state_name, state_abbr, include_cep=True, cep_without_dash=cep_without_dash
                    )

                # Generate documents using the correct state
                if always_cpf or only_cpf:
                    documents['cpf'] = doc_sampler.generate_cpf()
                if always_pis or only_pis:
                    documents['pis'] = doc_sampler.generate_pis()
                if always_cnpj or only_cnpj:
                    documents['cnpj'] = doc_sampler.generate_cnpj()
                if always_cei or only_cei:
                    documents['cei'] = doc_sampler.generate_cei()
                if always_rg or only_rg:
                    # Always use the state from our location for RG generation
                    documents['rg'] = f'{doc_sampler.generate_rg(state_abbr, include_issuer)}'

                # Generate name components if needed
                name_components = None

                name_components = name_sampler.get_random_name(
                    time_period=time_period,
                    raw=name_raw,
                    include_surname=True,
                    top_40=top_40,
                    with_only_one_surname=with_only_one_surname,
                    always_middle=always_middle,
                    return_components=True,
                )

                results.append((location, name_components, documents))

        # Convert results to dictionary format
        parsed_results = [
            parse_result(
                location, name_components, documents, state_info=(state_name, state_abbr, city_name) if 'state_name' in locals() else None
            )
            for location, name_components, documents in results
        ]

        return parsed_results[0] if actual_qty == 1 else parsed_results

    except Exception as e:
        # Re-raise the exception with more context
        raise RuntimeError(f'Error generating samples: {e}') from e
