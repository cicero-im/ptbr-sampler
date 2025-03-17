import os
import sys
from datetime import timedelta, timezone
from pathlib import Path

import typer
from loguru import logger
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table

from src.br_name_class import NameComponents, TimePeriod

# Import the sample function from the sampler module
from src.sampler import sample as sampler_sample

# Configure loguru logger
# Remove default handler
logger.remove()
# Add custom handler with Brasilia timezone (UTC-3)
brasilia_tz = timezone(timedelta(hours=-3))
log_format = '<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{file}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
logger.configure(handlers=[{'sink': sys.stderr, 'format': log_format, 'colorize': True}])

app = typer.Typer(help='Brazilian Location, Name and Document Sampler CLI')
console = Console()

# Define options at module level organized by panels
# Basic options
DEFAULT_QTY = typer.Option(1, '--qty', '-q', help='Number of samples to generate', rich_help_panel='Basic Options')
ALL_DATA = typer.Option(False, '--all', '-a', help='Include all possible data in the generated samples', rich_help_panel='Basic Options')
SAVE_TO_JSONL = typer.Option(None, '--save-to-jsonl', '-sj', help='Save generated samples to a JSONL file', rich_help_panel='Basic Options')
APPEND_TO_JSONL = typer.Option(True, '--append', '-ap', help='Append to JSONL file instead of overwriting', rich_help_panel='Basic Options')
# New convenience options
BATCH = typer.Option(
    None,
    '--batch',
    '-b',
    help='Maximum samples per batch before saving (processes large requests in smaller chunks)',
    rich_help_panel='Basic Options',
)
EASY = typer.Option(
    None, '--easy', '-e', help='Easy mode with integer qty (enables API calls, all data, and auto-saves)', rich_help_panel='Basic Options'
)

# Location options
CITY_ONLY = typer.Option(False, '--city-only', '-c', help='Return only city names', rich_help_panel='Location Options')
STATE_ABBR_ONLY = typer.Option(
    False, '--state-abbr-only', '-sa', help='Return only state abbreviations', rich_help_panel='Location Options'
)
STATE_FULL_ONLY = typer.Option(False, '--state-full-only', '-sf', help='Return only full state names', rich_help_panel='Location Options')
ONLY_CEP = typer.Option(False, '--only-cep', '-oc', help='Return only CEP', rich_help_panel='Location Options')
CEP_WITHOUT_DASH = typer.Option(False, '--cep-without-dash', '-nd', help='Return CEP without dash', rich_help_panel='Location Options')
MAKE_API_CALL = typer.Option(
    False,
    '--make-api-call',
    '-mac',
    help='Make API calls to retrieve real CEP data instead of generating synthetic address data',
    rich_help_panel='Location Options',
)

# Name options
TIME_PERIOD = typer.Option(
    TimePeriod.UNTIL_2010, '--time-period', '-t', help='Time period for name sampling', rich_help_panel='Name Options'
)
RETURN_ONLY_NAME = typer.Option(
    False, '--return-only-name', '-rn', help='Return only the name without location', rich_help_panel='Name Options'
)
NAME_RAW = typer.Option(False, '--name-raw', '-r', help='Return names in raw format (all caps)', rich_help_panel='Name Options')
ONLY_SURNAME = typer.Option(False, '--only-surname', '-s', help='Return only surname', rich_help_panel='Name Options')
TOP_40 = typer.Option(False, '--top-40', '-t40', help='Use only top 40 surnames', rich_help_panel='Name Options')
WITH_ONLY_ONE_SURNAME = typer.Option(
    False, '--one-surname', '-os', help='Return only one surname instead of two', rich_help_panel='Name Options'
)
ALWAYS_MIDDLE = typer.Option(False, '--always-middle', '-am', help='Always include a middle name', rich_help_panel='Name Options')
ONLY_MIDDLE = typer.Option(False, '--only-middle', '-om', help='Return only middle name', rich_help_panel='Name Options')

