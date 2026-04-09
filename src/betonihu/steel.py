"""Reinforcing steel properties per Eurocode 2 (EN 1992-1-1)."""

from dataclasses import dataclass


@dataclass
class SteelProperties:
    """Properties for reinforcing steel.

    Parameters
    ----------
    fyk : float
        Characteristic yield strength [MPa].
    Es : float
        Modulus of elasticity [GPa] (default 200).
    gamma_s : float
        Partial safety factor for steel (default 1.15).
    """

    fyk: float
    Es: float = 200.0
    gamma_s: float = 1.15

    @property
    def fyd(self) -> float:
        """Design yield strength [MPa]."""
        return self.fyk / self.gamma_s

    @property
    def eyd(self) -> float:
        """Design yield strain [-]."""
        return self.fyd / (self.Es * 1000)

    def __repr__(self) -> str:
        return f"B{self.fyk:.0f} (fyd={self.fyd:.2f} MPa, εyd={self.eyd:.5f})"


def fyd(fyk: float, gamma_s: float = 1.15) -> float:
    """Quick helper: design yield strength [MPa]."""
    return fyk / gamma_s
