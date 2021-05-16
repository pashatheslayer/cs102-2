import hashlib
import operator
import os
import pathlib
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        return struct.pack(
            f"!10I20sH{len(self.name)}s{8 - (62 + len(self.name)) % 8}x",
            self.ctime_s,
            self.ctime_n,
            self.mtime_s,
            self.mtime_n,
            self.dev,
            self.ino & 0xFFFFFFFF,
            self.mode,
            self.uid,
            self.gid,
            self.size,
            self.sha1,
            self.flags,
            self.name.encode(),
        )

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        data_list = list(struct.unpack(f"!10I20sH{len(data) - 62}s", data))
        data_list[-1] = data_list[-1].strip(b"\00").decode()
        return GitIndexEntry(*data_list)


def read_index(gitdir: pathlib.Path) -> tp.List[GitIndexEntry]:
    if not (gitdir / "index").exists():
        return []
    with (gitdir / "index").open("rb") as f:
        data = f.read()
    last_position = 12
    result = []
    i_range = struct.unpack("!I", data[8:12])[0]
    for i in range(i_range):
        last_position2 = data.index(b"\00", last_position + 62)
        while data[last_position2] != 0 or (last_position2 - 11) % 8 != 0:
            last_position2 += 1
        result.append(GitIndexEntry.unpack(data[last_position : last_position2 + 1]))
        last_position = last_position2 + 1
    return result


def write_index(gitdir: pathlib.Path, entries: tp.List[GitIndexEntry]) -> None:
    data = b"DIRC" + struct.pack("!2I", 2, len(entries))
    for entry in entries:
        data += entry.pack()
    data += hashlib.sha1(data).digest()
    with (gitdir / "index").open("wb") as f:
        f.write(data)


def ls_files(gitdir: pathlib.Path, details: bool = False) -> None:
    entries = read_index(gitdir)
    if details:
        for entry in entries:
            print(f"{entry.mode:o} {entry.sha1.hex()} 0\t{entry.name}")
    else:
        for entry in entries:
            print(entry.name)


def update_index(
    gitdir: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True
) -> None:
    entries = read_index(gitdir)
    for path in paths:
        with path.open("rb") as f:
            data = f.read()
        stat = path.stat()
        hash = hash_object(data, "blob", write=True)
        entries.append(
            GitIndexEntry(
                ctime_s=int(stat.st_ctime),
                ctime_n=0,
                mtime_s=int(stat.st_mtime),
                mtime_n=0,
                dev=stat.st_dev,
                ino=stat.st_ino,
                mode=stat.st_mode,
                uid=stat.st_uid,
                gid=stat.st_gid,
                size=stat.st_size,
                sha1=bytes.fromhex(hash),
                flags=len(path.name),
                name=str(path),
            )
        )
    if write:
        write_index(gitdir, sorted(entries, key=lambda x: x.name))