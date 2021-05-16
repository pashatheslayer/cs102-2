import os
import pathlib
import typing as tp


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    dirs_name = os.getenv("GIT_DIR", ".pyvcs")
    workdir = pathlib.Path(workdir)
    while pathlib.Path(workdir.absolute().root) != workdir.absolute():
        if (workdir / dirs_name).is_dir():
            return workdir / dirs_name
        workdir = workdir.parent
    if (workdir / dirs_name).is_dir():
        return workdir / dirs_name
    raise Exception("Not a git repository")


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    dirs_name = os.getenv("GIT_DIR", ".pyvcs")
    workdir = pathlib.Path(workdir)
    if workdir.is_file():
        raise Exception(f"{workdir} is not a directory")
    os.makedirs(workdir / dirs_name / "refs" / "heads", exist_ok=True)
    os.makedirs(workdir / dirs_name / "refs" / "tags", exist_ok=True)
    (workdir / dirs_name / "objects").mkdir()
    with (workdir / dirs_name / "config").open("w") as f:
        f.write(
            "[core]\n\trepositoryformatversion = 0\n\tfilemode = true\n\tbare = false\n\tlogallrefupdates = false\n",
        )
    with (workdir / dirs_name / "HEAD").open("w") as f:
        f.write("ref: refs/heads/master\n")
    with (workdir / dirs_name / "description").open("w") as f:
        f.write("Unnamed pyvcs repository.\n")
    return workdir / dirs_name
