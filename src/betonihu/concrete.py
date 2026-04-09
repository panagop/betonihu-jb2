"""Concrete material properties per Eurocode 2 (EN 1992-1-1)."""

from dataclasses import dataclass


@dataclass
class ConcreteProperties:
    """Properties for a concrete class C(fck)/(fck+δ).

    Parameters
    ----------
    fck : float
        Characteristic compressive cylinder strength [MPa].
    gamma_c : float
        Partial safety factor for concrete (default 1.5).
    """

    fck: float
    gamma_c: float = 1.5

    @property
    def fcm(self) -> float:
        """Mean compressive strength [MPa]."""
        return self.fck + 8

    @property
    def fcd(self) -> float:
        """Design compressive strength [MPa]."""
        return self.fck / self.gamma_c

    @property
    def fctm(self) -> float:
        """Mean axial tensile strength [MPa]."""
        if self.fck <= 50:
            return 0.30 * self.fck ** (2 / 3)
        else:
            return 2.12 * (1 + self.fcm / 10) ** 0.1  # noqa: E226

    @property
    def Ecm(self) -> float:
        """Secant modulus of elasticity [GPa]."""
        return 22.0 * (self.fcm / 10) ** 0.3

    def __repr__(self) -> str:
        return f"C{self.fck:.0f} (fcd={self.fcd:.2f} MPa, Ecm={self.Ecm:.2f} GPa)"


def fcd(fck: float, gamma_c: float = 1.5) -> float:
    """Quick helper: design compressive strength [MPa]."""
    return fck / gamma_c
