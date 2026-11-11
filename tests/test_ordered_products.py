"""No BLAS-backed product comes back onto a draw path unseen (S93, #218; the review's first concern, the gate's M1).

A BLAS or LAPACK product sums in an order that follows its thread count and its per-CPU kernel, so its last bits are
the machine's, and a seed names one galaxy whatever the machine (#216's ruling). S93 made every such product on a
draw path under ``model/galaxy`` a sum the model orders itself (``core.special.ordered_product``). This test reads
the source (``ast``, no model run) for every matrix-product operator (``@``, ``@=``) and every call of ``dot``,
``matmul``, ``tensordot``, ``inner``, ``vdot``, ``einsum``, ``polyfit`` or anything under ``linalg``, and holds the
sites to an explicit list, each row with its reason. A new site fails it, and so does a listed site that is gone.
Rows are keyed on (file, enclosing function, kind, count), not on lines, so an unrelated edit does not break it.
It does not show bits: the pair of runs at two thread counts in separate processes is not built here (#218).
"""

from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

GALAXY = Path(__file__).resolve().parents[1] / "model" / "galaxy"
NAMES = {"dot", "matmul", "tensordot", "inner", "vdot", "einsum", "polyfit"}

_EINSUM = "einsum: numpy's own loops, not BLAS - it does not follow the thread count; another CPU's bits not shown"
_SPEC = "specs/: a spec's measurement of the model's output, not the model; no draw reads it"
_POLYFIT = "polyfit (LAPACK lstsq on n x 2): a published gradient or scale length; the specs' windows read it, no stage"

# (file under model/galaxy, enclosing function or Class.method, kind, count) -> the reason it may stay unordered.
ALLOWED: dict[tuple[str, str, str, int], str] = {
    ("api/v6_clouds.py", "continuous_share", "linalg.solve", 1): (
        "the 32 x 32 solve (LAPACK): a published weight, not a draw; it feeds bounded_share's raw != clip(raw), "
        "the header's held_rings, which flips only for a node within an ulp of 0 or 1 - left unordered, named (#218)"),
    ("api/v6_tiles.py", "table_of", "einsum", 1): _EINSUM,
    ("stages/bright.py", "BrightGalaxy.__init__", "einsum", 1): _EINSUM + " (mass_cell -> count_cell -> the draw)",
    ("stages/photometry.py", "population_light", "einsum", 1): _EINSUM,
    ("stages/remnants.py", "budget", "einsum", 1): _EINSUM,
    ("stages/chemistry.py", "migrate", "@", 2): "chemistry.migrate: no caller in the model",
    ("stages/spectra.py", "_build_factors", "@", 2): (
        "spectra's response tables: published arrays; read only by a lit > 0 test that cannot flip"),
    ("stages/spectra.py", "_through", "@", 1): (
        "spectra's object / stellar response: published arrays; read only by a lit > 0 test that cannot flip"),
    ("stages/chemistry.py", "gradient", "polyfit", 1): _POLYFIT,
    ("stages/nebular.py", "luminosity_function_slope", "polyfit", 1): _POLYFIT,
    ("stages/nebular.py", "nii_halpha_gradient", "polyfit", 1): _POLYFIT,
    ("stages/sfh.py", "fit_scale_length", "polyfit", 1): _POLYFIT,
    ("specs/clustering.py", "Annulus.contains", "einsum", 1): _SPEC,
    ("specs/performance.py", "catalogue_cost", "polyfit", 1): _SPEC,
    ("specs/spec.py", "evaluate", "polyfit", 1): _SPEC,
    ("specs/spectrum.py", "fit_broken", "@", 1): _SPEC,
    ("specs/spectrum.py", "fit_broken", "linalg.lstsq", 1): _SPEC,
    ("specs/spectrum.py", "fit_power_law", "@", 2): _SPEC,
    ("specs/spectrum.py", "fit_power_law", "linalg.lstsq", 1): _SPEC,
}


class _Scan(ast.NodeVisitor):
    def __init__(self) -> None:
        self.stack: list[str] = []
        self.sites: list[tuple[str, str, int]] = []  # (function, kind, line)

    def _scope(self, node) -> None:
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_FunctionDef = visit_AsyncFunctionDef = visit_ClassDef = _scope

    def _add(self, node, kind: str) -> None:
        self.sites.append((".".join(self.stack) or "<module>", kind, node.lineno))

    def visit_BinOp(self, node) -> None:
        if isinstance(node.op, ast.MatMult):
            self._add(node, "@")
        self.generic_visit(node)

    def visit_AugAssign(self, node) -> None:
        if isinstance(node.op, ast.MatMult):
            self._add(node, "@=")
        self.generic_visit(node)

    def visit_Call(self, node) -> None:
        f, parts = node.func, []
        while isinstance(f, ast.Attribute):
            parts.append(f.attr)
            f = f.value
        if isinstance(f, ast.Name):
            parts.append(f.id)
        parts.reverse()
        if parts and "linalg" in parts[:-1]:
            self._add(node, "linalg." + parts[-1])
        elif parts and parts[-1] in NAMES:
            self._add(node, parts[-1])
        self.generic_visit(node)


def scan(source: str) -> list[tuple[str, str, int]]:
    s = _Scan()
    s.visit(ast.parse(source))
    return s.sites


def test_the_scanner_finds_each_kind():
    src = (
        "import numpy as np\n"
        "def f(a, b):\n"
        "    c = a @ b\n"
        "    c @= b\n"
        "    np.dot(a, b); a.dot(b); np.matmul(a, b); np.tensordot(a, b, 1); np.inner(a, b); np.vdot(a, b)\n"
        "    np.einsum('ij,jk', a, b); np.polyfit(a, b, 1); np.linalg.solve(a, b); np.linalg.lstsq(a, b)\n"
        "class K:\n"
        "    def g(self, a):\n"
        "        return a @ a\n"
    )
    found = Counter((fn, kind) for fn, kind, _ in scan(src))
    assert found == Counter({
        ("f", "@"): 1, ("f", "@="): 1, ("f", "dot"): 2, ("f", "matmul"): 1, ("f", "tensordot"): 1,
        ("f", "inner"): 1, ("f", "vdot"): 1, ("f", "einsum"): 1, ("f", "polyfit"): 1,
        ("f", "linalg.solve"): 1, ("f", "linalg.lstsq"): 1, ("K.g", "@"): 1,
    })


def test_no_unlisted_blas_product_under_model_galaxy():
    seen: Counter = Counter()
    lines: dict[tuple[str, str, str], list[int]] = {}
    for path in sorted(GALAXY.rglob("*.py")):
        rel = path.relative_to(GALAXY).as_posix()
        for fn, kind, line in scan(path.read_text(encoding="utf-8")):
            seen[(rel, fn, kind)] += 1
            lines.setdefault((rel, fn, kind), []).append(line)
    found = {(rel, fn, kind, n) for (rel, fn, kind), n in seen.items()}
    new = sorted(found - set(ALLOWED))
    gone = sorted(set(ALLOWED) - found)
    problems = [
        f"model/galaxy/{rel} line(s) {lines[(rel, fn, kind)]}, in {fn}: {n} x {kind} not in ALLOWED - a BLAS-backed "
        f"product's bits follow the thread count and the CPU (#218, #216): sum it with core.special.ordered_product, "
        f"or, if no draw reads it, add its row to ALLOWED in tests/test_ordered_products.py with the reason"
        for rel, fn, kind, n in new
    ] + [
        f"ALLOWED row {row} names a site that is gone (or whose count changed): remove or correct the row"
        for row in gone
    ]
    assert not problems, "\n".join(problems)
