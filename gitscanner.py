import asyncio
import aiohttp
from itertools import islice
import sys
import re
import time
from colorama import Fore, Style
from colorama import init as color_init

color_init()


def log(line, output_type="info"):
    types = {
        "found": f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} {line}",
        "warning": f"{Fore.YELLOW}{Style.BRIGHT}[?]{Style.RESET_ALL} {line}",
        "error": f"{Fore.RED}{Style.BRIGHT}[!]{Style.RESET_ALL} {line}",
        "info": f"{Fore.WHITE}{Style.BRIGHT}[*]{Style.RESET_ALL} {line}",
    }
    print(types.get(output_type,
          f"{Fore.WHITE}{Style.BRIGHT}[*]{Style.RESET_ALL} {line}"))


async def write_to_found(url):
    try:
        with open('found.txt', 'a') as file:
            file.write(url + '\n')
    except FileNotFoundError:
        with open('found.txt', 'w') as file:
            await file.write(url + '\n')


def chunked_iterable(iterable, chunk_size):
    it = iter(iterable)
    while True:
        chunk = list(islice(it, chunk_size))
        if not chunk:
            break
        yield chunk


async def get_fetch_results(domains):
    attributes = []
    max_workers = 150

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
               'AppleWebKit/537.11 (KHTML, like Gecko) '
               'Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}

    tcp_connection = aiohttp.TCPConnector(limit=max_workers)
    async with aiohttp.ClientSession(connector=tcp_connection, headers=headers, timeout=25) as session:
        for chunk in chunked_iterable(domains, max_workers):
            results = await do_fetch_tasks(chunk, session)
            attributes.extend(results)
    await tcp_connection.close()
    return attributes


class timeit_context(object):
    def __init__(self):
        self.initial = None

    def __enter__(self):
        self.initial = time.time()

    def __exit__(self, type_arg, value, traceback):
        elapsed_time = time.time() - self.initial
        if elapsed_time >= 60:
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            log('Total time elapsed: {} hours, {} minutes, {:.2f} seconds'.format(
                int(hours), int(minutes), seconds))
        else:
            log('Total time elapsed: {:.2f} seconds'.format(elapsed_time))


async def do_fetch_tasks(domains, session):
    tasks = []

    for domain in domains:
        task = asyncio.ensure_future(fetch(domain, session=session))
        tasks.append(task)

    return await asyncio.gather(*tasks, return_exceptions=True)


async def fetch(domain, session):
    for protocol in ["https://", "http://", "https://www.", "http://www."]:
        await asyncio.sleep(.250)
        try:
            async with session.get(f"{protocol}{domain}/.git/config", timeout=25, ssl=False) as response:
                if response.status == 200:
                    response_text = await response.text()
                    if response_text.startswith("["):
                        log(
                            f"[FOUND] python3 gitdumper.py {protocol}{domain} {domain}", "found")
                        # check for .env
                        async with session.get(f"{protocol}{domain}/.env", timeout=25, ssl=False) as env_response:
                            if env_response.status == 200:
                                log(
                                    f"[FOUND - ENV] {protocol}{domain}/.env", "found")
                                await write_to_found(f"{protocol}{domain}/.env")
                                return 998
                        await write_to_found(f"{protocol}{domain}/.git/config")
                        return 999
                    return response.status
                else:
                    log(f"[{response.status}] {protocol}{domain}/.git/config")
                    return response.status
        except aiohttp.ClientOSError as error_message:
            if 'Header value is too long' in str(error_message):
                log(
                    f"[WARNING] Header value too long: {error_message}. URL : {protocol}{domain}", "warning")
            elif 'nodename nor servname provided, or not known' in str(error_message):
                log(
                    f"[ERROR] Cannot connect to host {protocol}{domain}: {error_message}", "error")
            else:
                log(
                    f"[WARNING] A ClientOSError occurred for domain {protocol}{domain}: {error_message}", "warning")
            return {}

        except Exception as e:
            log(
                f"[ERROR] An unexpected error occurred for domain {protocol}{domain}: {e}", "error")
            return {}

if __name__ == "__main__":
    with open(sys.argv[1], 'r') as file:
        domains = [domain.strip() for domain in open(
            sys.argv[1], 'r').readlines() if re.match(r"^[a-zA-Z0-9.-]+$", domain.strip())]
        print(
            f'Successfully read input file: {sys.argv[1]} with {len(domains)}/{len(file.readlines())} lines.')

    with timeit_context():
        loop = asyncio.get_event_loop()
        fetch_attributes = loop.run_until_complete(
            get_fetch_results(domains))
        empty_dicts_count = sum(
            1 for item in fetch_attributes if isinstance(item, dict) and not item)
        non_empty_sets = len(domains) - empty_dicts_count

        print(fetch_attributes)
        log(f"Found {fetch_attributes.count(999)+fetch_attributes.count(998)} git directories.", "found")
        log(f"Found {fetch_attributes.count(998)} .env files.", "found")
        log(f"200 Statuses: {fetch_attributes.count(200)}", "warning")
        log(f"403 Statuses: {fetch_attributes.count(403)}", "warning")
        log(f"404 Statuses: {fetch_attributes.count(404)}", "warning")
        log(
            f"Number of non-empty sets: {non_empty_sets}/{len(domains)}")
