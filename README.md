# Git Scanner

Git Scanner is a tool designed to scan a list of domains for exposed `.git` directories. It consists of two programs: `gitscanner` for scanning and `gitdumper` for extracting Git repositories.

## `gitscanner`

`gitscanner` is used to scan a list of domains for exposed `.git` directories. It checks each domain for Git repository information and reports any findings.

### Usage

```bash
python3 gitscanner.py input_file
```

- `input_file` should contain a list of domains, one per line.

Example:

```bash
python3 gitscanner.py domains.txt
```

## `gitdumper`

Once you have identified exposed Git directories using `gitscanner`, you can use `gitdumper` to clone and extract the contents of these repositories.

### Usage

```bash
while read -r line; do
domain=$(echo "$line" | sed -E 's/^(http|https)://([^/]+).*/.git/config$/2/')
  python3 gitdumper.py "${line%.git/config}" "$domain"
done < found.txt

```

This one-liner reads each line from `found.txt` produced by gitscanner.py, then extracts the domain, and uses `gitdumper` to clone the Git repository.

---

**Note**: Ensure that you have both `gitscanner` and `gitdumper` set up and configured properly before using them. Be responsible and use these tools only for legitimate and authorized purposes.

For more information and contributions, please visit the respective repositories:

- [gitdumper](https://github.com/arthaud/git-dumper/blob/master/git_dumper.py)

