#!/usr/bin/env python3
"""Prepare the uv venv to move with its bundled CPython runtime in the pkg."""
from __future__ import annotations

import argparse
import os
from pathlib import Path


def relocate(root: Path, prefix: str, venv_dir: str = "venv") -> None:
    root = root.resolve(strict=True)
    env = (root / venv_dir).resolve(strict=True)
    try:
        env.relative_to(root)
    except ValueError as error:
        raise SystemExit("Virtual environment must remain inside the package root") from error
    cfg = env / "pyvenv.cfg"
    if cfg.is_symlink() or not cfg.is_file():
        raise SystemExit(f"Missing or unsafe uv virtual-environment config: {cfg}")
    bin_dir = env / "bin"
    if bin_dir.is_symlink() or not bin_dir.is_dir():
        raise SystemExit(f"Missing or unsafe virtual-environment bin directory: {bin_dir}")

    values: dict[str, str] = {}
    lines = cfg.read_text().splitlines()
    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    home = values.get("home")
    if not home:
        raise SystemExit("pyvenv.cfg has no base interpreter 'home' entry")

    home_path = Path(home).resolve(strict=True)
    search_dirs = (home_path, home_path / "bin")
    base_python = next(
        (
            candidate
            for directory in search_dirs
            for candidate in (directory / "python3.14", directory / "python3", directory / "python")
            if candidate.is_file()
        ),
        None,
    )
    if base_python is None:
        raise SystemExit(f"No Python executable found under bundled runtime home: {home_path}")
    base_bin = base_python.parent.resolve(strict=True)
    try:
        relative_base_bin = base_bin.relative_to(root)
    except ValueError as error:
        raise SystemExit(f"Python runtime is not inside package root: {base_bin}") from error

    # pyvenv.cfg uses the base interpreter directory to locate its standard
    # library. Keep it at the final immutable installation path, not build/.
    final_home = Path(prefix) / relative_base_bin
    output = []
    for line in lines:
        if line.lstrip().startswith("home ="):
            output.append(f"home = {final_home}")
        else:
            output.append(line.replace(str(root), prefix))
    cfg.write_text("\n".join(output) + "\n")

    # uv may create absolute interpreter symlinks. Point them relatively to the
    # sibling bundled runtime so the whole /opt/homeassistant tree can move.
    relative_python = os.path.relpath(base_python, bin_dir)
    for name in ("python", "python3", "python3.14"):
        link = bin_dir / name
        if link.is_symlink() or link.exists():
            if link.is_dir() and not link.is_symlink():
                raise SystemExit(f"Refusing to replace unexpected directory: {link}")
            link.unlink()
        link.symlink_to(relative_python)

    resolved = (bin_dir / "python").resolve(strict=True)
    if resolved != base_python.resolve(strict=True):
        raise SystemExit(f"Relocated interpreter link resolves incorrectly: {resolved}")
    if f"{root}/" in cfg.read_text():
        raise SystemExit("Build path leaked into pyvenv.cfg")
    print(f"Prepared relocatable venv: {env} -> {prefix} (Python {relative_python})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="Staged /opt/homeassistant directory")
    parser.add_argument("--prefix", default="/opt/homeassistant", help="Final install prefix")
    parser.add_argument("--venv-dir", default="venv", help="Venv path relative to root (default: venv)")
    args = parser.parse_args()
    relocate(args.root, args.prefix, args.venv_dir)


if __name__ == "__main__":
    main()
