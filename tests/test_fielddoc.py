"""Closed vocabularies: units and field declarations (rule A8)."""

from __future__ import annotations

import pytest

from galaxy.core import units
from galaxy.core.fielddoc import AXES, CMAPS, OBJECTS, DeclarationError, FieldDecl, Kind, Palette, Ramp
from helpers import decl


def test_units_are_ascii_and_unique():
    assert len(units.UNITS) == len(units._UNITS)
    for sym, u in units.UNITS.items():
        assert sym and sym.isascii(), sym
        assert u.symbol == sym
        assert u.dimension


def test_unit_lookup():
    assert units.unit("kpc").dimension == "length"
    assert units.unit("Msun").display == "M☉"
    with pytest.raises(units.UnknownUnit):
        units.unit("furlong")
    with pytest.raises(units.UnknownUnit):
        units.unit(None)  # type: ignore[arg-type]


@pytest.mark.parametrize("kind", list(Kind))
def test_every_kind_declares(kind):
    d = decl("x", kind)
    assert d.kind is kind
    assert d.contract()[3] == kind.value


def test_kind_structure():
    assert {k.domain for k in Kind} == {"grid", "galaxy", "object"}
    assert Kind.FIELD.domain == "grid" and not Kind.FIELD.categorical
    assert Kind.CATEGORY_SCALAR.domain == "galaxy" and Kind.CATEGORY_SCALAR.categorical
    assert Kind.COLUMN.domain == "object"
    assert len(Kind) == 6


def test_kind_accepts_string():
    assert decl("x", "scalar").kind is Kind.SCALAR


@pytest.mark.parametrize(
    "bad",
    [
        dict(name="Bad"),
        dict(name="1x"),
        dict(name="a-b"),
        dict(label=" "),
        dict(unit="furlong"),
        dict(kind="tensor"),
        dict(about=""),
        dict(about="   "),
        dict(provenance="random"),
    ],
)
def test_rejects(bad):
    name = bad.pop("name", "x")
    with pytest.raises(DeclarationError):
        decl(name, **bad)


def test_grid_needs_axes_in_canonical_order():
    with pytest.raises(DeclarationError):
        decl("x", axes=())
    assert decl("x", axes=("R", "t")).axes == ("R", "t")
    assert decl("x", axes=("t",)).axes == ("t",)
    assert decl("x", axes=("R", "z")).axes == ("R", "z")
    assert decl("x", axes=("R", "phi")).axes == ("R", "phi")
    for axes in [("t", "R"), ("R", "R"), ("R", "q"), ("phi", "R")]:
        with pytest.raises(DeclarationError):
            decl("x", axes=axes)


def test_scalar_takes_no_axes_and_needs_no_ramp():
    with pytest.raises(DeclarationError):
        decl("x", Kind.SCALAR, axes=("R",))
    assert decl("x", Kind.SCALAR).ramp is None
    assert decl("x", Kind.SCALAR, ramp=Ramp("viridis")).ramp == Ramp("viridis")


def test_object_kinds_need_an_object_class():
    with pytest.raises(DeclarationError):
        decl("x", Kind.COLUMN, of=None)
    with pytest.raises(DeclarationError):
        decl("x", Kind.COLUMN, of="rock")
    for of in OBJECTS:
        assert decl("x", Kind.COLUMN, of=of).of == of
    with pytest.raises(DeclarationError):
        decl("x", of="star")  # grid kind
    with pytest.raises(DeclarationError):
        decl("x", Kind.SCALAR, of="star")


def test_categorical_rules():
    with pytest.raises(DeclarationError):
        decl("x", Kind.CATEGORY_FIELD, categories=())
    with pytest.raises(DeclarationError):
        decl("x", Kind.CATEGORY_FIELD, categories=("a", "a"))
    with pytest.raises(DeclarationError):
        decl("x", Kind.CATEGORY_FIELD, unit="kpc")
    with pytest.raises(DeclarationError):
        decl("x", Kind.CATEGORY_FIELD, ramp=Palette(("#000000",)))  # 1 colour, 2 categories
    with pytest.raises(DeclarationError):
        decl("x", Kind.CATEGORY_FIELD, ramp=Ramp("greys"))
    with pytest.raises(DeclarationError):
        decl("x", ramp=Palette(("#000000",)))  # palette on a continuous field
    with pytest.raises(DeclarationError):
        decl("x", categories=("a",))  # categories on a continuous field
    assert decl("x", Kind.CATEGORY_SCALAR).ramp is None


def test_grid_and_object_fields_need_a_ramp():
    with pytest.raises(DeclarationError):
        decl("x", ramp=None)
    with pytest.raises(DeclarationError):
        decl("x", Kind.COLUMN, ramp=None)
    with pytest.raises(DeclarationError):
        decl("x", Kind.CATEGORY_FIELD, ramp=None)


def test_ramp_validation():
    with pytest.raises(DeclarationError):
        Ramp("nope")
    with pytest.raises(DeclarationError):
        Ramp("greys", scale="cubic")
    with pytest.raises(DeclarationError):
        Ramp("greys", lo=1.0, hi=1.0)
    assert Ramp("greys", lo=0.0, hi=1.0).hi == 1.0
    assert Ramp("magma", scale="log").scale == "log"


def test_palette_validation():
    with pytest.raises(DeclarationError):
        Palette(())
    with pytest.raises(DeclarationError):
        Palette(("red",))
    with pytest.raises(DeclarationError):
        Palette(("#12345",))
    assert Palette(("#00ff00", "#FF00aa")).colors[1] == "#FF00aa"


def test_contract_excludes_about_only():
    a = decl("x", about="one surprise")
    b = decl("x", about="another")
    assert a.contract() == b.contract()
    assert decl("x", unit="kpc").contract() != a.contract()
    assert decl("x", optional=True).contract() != a.contract()
    assert decl("x", provenance="seeded").contract() != a.contract()
    assert decl("x", meaningful_zero=True).contract() != a.contract()
    assert decl("x", ramp=Ramp("viridis")).contract() != a.contract()


def test_closed_sets():
    assert AXES == ("R", "t", "z", "phi")
    assert "greys" in CMAPS
    assert "star" in OBJECTS and "planet" in OBJECTS


def test_frozen():
    d = decl("x")
    with pytest.raises(AttributeError):
        d.unit = "kpc"  # type: ignore[misc]
    assert isinstance(d, FieldDecl)
