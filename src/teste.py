import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from src.br_location_class import BrazilianLocationSampler
from src.br_name_class import BrazilianNameSampler, NameComponents, TimePeriod
from src.document_sampler import DocumentSampler

app = typer.Typer(help='Brazilian Location, Name and Document Sampler CLI')
console = Console()

# Define options at module level
DEFAULT_QTY = typer.Option(1, '--qty', '-q', help='Number of samples to generate')
CITY_ONLY = typer.Option(False, '--city-only', '-c', help='Return only city names')
STATE_ABBR_ONLY = typer.Option(False, '--state-abbr-only', '-sa', help='Return only state abbreviations')
STATE_FULL_ONLY = typer.Option(False, '--state-full-only', '-sf', help='Return only full state names')
JSON_PATH = typer.Option(
    'data/cities_with_ceps.json',  # Updated default path
    '--json-path',
    '-j',
    help='Path to the cities and CEPs data JSON file',
)
NAMES_PATH = typer.Option(
    'data/names_data.json',
    '--names-path',
    '-n',
    help='Path to the first names data JSON file',
)
MIDDLE_NAMES_PATH = typer.Option(
    'data/middle_names.json',
    '--middle-names-path',
    '-m',
    help='Path to the middle names JSON file',
)
SURNAMES_PATH = typer.Option('data/surnames_data.json', '--surnames-path', '-sp', help='Path to the surnames JSON file')
CEP_WITHOUT_DASH = typer.Option(False, '--cep-without-dash', '-nd', help='Return CEP without dash')
ONLY_CEP = typer.Option(False, '--only-cep', '-oc', help='Return only CEP')
TIME_PERIOD = typer.Option(TimePeriod.UNTIL_2010, '--time-period', '-t', help='Time period for name sampling')
RETURN_ONLY_NAME = typer.Option(False, '--return-only-name', '-n', help='Return only the name without location')
NAME_RAW = typer.Option(False, '--name-raw', '-r', help='Return names in raw format (all caps)')
ONLY_SURNAME = typer.Option(False, '--only-surname', '-s', help='Return only surname')
TOP_40 = typer.Option(False, '--top-40', '-t40', help='Use only top 40 surnames')
WITH_ONLY_ONE_SURNAME = typer.Option(False, '--one-surname', '-os', help='Return only one surname instead of two')
ALWAYS_MIDDLE = typer.Option(False, '--always-middle', '-am', help='Always include a middle name')
ONLY_MIDDLE = typer.Option(False, '--only-middle', '-om', help='Return only middle name')
ALWAYS_CPF = typer.Option(True, '--always-cpf', '-ac', help='Always include CPF')
ALWAYS_PIS = typer.Option(False, '--always-pis', '-ap', help='Always include PIS')
ALWAYS_CNPJ = typer.Option(False, '--always-cnpj', '-acn', help='Always include CNPJ')
ALWAYS_CEI = typer.Option(False, '--always-cei', '-ace', help='Always include CEI')
ALWAYS_RG = typer.Option(True, '--always-rg', '-ar', help='Always include RG')
ONLY_CPF = typer.Option(False, '--only-cpf', '-oc', help='Return only CPF')
ONLY_PIS = typer.Option(False, '--only-pis', '-op', help='Return only PIS')
ONLY_CNPJ = typer.Option(False, '--only-cnpj', '-ocn', help='Return only CNPJ')
ONLY_CEI = typer.Option(False, '--only-cei', '-oce', help='Return only CEI')
ONLY_RG = typer.Option(False, '--only-rg', '-or', help='Return only RG')
INCLUDE_ISSUER = typer.Option(True, '--include-issuer', '-ii', help='Include issuer in RG (default: True)')
ONLY_DOCUMENT = typer.Option(False, '--only-document', '-od', help='Return only documents')


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


