from pathlib import Path
from os.path import basename
import sys


if len(sys.argv) == 2:
    repo_path = sys.argv[1]
    for branch in Path(repo_path).glob(".git/refs/heads/*"):
        print(basename(branch))
