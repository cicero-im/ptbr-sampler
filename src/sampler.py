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


def save_to_jsonl_file(data: list[dict], filename: str) -> None:
    """Save generated samples to a JSONL file.

    Args:
        data: List of dictionaries containing sample data
        filename: Path to the output JSONL file
    """
    with Path(filename).open('w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def sample(
    qty: int,
    q: int | None,
    city_only: bool,
    state_abbr_only: bool,
    state_full_only: bool,
    only_cep: bool,
    cep_without_dash: bool,
    time_period: TimePeriod,
    return_only_name: bool,
    name_raw: bool,
    json_path: str | Path,
    names_path: str | Path,
    middle_names_path: str | Path,
    only_surname: bool,
    top_40: bool,
    with_only_one_surname: bool,
    always_middle: bool,
    only_middle: bool,
    always_cpf: bool,
    always_pis: bool,
    always_cnpj: bool,
    always_cei: bool,
    always_rg: bool,
    only_cpf: bool,
    only_pis: bool,
    only_cnpj: bool,
    only_cei: bool,
    only_rg: bool,
    include_issuer: bool,
    only_document: bool,
    surnames_path: str | Path,
    locations_path: str | Path,
    save_to_jsonl: str | None,
    all_data: bool,
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
        save_to_jsonl: Path to save generated samples as JSONL
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

        if only_document:
            # Document-only generation with proper state handling
            for _ in range(actual_qty):
                documents = {}

                # Generate location first to get proper state for RG
                state_name, state_abbr, city_name = location_sampler.get_state_and_city()

                # Generate all requested documents
                if always_cpf or only_cpf:
                    documents['cpf'] = doc_sampler.generate_cpf()
                if always_pis or only_pis:
                    documents['pis'] = doc_sampler.generate_pis()
                if always_cnpj or only_cnpj:
                    documents['cnpj'] = doc_sampler.generate_cnpj()
                if always_cei or only_cei:
                    documents['cei'] = doc_sampler.generate_cei()
                if always_rg or only_rg:
                    documents['rg'] = f'{doc_sampler.generate_rg(state_abbr, include_issuer)}'

                results.append((None, None, documents))

        elif any([only_cpf, only_pis, only_cnpj, only_cei, only_rg]):
            # Handle document-only generation with proper state handling
            for _ in range(actual_qty):
                documents = {}

                # No need to reload location data - already loaded once at the beginning

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

        elif return_only_name or only_surname or only_middle:
            # Name-only generation
            for _ in range(actual_qty):
                documents = {}
                name_components = None

                # No need to reload location data - already loaded once at the beginning

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
        else:
            # Full sample generation with location, name, and documents
            for _ in range(actual_qty):
                documents = {}

                # No need to reload location data - already loaded once at the beginning

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

        # Modify the results to include state_info for each sample
        results_with_state_info = []

        # For all types of generation
        for i in range(actual_qty):
            # Generate a new state and city for each sample
            state_name, state_abbr, city_name = location_sampler.get_state_and_city()

            # Get a random CEP for the city
            cep = location_sampler._get_random_cep_for_city(city_name)
            formatted_cep = location_sampler._format_cep(cep, not cep_without_dash)

            # Format the full location string with CEP
            # The parse_result function expects the format: "city - cep, state (abbr)"
            location_str = f'{city_name} - {formatted_cep}, {state_name} ({state_abbr})'

            # Get the corresponding result
            location, name_components, documents = results[i]

            # Add to the new results list with state_info
            results_with_state_info.append((location_str, name_components, documents))

        # Convert results to dictionary format
        parsed_results = []
        for location, name_components, documents in results_with_state_info:
            # Parse the location string to extract city, state, and CEP
            result_dict = parse_result(location, name_components, documents, state_info=None)
            parsed_results.append(result_dict)

        # Save to JSONL if requested
        if save_to_jsonl:
            if isinstance(parsed_results, list):
                save_to_jsonl_file(parsed_results, save_to_jsonl)
            else:
                save_to_jsonl_file([parsed_results], save_to_jsonl)

        return parsed_results[0] if actual_qty == 1 else parsed_results

    except Exception as e:
        # Re-raise the exception with more context
        raise RuntimeError(f'Error generating samples: {e}') from e