def _format_document_lines(doc: dict[str, str]) -> list[str]:
    """Format document information into display lines.

    This function processes document information and formats it into
    a list of strings suitable for display. It handles special
    formatting for RG numbers which include state information.

    Args:
        doc: Dictionary containing document information
             Keys can be: 'cpf', 'pis', 'cnpj', 'cei', 'rg'

    Returns:
        List of formatted document strings
    """
    doc_lines = []

    # Handle documents in a specific order
    if 'cpf' in doc:
        doc_lines.append(f'CPF: {doc["cpf"]}')
    if 'rg' in doc:
        if '/' in doc['rg']:  # RG with state information
            rg_num, state = doc['rg'].split('/')
            doc_lines.append(f'RG: {rg_num} ({state})')
        else:
            doc_lines.append(f'RG: {doc["rg"]}')
    if 'pis' in doc:
        doc_lines.append(f'PIS: {doc["pis"]}')
    if 'cnpj' in doc:
        doc_lines.append(f'CNPJ: {doc["cnpj"]}')
    if 'cei' in doc:
        doc_lines.append(f'CEI: {doc["cei"]}')

    return doc_lines


def create_results_table(
    results: list[tuple[str, NameComponents, dict[str, str]] | str],
    title: str,
    return_only_name: bool = False,
    only_location: bool = False,
    only_document: bool = False,
    sanitize: bool = False,
) -> Table:
    """Create a formatted table for displaying Brazilian sample data results.

    This function creates a rich, formatted table that handles complex Brazilian name patterns,
    including compound names, surnames with prefixes, and various document types.

    Args:
        results: List of tuples containing:
                - location string
                - NameComponents object (first_name, middle_name, surname)
                - Dictionary of documents
                OR a plain string for simple results
        title: The title to display at the top of the table
        return_only_name: If True, displays only name information
        only_location: If True, displays only location information
        only_document: If True, displays only document information
        sanitize: If True, uses English column names instead of Portuguese

    Returns:
        Rich Table object formatted according to specifications

    The table structure adapts based on the content type:
    - Full display: ID, Name, Middle Name, Surname, Location, Documents
    - Name only: ID, Name, Middle Name, Surname
    - Location only: ID, Location
    - Document only: ID, Documents
    """
    table = Table(
        title=title,
        show_lines=True,  # Add horizontal lines between rows
        show_edge=True,  # Show table edges
        padding=(0, 1),  # Add minimal padding for readability
        title_style='bold yellow',
        border_style='blue',
    )

    # Add columns based on display mode
    table.add_column('Id', justify='right', style='blue', no_wrap=True)

    if only_document:
        table.add_column('Documentos' if not sanitize else 'Documents', style='yellow', overflow='fold', width=50)
    else:
        if not only_location:
            # Name columns
            table.add_column('Nome' if not sanitize else 'Name', style='yellow', width=20)
            table.add_column('Nome do Meio' if not sanitize else 'Middle', style='yellow', width=20)
            table.add_column('Sobrenome' if not sanitize else 'Surname', style='yellow', width=30)

        if not return_only_name:
            # Location and documents columns
            table.add_column('Local' if not sanitize else 'Place', style='yellow', width=40)
            table.add_column('Documentos' if not sanitize else 'Documents', style='yellow', overflow='fold', width=50)

    # Process and add rows
    for idx, result in enumerate(results, 1):
        if isinstance(result, tuple):
            location, name_components, documents = result

            # Format documents string
            doc_lines = _format_document_lines(documents)
            doc_str = '\n'.join(doc_lines)

            if only_document:
                table.add_row(str(idx), doc_str)
            else:
                row = [str(idx)]

                # Add name components if not location-only
                if not only_location and name_components:
                    row.extend([name_components.first_name, name_components.middle_name or '', name_components.surname])

                # Add location and documents if not name-only
                if not return_only_name:
                    row.extend([location or '', doc_str])

                table.add_row(*row)
        else:
            # Handle plain string results
            table.add_row(str(idx), result)

    return table


@app.command()
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
    Returns:
        List of tuples containing (location, name_components, documents)

    Raises:
        typer.Exit: If an error occurs during execution
    """

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
            for _ in range(qty):
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
            for _ in range(qty):
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
            for _ in range(qty):
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

        # Convert results to dictionary format when used as a function
        parsed_results = [
            parse_result(
                location, name_components, documents, state_info=(state_name, state_abbr, city_name) if 'state_name' in locals() else None
            )
            for location, name_components, documents in results
        ]

        return parsed_results[0] if qty == 1 else parsed_results

    except Exception as e:
        console.print(f'[red]Error: {e!s}[/red]')
        raise typer.Exit(code=1) from e


def main() -> None:
    """Entry point for the CLI application.

    This function serves as the main entry point for the command-line interface.
    It initializes and runs the Typer application with all configured commands
    and options.
    """
    app()


if __name__ == '__main__':
    main()
