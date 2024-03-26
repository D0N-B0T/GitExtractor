# Git Extractor

This Python script is based on the work of [Internetwache's GitTools](https://github.com/internetwache/GitTools/), with modifications to consolidate functionality into a single script.

## Credits

This script is heavily inspired by and borrows code from [Internetwache's GitTools](https://github.com/internetwache/GitTools/), a collection of tools for interacting with Git repositories.

## Description

The Git Extractor allows users to extract files and commits from a remote Git repository. It traverses the repository's history, downloading files and commits locally. The script is written in Python and is easily customizable.

## How to Use

1. Clone the repository.
2. Run the script with the URL of the target Git repository's `.git` folder as an argument.
3. Extracted files and commits will be saved locally in a directory named after the target repository.

## Features

- Download files from the repository.
- Extract commit information and files.
- Easy to use and customize.

## Usage

```bash
python git_extractor.py http://target.tld/.git/
```
Note: Ensure you have Python installed on your system.


## License

This project is licensed under the MIT License - see the LICENSE file for details.

Feel free to contribute and report issues!




