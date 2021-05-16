import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    data_reformatted = (fmt + " " + str(len(data))).encode() + b"\00" + data
    data_hash_sum = hashlib.sha1(data_reformatted).hexdigest()
    if write:
        gitdir = repo_find()
        (gitdir / "objects" / data_hash_sum[:2]).mkdir(exist_ok=True)
        with (gitdir / "objects" / data_hash_sum[:2] / data_hash_sum[2:]).open(
            "wb"
        ) as f:
            f.write(zlib.compress(data_reformatted))
    return data_hash_sum


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    if (4 <= len(obj_name) <= 40) is False:
        raise Exception(f"Not a valid object name {obj_name}")
    result = []
    for file in (gitdir / "objects" / obj_name[:2]).glob(f"{obj_name[2:]}*"):
        result.append(obj_name[:2] + file.name)
    if not result:
        raise Exception(f"Not a valid object name {obj_name}")
    return result


def find_object(obj_name: str, gitdir: pathlib.Path) -> str:
    # PUT YOUR CODE HERE
    ...


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    with (gitdir / "objects" / sha[:2] / sha[2:]).open("rb") as f:
        data = zlib.decompress(f.read())
    return data.split(b" ")[0].decode(), data.split(b"\00", maxsplit=1)[1]


def read_tree(data: bytes) -> tp.List[tp.Tuple[int, str, str]]:
    arr = []
    while data:
        before_sha_ind = data.index(b"\00")
        mode, name = map(lambda x: x.decode(), data[:before_sha_ind].split(b" "))
        sha = data[before_sha_ind + 1 : before_sha_ind + 21]
        arr.append((int(mode), sha.hex(), name))
        data = data[before_sha_ind + 21 :]
    return arr


def cat_file(obj_name: str, pretty: bool = True) -> None:
    fmt, data = read_object(obj_name, repo_find())
    if fmt == "blob" or fmt == "commit":
        print(data.decode())
    else:
        for i in read_tree(data):
            print(f"{i[0]:06}", "tree" if i[0] == 40000 else "blob", i[1] + "\t" + i[2])


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    # PUT YOUR CODE HERE
    ...


def commit_parse(raw: bytes, start: int = 0, dct=None):
    data: tp.Dict[str, tp.Any] = {"message": []}
    arr = raw.decode().split("\n")
    for line in arr:
        if line.startswith(("tree", "parent", "author", "committer")):
            name, val = line.split(" ", maxsplit=1)
            data[name] = val
        else:
            data["message"].append(line)
    return data
