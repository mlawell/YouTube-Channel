"""Number formatting, split by what the number *means*.

House numbers and lot numbers are identifiers, not quantities. "9201 Escape
Ave" is an address; "9,201 Escape Ave" is not a thing, and on a reference sheet
whose whole purpose is matching an address to a listing, a stray comma is wrong
in the one place it cannot afford to be.

Quantities -- homesite counts, acreages -- take the separator as normal.

    ident(9201)          -> '9201'
    ident_range(9201, 9499) -> '9201-9499'
    qty(3229)            -> '3,229'
"""

from __future__ import annotations

DASH = "\u2013"  # en dash, for ranges


def ident(n) -> str:
    """An identifier: house number, lot number, plat page. Never separated."""
    if n is None or n == "":
        return ""
    return str(int(n))


def ident_range(lo, hi, *, dash: str = DASH, empty: str = "\u2014") -> str:
    """A span of identifiers. A one-item span prints as a lone number, because
    '9394-9394' is just noise for a street with a single addressed parcel."""
    if lo is None or hi is None:
        return empty
    lo, hi = int(lo), int(hi)
    return ident(lo) if lo == hi else f"{ident(lo)}{dash}{ident(hi)}"


def qty(n) -> str:
    """A real quantity: counts, acreages. Thousands separator is correct here."""
    if n is None:
        return ""
    return f"{n:,}"