# Document options
ONLY_DOCUMENT = typer.Option(False, '--only-document', '-od', help='Return only documents', rich_help_panel='Document Options')
ALWAYS_CPF = typer.Option(True, '--always-cpf', '-ac', help='Always include CPF', rich_help_panel='Document Options')
ALWAYS_PIS = typer.Option(False, '--always-pis', '-ap', help='Always include PIS', rich_help_panel='Document Options')
ALWAYS_CNPJ = typer.Option(False, '--always-cnpj', '-acn', help='Always include CNPJ', rich_help_panel='Document Options')
ALWAYS_CEI = typer.Option(False, '--always-cei', '-ace', help='Always include CEI', rich_help_panel='Document Options')
ALWAYS_RG = typer.Option(True, '--always-rg', '-ar', help='Always include RG', rich_help_panel='Document Options')
ALWAYS_PHONE = typer.Option(True, '--always-phone', '-aph', help='Always include phone number', rich_help_panel='Local e Fone')
ONLY_CPF = typer.Option(False, '--only-cpf', '-ocpf', help='Return only CPF', rich_help_panel='Document Options')
ONLY_PIS = typer.Option(False, '--only-pis', '-op', help='Return only PIS', rich_help_panel='Document Options')
ONLY_CNPJ = typer.Option(False, '--only-cnpj', '-ocn', help='Return only CNPJ', rich_help_panel='Document Options')
ONLY_CEI = typer.Option(False, '--only-cei', '-oce', help='Return only CEI', rich_help_panel='Document Options')
ONLY_RG = typer.Option(False, '--only-rg', '-or', help='Return only RG', rich_help_panel='Document Options')
ONLY_FONE = typer.Option(False, '--only-fone', '-of', help='Return only phone number', rich_help_panel='Local e Fone')
INCLUDE_ISSUER = typer.Option(
    True, '--include-issuer', '-ii', help='Include issuer in RG (default: True)', rich_help_panel='Document Options'
)

# Data source options
JSON_PATH = typer.Option(
    'src/data/cities_with_ceps.json',
    '--json-path',
    '-j',
    help='Path to the cities and CEPs data JSON file',
    rich_help_panel='Data Source Options',
)
NAMES_PATH = typer.Option(
    'src/data/names_data.json', '--names-path', '-np', help='Path to the first names data JSON file', rich_help_panel='Data Source Options'
)
MIDDLE_NAMES_PATH = typer.Option(
    'src/data/middle_names.json',
    '--middle-names-path',
    '-mnp',
    help='Path to the middle names JSON file',
    rich_help_panel='Data Source Options',
)
SURNAMES_PATH = typer.Option(
    'src/data/surnames_data.json', '--surnames-path', '-sp', help='Path to the surnames JSON file', rich_help_panel='Data Source Options'
)
LOCATIONS_PATH = typer.Option(
    'src/data/locations_data.json',
    '--locations-path',
    '-lp',
    help='Path to the locations data JSON file',
    rich_help_panel='Data Source Options',
)


