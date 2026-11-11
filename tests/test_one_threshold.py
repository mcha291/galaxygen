"""The frame's one threshold is one computation (S95, Audit VI F-3B-5; register #217, discharged at S92).

#217: ``/api/bright``'s table published ``threshold`` as ``10.0 ** np.asarray(grid)`` (an array power, a CPU-dispatched
loop) and the tile answered ``l_min_used`` as a scalar power of the same grid value; on one runner the two parted by an
ulp. S92 made both read ``v6_tiles.grid_threshold`` (``math.pow``, element by element). The discharge's only check is
the machine-pinned (3, milky_way) case of ``test_v6b_points``, which shows bits on the machine that runs it, not the
code path. This file reads the source (``ast``, no model run), in the manner of ``tests/test_ordered_products.py``:
both tables' ``threshold`` column and the tile's ``l_min_used`` come from ``grid_threshold``, ``grid_threshold`` is
the scalar power, and nowhere under ``model/galaxy/api`` or ``stages/bright.py`` is a power of ten taken of the
luminosity grid as an array. A return of the array power fails it, on any machine.
"""

from __future__ import annotations

import ast
from pathlib import Path

GALAXY = Path(__file__).resolve().parents[1] / "model" / "galaxy"
TILES = GALAXY / "api" / "v6_tiles.py"
GRID_NAMES = {"LOG_L_GRID", "grid", "log_l"}
# (file under model/galaxy, the exponent's source) -> why this power of ten reading a grid-like name is no threshold.
ALLOWED = {
    ("api/service.py", "res.log_l"): (
        "the render's resolved l_min: bright.resolve's log_l is math.log10 of the REQUESTED l_min (a Python float "
        "scalar), not a grid threshold - no table publishes it"),
    ("stages/bright.py", "log_l"): (
        "the bright catalogue's per-star luminosities (bright_star_luminosity), drawn values, not a threshold"),
}


def _call_name(node: ast.AST) -> str:
    f = node.func if isinstance(node, ast.Call) else node
    parts = []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    if isinstance(f, ast.Name):
        parts.append(f.id)
    return ".".join(reversed(parts))


def _is_ten(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and float(node.value) == 10.0


def _mentions_grid(node: ast.AST) -> bool:
    return any((isinstance(n, ast.Name) and n.id in GRID_NAMES) or (isinstance(n, ast.Attribute) and n.attr in GRID_NAMES)
               for n in ast.walk(node))


def _scalar(node: ast.AST) -> bool:
    """A scalar exponent: ``float(...)``, or a subscript by a constant index (``LOG_L_GRID[0]``)."""
    if isinstance(node, ast.Call) and _call_name(node) == "float":
        return True
    return isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, int)


def array_powers_of_the_grid(source: str) -> list[tuple[int, str]]:
    """(line, exponent's source) where a power of ten (``10 ** x``, ``np.power(10, x)``, ``np.float_power``, ``pow``,
    ``math.pow``) is taken of an exponent that reads the luminosity grid (a name in ``GRID_NAMES``) and is not a
    scalar form."""
    found = []
    for node in ast.walk(ast.parse(source)):
        exponent = None
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow) and _is_ten(node.left):
            exponent = node.right
        elif isinstance(node, ast.Call) and _call_name(node).split(".")[-1] in {"power", "float_power", "pow"} \
                and len(node.args) == 2 and _is_ten(node.args[0]):
            exponent = node.args[1]
        if exponent is not None and _mentions_grid(exponent) and not _scalar(exponent):
            found.append((node.lineno, ast.unparse(exponent)))
    return found


def _functions(tree: ast.AST) -> dict[str, ast.FunctionDef]:
    return {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def test_the_scanner_finds_an_array_power_of_the_grid():
    src = (
        "import math\nimport numpy as np\n"
        "def f(grid):\n"
        "    a = 10.0 ** np.asarray(grid)\n"
        "    b = np.power(10.0, _bright.LOG_L_GRID)\n"
        "    c = 10 ** log_l\n"
        "    d = 10.0 ** LOG_L_GRID[0]\n"
        "    e = math.pow(10.0, float(grid[3]))\n"
        "    g = 10.0 ** other\n"
    )
    assert [line for line, _ in array_powers_of_the_grid(src)] == [4, 5, 6]


def test_217_both_tables_and_the_tile_read_one_threshold_function():
    tree = ast.parse(TILES.read_text(encoding="utf-8"))
    fns = _functions(tree)
    # grid_threshold is the scalar power, element by element: math.pow, no ** and no array power.
    body = fns["grid_threshold"]
    calls = {_call_name(n) for n in ast.walk(body) if isinstance(n, ast.Call)}
    assert "math.pow" in calls, calls
    assert not any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.Pow) for n in ast.walk(body))
    # The tables: every ("threshold", x) pair's x is grid_threshold(...), in both tables' functions.
    owners = {}
    for name, fn in fns.items():
        for n in ast.walk(fn):
            if isinstance(n, ast.Tuple) and len(n.elts) == 2 and isinstance(n.elts[0], ast.Constant) \
                    and n.elts[0].value == "threshold":
                owners.setdefault(name, []).append(_call_name(n.elts[1]) if isinstance(n.elts[1], ast.Call) else ast.dump(n.elts[1]))
    assert owners == {"_table": ["grid_threshold"], "_cells_table": ["grid_threshold"]}, owners
    # The tile: snap_up returns grid_threshold's value, and every `used` (the tile's l_min_used) is snap_up's.
    returns = [n for n in ast.walk(fns["snap_up"]) if isinstance(n, ast.Return)]
    assert len(returns) == 1 and any(isinstance(n, ast.Call) and _call_name(n) == "grid_threshold" for n in ast.walk(returns[0]))
    used_from = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "used" or
                                             isinstance(t, ast.Tuple) and any(isinstance(e, ast.Name) and e.id == "used" for e in t.elts)
                                             for t in n.targets):
            used_from.append(_call_name(n.value) if isinstance(n.value, ast.Call) else ast.dump(n.value))
    assert used_from and set(used_from) == {"snap_up"}, used_from
    published = [n for n in ast.walk(tree) if isinstance(n, ast.Dict)
                 and any(isinstance(k, ast.Constant) and k.value == "l_min_used" for k in n.keys)]
    assert len(published) == 1
    value = published[0].values[[k.value if isinstance(k, ast.Constant) else None for k in published[0].keys].index("l_min_used")]
    assert isinstance(value, ast.Name) and value.id == "used", ast.dump(value)


def test_217_no_array_power_of_ten_of_the_luminosity_grid():
    paths = sorted((GALAXY / "api").glob("*.py")) + [GALAXY / "stages" / "bright.py"]
    assert len(paths) > 5
    seen, problems = set(), {}
    for p in paths:
        rel = p.relative_to(GALAXY).as_posix()
        for line, exponent in array_powers_of_the_grid(p.read_text(encoding="utf-8")):
            seen.add((rel, exponent))
            if (rel, exponent) not in ALLOWED:
                problems.setdefault(rel, []).append((line, exponent))
    assert seen >= set(ALLOWED), f"ALLOWED rows whose site is gone: {sorted(set(ALLOWED) - seen)} - remove them"
    assert not problems, (
        f"an array power of ten of the luminosity grid at {problems}: a CPU-dispatched loop whose last bits are the "
        "machine's (#217) - take the threshold from v6_tiles.grid_threshold")
