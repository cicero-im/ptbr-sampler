import asyncio
import contextlib
import json
import subprocess
import sys
from typing import Any


async def get_cep_data(cep: str) -> list[dict[str, Any]]:
    """
    Retrieves address information for a single CEP using cep_service.js
    which directly imports from the cep-promise package.

    Args:
        cep: A CEP (string).

    Returns:
        A list of dictionaries containing the address information.
        Returns a list with an error dictionary if there is an issue after 100 retry attempts.
    """
    # Ensure cep is a string
    cep = str(cep)

    max_retries = 100
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Use the cep_service.js directly
            process = await asyncio.create_subprocess_exec(
                'node',
                'src/utils/cep_service.js',
                cep,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_output = stderr.decode('utf-8').strip() if stderr else 'No error details available'
                retry_count += 1
                if retry_count >= max_retries:
                    return [{'error': f'Error calling cep_service.js after {max_retries} retries: {error_output}', 'cep': cep}]
                await asyncio.sleep(0.01)  # Small delay between retries
                continue  # Skip to next iteration

            result = json.loads(stdout.decode('utf-8'))

            # Ensure result is always a list
            if not isinstance(result, list):
                return [result]
            return result

        except subprocess.CalledProcessError as e:
            retry_count += 1
            if retry_count >= max_retries:
                return [{'error': f'Error calling cep_service.js after {max_retries} retries: {e}', 'cep': cep}]
            await asyncio.sleep(0.01)  # Small delay between retries

        except json.JSONDecodeError as e:
            retry_count += 1
            if retry_count >= max_retries:
                return [{'error': f'Error decoding JSON after {max_retries} retries: {e}', 'cep': cep}]
            await asyncio.sleep(0.01)  # Small delay between retries

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                return [{'error': f'Unexpected error after {max_retries} retries: {e!s}', 'cep': cep}]
            await asyncio.sleep(0.01)  # Small delay between retries


async def workers_for_multiple_cep(ceps: list[str], max_workers: int = 10) -> list[dict[str, Any]]:
    """
    Process multiple CEPs concurrently using a worker pool.

    Args:
        ceps: List of CEP strings to process
        max_workers: Maximum number of concurrent workers

    Returns:
        List of dictionaries containing address information for each CEP
    """
    # Use worker pool approach for individual processing
    queue = asyncio.Queue()
    # Keep track of CEPs being processed to handle timeouts
    in_progress = set()
    worker_timeout = 15  # 15 seconds timeout for workers

    # Add all CEPs to the queue
    for cep in ceps:
        await queue.put(cep)

    # Results container with mapping to preserve order
    results_dict = {}

    # Worker function that processes CEPs from the queue
    async def worker():
        while not queue.empty():
            try:
                # Get a CEP from the queue
                cep = await queue.get()

                # Skip if already being processed by another worker
                if cep in in_progress:
                    queue.task_done()
                    continue

                # Mark as in-progress
                in_progress.add(cep)

                try:
                    # Process the CEP with timeout
                    task = asyncio.create_task(get_cep_data(cep))
                    try:
                        result = await asyncio.wait_for(task, timeout=worker_timeout)
                        # Store the result with the CEP as key to preserve order
                        results_dict[cep] = result[0] if result else {'error': 'Empty result', 'cep': cep}
                    except TimeoutError:
                        # If timeout occurs, cancel the task and put CEP back in queue
                        task.cancel()
                        with contextlib.suppress(asyncio.CancelledError):
                            await task
                        # Put back in queue only if not yet processed successfully
                        if cep not in results_dict:
                            await queue.put(cep)
                            print(f'Worker timeout for CEP {cep}, retrying...')
                finally:
                    # Remove from in-progress set
                    in_progress.discard(cep)

                # Mark task as done
                queue.task_done()
            except Exception as e:
                # Handle any exceptions in the worker
                if 'cep' in locals():
                    results_dict[cep] = {'error': f'Worker error processing CEP: {e!s}', 'cep': cep}
                    in_progress.discard(cep)
                queue.task_done()

    # Create worker tasks
    tasks = []
    for _ in range(min(max_workers, len(ceps))):
        task = asyncio.create_task(worker())
        tasks.append(task)

    # Wait for the queue to be fully processed
    await queue.join()

    # Cancel any remaining worker tasks
    for task in tasks:
        task.cancel()

    # Wait for all tasks to be cancelled
    await asyncio.gather(*tasks, return_exceptions=True)

    # Convert results dict back to list in the original order
    return [results_dict.get(cep, {'error': 'CEP processing failed', 'cep': cep}) for cep in ceps]


async def display_cep_info(data):
    """Display CEP information in a formatted way."""
    # Ensure data is a list
    if not isinstance(data, list):
        data = [data]

    for cep_info in data:
        if 'error' in cep_info:
            print(f'Error: {cep_info["error"]}')
        else:
            print(f'CEP: {cep_info.get("cep", "N/A")}')
            print(f'State: {cep_info.get("state", "N/A")}')
            print(f'City: {cep_info.get("city", "N/A")}')
            print(f'Neighborhood: {cep_info.get("neighborhood", "N/A")}')
            print(f'Street: {cep_info.get("street", "N/A")}')
            print(f'Service: {cep_info.get("service", "N/A")}')
            print()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ceps = sys.argv[1:]

        async def main():
            # If there's only one CEP, use get_cep_data directly
            if len(ceps) == 1:
                data = await get_cep_data(ceps[0])
                await display_cep_info(data)
            # Otherwise use the worker pool for multiple CEPs
            else:
                data = await workers_for_multiple_cep(ceps)
                await display_cep_info(data)

        asyncio.run(main())