def _format_document_lines(doc: dict[str, str]) -> list[str]:
    """Format document information into display lines.

    This function processes document information and formats it into
    a list of strings suitable for display. It handles special
    formatting for RG numbers which include state information.

    Args:
        doc: Dictionary containing document information
             Keys can be: 'cpf', 'pis', 'cnpj', 'cei', 'rg', 'phone'

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
    if 'phone' in doc:
        doc_lines.append(f'Telefone: {doc["phone"]}')

    return doc_lines


def create_results_table(
    results: list[tuple[str, NameComponents, dict[str, str], dict[str, str]] | str],
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
                - Dictionary of address data (street, neighborhood, building_number)
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
        header_style='bold blue',
        expand=True,
        collapse_padding=True,
    )

    # Add columns based on display mode
    table.add_column('Id', justify='right', style='yellow', no_wrap=True, width=5)

    if only_document:
        table.add_column('Documentos' if not sanitize else 'Documents', style='yellow', overflow='fold', max_width=50)
    else:
        if not only_location:
            # Name columns
            table.add_column('Nome' if not sanitize else 'Name', style='yellow', width=21)
            table.add_column('Nome do Meio' if not sanitize else 'Middle', style='yellow', width=22)
            table.add_column('Sobrenome' if not sanitize else 'Surname', style='yellow', width=23)

        if not return_only_name:
            # Location and documents columns
            table.add_column('Local' if not sanitize else 'Place', style='yellow', width=30)
            table.add_column('Logradouro' if not sanitize else 'Address', style='yellow', width=50)
            table.add_column('Documentos' if not sanitize else 'Documents', style='yellow', overflow='fold', width=28)

    # Process and add rows
    for idx, result in enumerate(results, 1):
        if isinstance(result, tuple):
            if len(result) == 4:  # New format with address data
                location, name_components, documents, address_data = result
            else:  # Old format without address data
                location, name_components, documents = result
                address_data = {}

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
                    # Combine address data into a single logradouro field
                    street = address_data.get('street', '')
                    neighborhood = address_data.get('neighborhood', '')
                    building_number = address_data.get('building_number', '')

                    # Format the logradouro: street, building_number - neighborhood
                    logradouro = ''
                    if street:
                        logradouro = street
                        if building_number:
                            logradouro += f', {building_number}'
                        if neighborhood:
                            logradouro += f' - {neighborhood}'
                    elif neighborhood:
                        logradouro = neighborhood
                        if building_number:
                            logradouro += f', {building_number}'

                    # Add phone number to logradouro if available
                    phone = address_data.get('phone', '')
                    if phone:
                        if logradouro:
                            logradouro += f'\nTelefone: {phone}'
                        else:
                            logradouro = f'Telefone: {phone}'

                    row.extend([location or '', logradouro, doc_str])

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
    make_api_call: bool = MAKE_API_CALL,
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
    always_phone: bool = ALWAYS_PHONE,
    only_cpf: bool = ONLY_CPF,
    only_pis: bool = ONLY_PIS,
    only_cnpj: bool = ONLY_CNPJ,
    only_cei: bool = ONLY_CEI,
    only_rg: bool = ONLY_RG,
    only_fone: bool = ONLY_FONE,
    include_issuer: bool = INCLUDE_ISSUER,
    only_document: bool = ONLY_DOCUMENT,
    surnames_path: Path = SURNAMES_PATH,
    locations_path: Path = LOCATIONS_PATH,
    save_to_jsonl: str = SAVE_TO_JSONL,
    all_data: bool = ALL_DATA,
    batch: int = BATCH,
    easy: int = EASY,
    append_to_jsonl: bool = APPEND_TO_JSONL,
) -> None:
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
        batch: Maximum number of samples per batch before saving to file
        easy: Easy mode with integer qty (enables API calls, all data, and auto-saves)
        append_to_jsonl: Append to JSONL file instead of overwriting

    Raises:
        typer.Exit: If an error occurs during execution
    """

    try:
        # Process easy mode if specified
        if easy is not None:
            console.print('[bold green]Easy mode enabled[/bold green]')
            qty = easy
            make_api_call = True
            all_data = True
            always_phone = True
            save_to_jsonl = 'output/output.jsonl'

            # Ensure output directory exists
            output_dir = os.path.dirname(save_to_jsonl)
            if output_dir and not os.path.exists(output_dir):
                console.print(f'[yellow]Creating output directory: {output_dir}[/yellow]')
                os.makedirs(output_dir)

        # Set up batch processing if enabled
        use_batches = False
        batch_size = 0

        if batch is not None and batch > 0 and save_to_jsonl:
            batch_size = min(batch, qty)  # Ensure batch size doesn't exceed total quantity
            use_batches = batch_size < qty  # Only use batches if we have multiple batches

            if use_batches:
                console.print(f'[bold blue]Processing {qty} samples in batches of {batch_size}[/bold blue]')
            else:
                console.print(f'[bold blue]Batch size ({batch_size}) equals or exceeds total quantity ({qty})[/bold blue]')

        # Show configuration summary for batch or easy modes
        if batch is not None or easy is not None:
            config_summary = [
                f'Quantity: {qty}',
                f'Make API call: [{"green" if make_api_call else "red"}]{make_api_call}[/]',
                f'All data: [{"green" if all_data else "red"}]{all_data}[/]',
                f'Always phone: [{"green" if always_phone else "red"}]{always_phone}[/]',
            ]
            if save_to_jsonl:
                save_mode = '[green]append[/]' if append_to_jsonl else '[yellow]overwrite[/]'
                config_summary.append(f'Save to: [cyan]{save_to_jsonl}[/] ({save_mode})')
                if use_batches:
                    config_summary.append(f'Batch size: [cyan]{batch_size}[/] samples')

            console.print('[bold]Configuration:[/bold]')
            for item in config_summary:
                console.print(f'  [cyan]•[/cyan] {item}')
            console.print()

        # Process in batches or as a single run
        all_results = []

        if use_batches:
            # Use batched processing with progress display
            with Progress(
                SpinnerColumn(),
                TextColumn('[bold blue]{task.description}'),
                BarColumn(complete_style='green', finished_style='green'),
                TaskProgressColumn(),
                TextColumn('{task.fields[status]}'),
                console=console,
            ) as progress:
                main_task = progress.add_task('[green]Generating samples...', total=qty, status='')
                api_task = None
                if make_api_call:
                    api_task = progress.add_task('[yellow]API calls...', visible=False, total=1.0, status='')
                batch_task = progress.add_task('[cyan]Batch progress...', total=batch_size, visible=False, status='')

                # Keep track of total progress across batches
                samples_completed = 0

                # Process each batch
                first_batch = True
                while samples_completed < qty:
                    # Calculate batch size for this iteration
                    current_batch_size = min(batch_size, qty - samples_completed)

                    # Update progress displays
                    progress.update(
                        batch_task,
                        description=f'[cyan]Batch {samples_completed // batch_size + 1}/{(qty + batch_size - 1) // batch_size}...',
                        total=current_batch_size,
                        completed=0,
                        visible=True,
                    )

                    # Create a progress callback that updates both total and batch progress
                    def progress_callback(completed: int, stage: str = None) -> None:
                        # Calculate total progress
                        total_completed = min(samples_completed + completed, qty)

                        # Update total progress
                        progress.update(
                            main_task,
                            completed=total_completed,
                            status=f'[dim cyan]{stage or ""} (Batch {samples_completed // batch_size + 1})[/]',
                        )

                        # Update batch progress
                        progress.update(batch_task, completed=min(completed, current_batch_size))

                        # Update API task if relevant
                        if api_task and stage:
                            if 'API' in stage:
                                progress.update(api_task, visible=True)
                                if 'starting' in stage.lower():
                                    progress.update(api_task, completed=0.2, status='[yellow]Connecting...[/]')
                                elif 'processing' in stage.lower():
                                    progress.update(api_task, completed=0.6, status='[yellow]Processing...[/]')
                                elif 'completed' in stage.lower():
                                    progress.update(api_task, completed=1.0, status='[green]Done[/]')

                    # Process the current batch
                    batch_results = sampler_sample(
                        qty=current_batch_size,
                        q=None,
                        city_only=city_only,
                        state_abbr_only=state_abbr_only,
                        state_full_only=state_full_only,
                        only_cep=only_cep,
                        cep_without_dash=cep_without_dash,
                        make_api_call=make_api_call,
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
                        always_phone=always_phone,
                        only_cpf=only_cpf,
                        only_pis=only_pis,
                        only_cnpj=only_cnpj,
                        only_cei=only_cei,
                        only_rg=only_rg,
                        only_fone=only_fone,
                        include_issuer=include_issuer,
                        only_document=only_document,
                        surnames_path=surnames_path,
                        locations_path=locations_path,
                        save_to_jsonl=save_to_jsonl,
                        all_data=all_data,
                        progress_callback=progress_callback,
                        append_to_jsonl=(append_to_jsonl or not first_batch),  # Force append for all batches after the first
                    )

                    # Force append mode after the first batch
                    first_batch = False

                    # Save this batch's results
                    if isinstance(batch_results, list):
                        all_results.extend(batch_results)
                    else:
                        all_results.append(batch_results)

                    # Update completed count
                    samples_completed += current_batch_size

                    # Mark the batch as completed
                    progress.update(batch_task, completed=current_batch_size, status=f'[green]Completed - Saved to {save_to_jsonl}[/]')

                # All batches are complete
                progress.update(main_task, completed=qty, status='[bold green]All batches completed![/]')
                progress.update(batch_task, visible=False)
                if api_task:
                    progress.update(api_task, visible=False)

                # Show completion message
                console.print(f'\n[bold green]✓[/] {qty} samples generated successfully in {(qty + batch_size - 1) // batch_size} batches!')
                if save_to_jsonl:
                    console.print(f'[bold green]✓[/] All results saved to [cyan]{save_to_jsonl}[/]')

        else:
            # Standard processing (non-batched) with progress display for larger quantities
            with Progress(
                SpinnerColumn(),
                TextColumn('[bold blue]{task.description}'),
                BarColumn(complete_style='green', finished_style='green'),
                TaskProgressColumn(),
                TextColumn('{task.fields[status]}'),
                console=console,
            ) as progress:
                main_task = progress.add_task('[green]Generating samples...', total=qty, status='')

                # Create a task for API calls if make_api_call is true
                api_task = None
                if make_api_call:
                    api_task = progress.add_task('[yellow]API calls...', visible=False, total=1.0, status='')

                # Call the sample function with progress updates
                def progress_callback(completed: int, stage: str = None) -> None:
                    # Update the main task
                    progress.update(main_task, completed=completed, status=f'[dim cyan]{stage or ""}[/]')

                    # Update API task if relevant
                    if api_task and stage:
                        if 'API' in stage:
                            progress.update(api_task, visible=True)
                            if 'starting' in stage.lower():
                                progress.update(api_task, completed=0.2, status='[yellow]Connecting...[/]')
                            elif 'processing' in stage.lower():
                                progress.update(api_task, completed=0.6, status='[yellow]Processing...[/]')
                            elif 'completed' in stage.lower():
                                progress.update(api_task, completed=1.0, status='[green]Done[/]')

                # Call the sample function from the sampler module with all parameters
                all_results = sampler_sample(
                    qty=qty,
                    q=None,  # We don't use this alias in the CLI
                    city_only=city_only,
                    state_abbr_only=state_abbr_only,
                    state_full_only=state_full_only,
                    only_cep=only_cep,
                    cep_without_dash=cep_without_dash,
                    make_api_call=make_api_call,
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
                    always_phone=always_phone,
                    only_cpf=only_cpf,
                    only_pis=only_pis,
                    only_cnpj=only_cnpj,
                    only_cei=only_cei,
                    only_rg=only_rg,
                    only_fone=only_fone,
                    include_issuer=include_issuer,
                    only_document=only_document,
                    surnames_path=surnames_path,
                    locations_path=locations_path,
                    save_to_jsonl=save_to_jsonl,
                    all_data=all_data,
                    progress_callback=progress_callback,
                    append_to_jsonl=append_to_jsonl,
                )

                # Ensure progress is complete
                progress.update(main_task, completed=qty, status='[bold green]Completed![/]')
                if api_task:
                    progress.update(api_task, visible=False)

                # Show completion message
                console.print('\n[bold green]✓[/] Sample generation completed successfully!')
                if save_to_jsonl:
                    console.print(f'[bold green]✓[/] Results saved to [cyan]{save_to_jsonl}[/]')

        # Convert parsed results back to the format expected by create_results_table
        results = []
        if isinstance(all_results, list):
            for result in all_results:
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
                if result.get('phone'):
                    documents['phone'] = result['phone']

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

                # Create address data dictionary
                address_data = {}
                if result.get('street'):
                    address_data['street'] = result['street']
                if result.get('neighborhood'):
                    address_data['neighborhood'] = result['neighborhood']
                if result.get('building_number'):
                    address_data['building_number'] = result['building_number']
                if result.get('phone'):
                    address_data['phone'] = result['phone']

                results.append((location, name_components, documents, address_data))
        else:
            # Single result
            name_components = NameComponents(
                all_results['name'], all_results['middle_name'] if all_results['middle_name'] else None, all_results['surnames']
            )

            documents = {}
            if all_results['cpf']:
                documents['cpf'] = all_results['cpf']
            if all_results['rg']:
                documents['rg'] = all_results['rg']
            if all_results.get('pis'):
                documents['pis'] = all_results['pis']
            if all_results.get('cnpj'):
                documents['cnpj'] = all_results['cnpj']
            if all_results.get('cei'):
                documents['cei'] = all_results['cei']
            if all_results.get('phone'):
                documents['phone'] = all_results['phone']

            location = None
            if all_results['city'] or all_results['state'] or all_results['state_abbr'] or all_results['cep']:
                # Reconstruct location based on what's available
                if only_cep and all_results['cep']:
                    location = all_results['cep']
                elif city_only and all_results['city']:
                    location = all_results['city']
                elif state_abbr_only and all_results['state_abbr']:
                    location = all_results['state_abbr']
                elif state_full_only and all_results['state']:
                    location = all_results['state']
                else:
                    # Try to reconstruct full location
                    city_part = all_results['city']
                    state_part = all_results['state']
                    if all_results['cep']:
                        cep_part = all_results['cep']
                        if all_results['state_abbr'] and state_part:
                            state_abbr_part = f' ({all_results["state_abbr"]})'
                            full_location = f'{city_part}, {state_part}{state_abbr_part} - {cep_part}'
                        else:
                            full_location = f'{city_part} - {cep_part}'

                    if all_results['state_abbr']:
                        state_part += f' ({state_abbr_part})'

                    if city_part and state_part:
                        location = full_location
                    elif city_part:
                        location = city_part
                    elif state_part:
                        location = state_part

            # Create address data dictionary
            address_data = {}
            if all_results.get('street'):
                address_data['street'] = all_results['street']
            if all_results.get('neighborhood'):
                address_data['neighborhood'] = all_results['neighborhood']
            if all_results.get('building_number'):
                address_data['building_number'] = all_results['building_number']
            if all_results.get('phone'):
                address_data['phone'] = all_results['phone']

            results.append((location, name_components, documents, address_data))

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
