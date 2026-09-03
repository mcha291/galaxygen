"""preflight: declarations reconcile within and across models; orphans; the table."""

from __future__ import annotations

import textwrap

import pytest

from galaxy.core.registry import INPUTS, Input
from galaxy.specs import preflight
from helpers import decl, impls, model, stage


def codes(rep):
    return sorted(p.code for p in rep.problems)


def chk(models, *stages, table=INPUTS):
    return preflight.check(models, impls(*stages), table, scan=None)


def test_production_preflights(prod):
    rep = preflight.check(*prod)
    assert rep.ok, rep.problems
    assert any("UNSET default: 0" in n for n in rep.notes)  # S3 set mergers, the last one
    assert any("controls without a range: 0" in n for n in rep.notes)  # S2 finished them
    assert any("controls: 7 of 12" in n for n in rep.notes)
    assert "OK" in preflight.report(*prod)


def test_constants_declared_and_used():
    s = stage("s", ("f",), reads_constants=("K",))
    assert codes(chk([model("m", s)], s)) == ["unknown-constant"]
    assert codes(chk([model("m", s, constants={"K": 1.0, "DEAD": 2.0})], s)) == ["dead-constant"]
    assert chk([model("m", s, constants={"K": 1.0})], s).ok


def test_inputs_and_seeds_exist_and_are_the_right_kind():
    s = stage("s", ("f",), reads_inputs=("nope",))
    assert "unknown-input" in codes(chk([model("m", s)], s))
    s = stage("s", ("f",), reads_inputs=("world_seed",))
    assert "seed-as-input" in codes(chk([model("m", s)], s))
    s = stage("s", ("f",), reads_seeds=("halo_mass",))
    assert "unknown-seed" in codes(chk([model("m", s)], s))
    s = stage("s", ("f",))
    assert "unknown-input" in codes(chk([model("m", s, inputs=("nope",))], s))


def test_missing_required():
    r = stage("r", ("g",), requires=("f",))
    assert codes(chk([model("m", r)], r)) == ["missing-required"]
    p = stage("p", ("f",))
    rep = chk([model("a", p, r), model("b", r)], p, r)
    assert "missing-required" in codes(rep) and "undeclared-optional" in codes(rep)


def test_optional_discipline():
    p = stage("p", (decl("f", optional=True),))
    strict = stage("r", ("g",), requires=("f",))
    assert codes(chk([model("m", p, strict)], p, strict)) == ["optional-read-strict"]
    soft = stage("r", ("g",), requires_optional=("f",))
    rep = chk([model("a", p, soft), model("b", soft)], p, soft)
    assert rep.ok, rep.problems
    q = stage("p", ("f",))  # non-optional producer
    assert codes(chk([model("m", q, soft)], q, soft)) == ["optional-read-of-required"]
    ghost = stage("r", ("g",), requires_optional=("ghost",))
    assert codes(chk([model("m", ghost)], ghost)) == ["optional-unpublished"]


def test_cross_model_reconciliation():
    i1 = stage("i1", (decl("f", unit="kpc"),), slot="s")
    i2 = stage("i2", (decl("f", unit="pc"),), slot="s")
    rep = chk([model("a", i1), model("b", i2)], i1, i2)
    assert codes(rep) == ["contract-mismatch"]
    i2 = stage("i2", (decl("f", unit="kpc", about="different surprise"),), slot="s")
    assert chk([model("a", i1), model("b", i2)], i1, i2).ok
    p = stage("p", ("f",))
    assert codes(chk([model("a", p), model("b")], p)) == ["undeclared-optional"]
    po = stage("p", (decl("f", optional=True),))
    rep = chk([model("a", po), model("b")], po)
    assert rep.ok and not any("every model publishes" in n for n in rep.notes)
    rep = chk([model("a", po), model("b", po)], po)
    assert rep.ok and any("every model publishes" in n for n in rep.notes)


def test_ceiling():
    table = dict(INPUTS)
    for k in range(6):
        name = f"extra_{k}"
        table[name] = Input(name, name, "control", "test", unit="kpc", default=1.0)
    s = stage("s", ("f",))
    assert "ceiling" in codes(chk([model("m", s)], s, table=table))


def test_orphan_scan(tmp_path, monkeypatch):
    pkg = tmp_path / "orphanpkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "mod.py").write_text(
        textwrap.dedent(
            """
            from galaxy.core.fielddoc import FieldDecl, Kind
            from galaxy.core.stage import Stage

            LOOSE = FieldDecl(name="loose", label="l", unit="kpc", kind=Kind.SCALAR, about="orphan")
            GROUP = (FieldDecl(name="grouped", label="g", unit="kpc", kind=Kind.SCALAR, about="orphan"),)

            def _c(ctx):
                return {}

            GHOST = Stage(id="ghost", slot="ghost", checkpoint=1, about="orphan", compute=_c)
            """
        ),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    s = stage("s", ("f",))
    rep = preflight.check([model("m", s)], impls(s), INPUTS, scan=("orphanpkg",))
    assert codes(rep) == ["orphan-declaration", "orphan-declaration", "orphan-stage"]
    import orphanpkg.mod as om  # type: ignore[import-not-found]

    rep = preflight.check([model("m", s)], impls(s, om.GHOST), INPUTS, scan=("orphanpkg",))
    assert any(p.code == "orphan-stage" and "no model uses it" in p.detail for p in rep.problems)


def test_scan_finds_production_declarations():
    stages, decls = preflight.scan_declarations(("galaxy.stages",))
    assert {"halo", "disc"} <= {s.id for s in stages}
    assert {"canary", "halo_virial_radius", "circular_velocity"} <= {d.name for d in decls}
