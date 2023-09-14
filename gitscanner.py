import sys
import aiohttp
import asyncio
import aiohttp


def write_to_found(url):
    try:
        with open('found.txt', 'a') as file:
            file.write(url + '\n')
    except FileNotFoundError:
        # If the file doesn't exist, create it
        with open('found.txt', 'w') as file:
            file.write(url + '\n')


async def check_website(domain, protocol):
    retries = 0
    while retries < 1:
        async with aiohttp.ClientSession() as session:
            url = f"{protocol}://{domain}/.git/config"
            try:
                # print(f'Scanning domain: {domain}')
                async with session.get(url, allow_redirects=False, ssl=True) as response:
                    print(f'url: {url}, response: {response.status}')
                    if response.status == 200:
                        text = await response.text()
                        if text.startswith('['):
                            print(
                                f"[FOUND] python3 git_dumper.py {url.strip('/.git/config')} {domain}")
                            write_to_found(url)
                        break
                    elif protocol == 'https':
                        protocol = 'http'  # Try HTTP if HTTPS failed
                        continue
                    else:
                        break  # Request failed with HTTP, exit the retry loop
            except Exception as e:
                # print(f"Error accessing {url}: {e}")
                retries += 1
                await asyncio.sleep(2)


async def main():
    if len(sys.argv) != 2:
        print("Usage: python3 gitscanner.py input_file")
        return

    with open(sys.argv[1], 'r') as file:
        domains = [line.strip() for line in file.readlines()]
        print(f'Read input file: {sys.argv[1]}')

    protocols = ['https', 'http']
    tasks = [check_website(domain, protocol)
             for domain in domains for protocol in protocols]
    for future in asyncio.as_completed(tasks):
        try:
            await future
        except asyncio.TimeoutError:
            print("A task timed out.")

if __name__ == "__main__":
    asyncio.run(main())
