"""Input checks shared by the standalone audio commands; no model dependencies."""
import importlib.util
import math
import pathlib
import re
import shutil


def records(path, fields):
    import json
    rows = json.loads(pathlib.Path(path).read_text())
    if not isinstance(rows, list) or not rows:
        raise ValueError("input must be a nonempty JSON list")
    ids = set()
    for row in rows:
        if not isinstance(row, dict) or any(key not in row for key in fields):
            raise ValueError("each input row must contain " + ", ".join(fields))
        ident = row["id"]
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", ident):
            raise ValueError("ids must be 1-64 letters, digits, underscores or hyphens, starting with a letter or digit")
        if ident in ids:
            raise ValueError("duplicate line id")
        ids.add(ident)
    return rows


def finite(value, label, minimum=0, maximum=None, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(label + " must be a finite number")
    if value < minimum or (positive and value == minimum) or (maximum is not None and value > maximum):
        raise ValueError(label + " is outside the allowed range")
    return value


def child(folder, name):
    folder = pathlib.Path(folder).resolve()
    path = folder / name
    if path.is_symlink() or path.resolve().parent != folder:
        raise ValueError("audio file must stay inside its selected folder")
    return path


def dependencies(modules=(), commands=()):
    missing = [m for m in modules if importlib.util.find_spec(m) is None]
    missing += [c for c in commands if shutil.which(c) is None]
    if missing:
        raise ValueError("missing dependencies: " + ", ".join(missing))
