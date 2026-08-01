"""Characteristic impedance of a coaxial cable under mechanical deformation.

A coaxial cable's characteristic impedance depends on the ratio of the shield
(outer) radius to the core (inner) radius and on the dielectric permittivity:

    Z0 = (60 / sqrt(eps_r)) * ln(b / a)

When the cable is compressed, the effective shield radius b shrinks, which lowers
b/a and therefore shifts Z0 away from its nominal value (typically 50 or 75 Ω).
This module models that shift and the resulting impedance mismatch.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CoaxGeometry:
    """Nominal coaxial cable geometry and dielectric."""

    core_radius_m: float = 0.5e-3    # a, inner conductor radius
    shield_radius_m: float = 3.0e-3  # b, outer shield radius (nominal)
    eps_r: float = 2.25              # relative permittivity of the dielectric


def characteristic_impedance(core_radius_m: float, shield_radius_m: float,
                             eps_r: float) -> float:
    """Characteristic impedance Z0 (ohms) of a coaxial line."""
    return (60.0 / np.sqrt(eps_r)) * np.log(shield_radius_m / core_radius_m)


def impedance_under_compression(geom: CoaxGeometry, compression_frac: float,
                                eps_r: float | None = None) -> float:
    """Z0 when the shield radius is reduced by `compression_frac` (0..1)."""
    if eps_r is None:
        eps_r = geom.eps_r
    b = geom.shield_radius_m * (1.0 - compression_frac)
    return characteristic_impedance(geom.core_radius_m, b, eps_r)


def reflection_coefficient(z0: float, z_ref: float = 50.0) -> float:
    """Voltage reflection coefficient for an impedance mismatch to `z_ref`."""
    return (z0 - z_ref) / (z0 + z_ref)


def vswr(z0: float, z_ref: float = 50.0) -> float:
    """Voltage standing-wave ratio for a mismatch to `z_ref`."""
    gamma = abs(reflection_coefficient(z0, z_ref))
    return (1.0 + gamma) / (1.0 - gamma) if gamma < 1.0 else np.inf
