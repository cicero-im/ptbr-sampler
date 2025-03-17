def sample(
    qty: int = DEFAULT_QTY,
    city_only: bool = CITY_ONLY,
    state_abbr_only: bool = STATE_ABBR_ONLY,
    state_full_only: bool = STATE_FULL_ONLY,
    only_cep: bool = ONLY_CEP,
    cep_without_dash: bool = CEP_WITHOUT_DASH,
    time_period: TimePeriod = TIME_PERIOD,
    return_only_name: bool = RETURN_ONLY_NAME,
    name_raw: bool = NAME_RAW,
    json_path: Path = JSON_PATH,
    names_path: Path = NAMES_PATH,
    middle_names_path: Path = MIDDLE_NAMES_PATH,
    only_surname: bool = ONLY_SURNAME,
    top_40: bool = TOP_40,
    with_only_one_surname: bool = WITH_ONLY_ONE_SURNAME,
    always_middle: bool = ALWAYS_MIDDLE,
    only_middle: bool = ONLY_MIDDLE,
    always_cpf: bool = ALWAYS_CPF,
    always_pis: bool = ALWAYS_PIS,
    always_cnpj: bool = ALWAYS_CNPJ,
    always_cei: bool = ALWAYS_CEI,
    always_rg: bool = ALWAYS_RG,
    only_cpf: bool = ONLY_CPF,
    only_pis: bool = ONLY_PIS,
    only_cnpj: bool = ONLY_CNPJ,
    only_cei: bool = ONLY_CEI,
    only_rg: bool = ONLY_RG,
    include_issuer: bool = INCLUDE_ISSUER,
    only_document: bool = ONLY_DOCUMENT,
    surnames_path: Path = SURNAMES_PATH,
    locations_path: Path = LOCATIONS_PATH,
    save_to_jsonl: str = SAVE_TO_JSONL,
    all_data: bool = ALL_DATA,
) -> list[tuple[str, NameComponents, dict[str, str]]]:
    """Generate random Brazilian samples with comprehensive information.

    This function generates random Brazilian location, name, and document samples
    based on the provided parameters. It handles various combinations of output
    formats and ensures proper state handling for document generation.

    Args:
        qty: Number of samples to generate
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
        List of tuples containing (location, name_components, documents)

    Raises:
        typer.Exit: If an error occurs during execution
    """

    try:
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

        # Call the sample function from the sampler module
        parsed_results = sampler_sample(
            qty=qty,
            city_only=city_only,
            state_abbr_only=state_abbr_only,
            state_full_only=state_full_only,
            only_cep=only_cep,
            cep_without_dash=cep_without_dash,
            time_period=time_period,
            return_only_name=return_only_name,
            name_raw=name_raw,
            json_path=json_path,
            names_path=names_path,
            middle_names_path=middle_names_path,
            only_surname=only_surname,
            top_40=top_40,
            with_only_one_surname=with_only_one_surname,
            always_middle=always_middle,
            only_middle=only_middle,
            always_cpf=always_cpf,
            always_pis=always_pis,
            always_cnpj=always_cnpj,
            always_cei=always_cei,
            always_rg=always_rg,
            only_cpf=only_cpf,
            only_pis=only_pis,
            only_cnpj=only_cnpj,
            only_cei=only_cei,
            only_rg=only_rg,
            include_issuer=include_issuer,
            only_document=only_document,
            surnames_path=surnames_path,
            locations_path=locations_path,
            all_data=all_data,
        )

        # Save to JSONL if requested
        if save_to_jsonl:
            if isinstance(parsed_results, list):
                save_to_jsonl_file(parsed_results, save_to_jsonl)
            else:
                save_to_jsonl_file([parsed_results], save_to_jsonl)

        # Convert parsed results back to the format expected by create_results_table
        results = []
        if isinstance(parsed_results, list):
            for result in parsed_results:
                # Create a NameComponents object
                name_components = NameComponents(
                    result['name'], result['middle_name'] if result['middle_name'] else None, result['surnames']
                )

                # Create a documents dictionary
                documents = {}
                if result['cpf']:
                    documents['cpf'] = result['cpf']
                if result['rg']:
                    documents['rg'] = result['rg']
                if result.get('pis'):
                    documents['pis'] = result['pis']
                if result.get('cnpj'):
                    documents['cnpj'] = result['cnpj']
                if result.get('cei'):
                    documents['cei'] = result['cei']

                # Create a location string
                location = None
                if result['city'] or result['state'] or result['state_abbr'] or result['cep']:
                    # Reconstruct location based on what's available
                    if only_cep and result['cep']:
                        location = result['cep']
                    elif city_only and result['city']:
                        location = result['city']
                    elif state_abbr_only and result['state_abbr']:
                        location = result['state_abbr']
                    elif state_full_only and result['state']:
                        location = result['state']
                    else:
                        # Try to reconstruct full location
                        city_part = result['city']
                        if result['cep']:
                            city_part += f' - {result["cep"]}'

                        state_part = result['state']
                        if result['state_abbr']:
                            state_part += f' ({result["state_abbr"]})'

                        if city_part and state_part:
                            location = f'{city_part}, {state_part}'
                        elif city_part:
                            location = city_part
                        elif state_part:
                            location = state_part

                results.append((location, name_components, documents))
        else:
            # Single result
            name_components = NameComponents(
                parsed_results['name'], parsed_results['middle_name'] if parsed_results['middle_name'] else None, parsed_results['surnames']
            )

            documents = {}
            if parsed_results['cpf']:
                documents['cpf'] = parsed_results['cpf']
            if parsed_results['rg']:
                documents['rg'] = parsed_results['rg']
            if parsed_results.get('pis'):
                documents['pis'] = parsed_results['pis']
            if parsed_results.get('cnpj'):
                documents['cnpj'] = parsed_results['cnpj']
            if parsed_results.get('cei'):
                documents['cei'] = parsed_results['cei']

            location = None
            if parsed_results['city'] or parsed_results['state'] or parsed_results['state_abbr'] or parsed_results['cep']:
                # Reconstruct location based on what's available
                if only_cep and parsed_results['cep']:
                    location = parsed_results['cep']
                elif city_only and parsed_results['city']:
                    location = parsed_results['city']
                elif state_abbr_only and parsed_results['state_abbr']:
                    location = parsed_results['state_abbr']
                elif state_full_only and parsed_results['state']:
                    location = parsed_results['state']
                else:
                    # Try to reconstruct full location
                    city_part = parsed_results['city']
                    if parsed_results['cep']:
                        city_part += f' - {parsed_results["cep"]}'

                    state_part = parsed_results['state']
                    if parsed_results['state_abbr']:
                        state_part += f' ({parsed_results["state_abbr"]})'

                    if city_part and state_part:
                        location = f'{city_part}, {state_part}'
                    elif city_part:
                        location = city_part
                    elif state_part:
                        location = state_part

            results.append((location, name_components, documents))

        # Determine appropriate title based on generation mode
        if only_document:
            doc_types = []
            if only_cpf:
                doc_types.append('CPF')
            if only_pis:
                doc_types.append('PIS')
            if only_cnpj:
                doc_types.append('CNPJ')
            if only_cei:
                doc_types.append('CEI')
            if only_rg:
                doc_types.append('RG')
            title = f'Random Brazilian {"and ".join(doc_types)} Numbers'
        elif only_middle:
            title = 'Random Brazilian Middle Names'
        elif only_surname:
            title = f'Random Brazilian Surnames{" (Top 40)" if top_40 else ""}{" (Single)" if with_only_one_surname else ""}'
        elif return_only_name:
            title = (
                f'Random Brazilian Names{" with Middle Names" if always_middle else ""}'
                f'{" with Single" if with_only_one_surname else " with"} Surname'
                f' ({time_period.value}{"- Top 40" if top_40 else ""})'
            )
        elif city_only:
            title = 'Random Brazilian City Samples'
        elif state_abbr_only:
            title = 'Random Brazilian State Abbreviation Samples'
        elif state_full_only:
            title = 'Random Brazilian State Name Samples'
        elif only_cep:
            title = f'Random Brazilian CEP Samples{"" if cep_without_dash else " with dash"}'
        elif all_data:
            title = 'Complete Brazilian Data Samples'
        else:
            title = 'Random Brazilian Location and Document Samples'

        # Create and display the results table
        table = create_results_table(
            results=results,
            title=title,
            return_only_name=return_only_name or only_surname or only_middle,
            only_location=any([city_only, state_abbr_only, state_full_only, only_cep]),
            only_document=only_document,
        )
        console.print(table)

        return parsed_results

    except Exception as e:
        console.print(f'[red]Error: {e!s}[/red]')
        raise typer.Exit(code=1) from e
