from pathlib import Path
from os.path import basename
import zlib
import sys


repo_path = sys.argv[1]
if len(sys.argv) == 2:
    for branch in Path(repo_path).glob(".git/refs/heads/*"):
        print(basename(branch))
if len(sys.argv) == 3:
    branch = sys.argv[2]

    with open(Path(repo_path) / f".git/refs/heads/{branch}", "rb") as f:
        commit_id = f.read().strip().decode()

    commit_path = Path(repo_path) / f".git/objects/{commit_id[:2]}/{commit_id[2:]}"

    with open(commit_path, "rb") as f:
        obj = zlib.decompress(f.read())

    _, _, body = obj.partition(b"\x00")
    lines = body.decode().split("\n")

    for line in lines:
        if line.startswith("tree ") or line.startswith("parent "):
            print(line)
        elif line.startswith("author ") or line.startswith("committer "):
            parts = line.split()
            print(" ".join(parts[:3]))
        elif not line.strip():
            print()
            break

    message_started = False
    for line in lines:
        if message_started and line.strip():
            print(line)
        if not message_started and not line.strip():
            message_started = True
