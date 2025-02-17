from pathlib import Path
from os.path import basename
import zlib
import sys


if len(sys.argv) == 2:
    repo_path = sys.argv[1]
    for branch in Path(repo_path).glob(".git/refs/heads/*"):
        print(basename(branch))
if len(sys.argv) == 3:

    repo_path, branch = sys.argv[1], sys.argv[2]

    with open(Path(repo_path) / f".git/refs/heads/{branch}", "rb") as f:
        commit_id = f.read().strip().decode()

    while commit_id:
        commit_path = Path(repo_path) / f".git/objects/{commit_id[:2]}/{commit_id[2:]}"

        with open(commit_path, "rb") as f:
            obj = zlib.decompress(f.read())

        _, _, body = obj.partition(b"\x00")
        lines = body.decode().split("\n")

        for line in lines:
            if line.startswith("tree "):
                tree_id = line.split()[1]
                break

        print(f"TREE for commit {commit_id}")

        tree_path = Path(repo_path) / f".git/objects/{tree_id[:2]}/{tree_id[2:]}"

        with open(tree_path, "rb") as f:
            obj = zlib.decompress(f.read())

        _, _, tree_body = obj.partition(b"\x00")

        while tree_body:
            entry, _, tree_body = tree_body.partition(b"\x00")
            mode, name = entry.split()
            sha1, tree_body = tree_body[:20], tree_body[20:]

            mode = mode.decode()
            name = name.decode()
            sha1_hex = sha1.hex()

            if mode.startswith("10"):
                print(f"blob {sha1_hex}    {name}")
            elif mode.startswith("40"):
                print(f"tree {sha1_hex}    {name}")

        commit_id = None
        for line in lines:
            if line.startswith("parent "):
                commit_id = line.split()[1]
                break
