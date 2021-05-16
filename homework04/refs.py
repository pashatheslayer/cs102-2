import pathlib
import typing as tp


def update_ref(
    gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str
) -> None:
    with (gitdir / ref).open("w") as file:
        file.write(new_value)


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    # PUT YOUR CODE HERE
    ...


def ref_resolve(gitdir: pathlib.Path, refname: str) -> str:
    if refname == "HEAD" and not is_detached(gitdir):
        return resolve_head(gitdir)  # type: ignore
    if (gitdir / refname).exists():
        with (gitdir / refname).open() as f:
            return f.read().strip()
    return None  # type: ignore


def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    with (gitdir / "HEAD").open() as f:
        return ref_resolve(gitdir, f.read().strip().split()[1])


def is_detached(gitdir: pathlib.Path) -> bool:
    try:
        get_ref(gitdir)
    except IndexError:
        return True
    return False


def get_ref(gitdir: pathlib.Path) -> str:
    with (gitdir / "HEAD").open() as f:
        return f.read().strip().split()[1]