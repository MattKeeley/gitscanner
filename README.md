# GitScanner

<h1 align="center">
<br>
<img src=/files/dumpsterfire.png height="375" border="2px solid #555">
<br>
GitScanner
</h1>

## WHAT

GitScanner is a Python script that scans a list of domains to check if they have exposed Git repositories. It does this by attempting to access the `.git/config` file on each domain using both HTTP and HTTPS protocols. If a valid Git configuration file is found, it will be added to the "found.txt" file.

## HOW TO USE

`GitScanner` requires **Python 3+**. Python 2 is not supported.

This tool is run in 2 parts, usage is shown below:

```console
Usage:
    ./python3 gitscanner.py input_file.txt
Install Dependencies:
    pip3 install aiohttp
```

Running `gitscanner.py` will output the results to the screen, and in a found.txt file. After `gitscanner.py` is finished running, you will need to run this bash 1-liner:

```bash
while read -r line; do
  domain=$(echo "$line" | sed -E 's/^(http|https):\/\/([^/]+).*\/\.git\/config$/\2/')
  python3 gitdumper.py "${line%.git/config}" "$domain"
done < found.txt
```

What does this 1-liner do? Well it uses the `gitdumper.py` file created by [arthaud](https://github.com/arthaud/git-dumper/blob/master/git_dumper.py) to download all of the files in the git repository for each domain in found.txt.

_(NOT REQUIRED)_ If you would like to manually get the `.git` repository for a specific domain, you can use gitdumper independently like so:

```console
Usage:
    ./python3 gitdumper.py https://domain.com folder
Install Dependencies:
    pip3 install PySocks requests beautifulsoup4 dulwich
```

## DISCLAIMER

> This tool is only for testing and academic purposes and can only be used where
> strict consent has been given. Do not use it for illegal purposes! It is the
> end user’s responsibility to obey all applicable local, state and federal laws.
> Developers assume no liability and are not responsible for any misuse or damage
> caused by this tool and software.

## LICENSE

This project is licensed under the Creative Commons Zero v1.0 Universal - see the [LICENSE](LICENSE) file for details
