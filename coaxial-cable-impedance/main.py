"""Coaxial cable impedance demo.

Shows how compression and dielectric permittivity shift the characteristic
impedance, and the resulting mismatch (reflection / VSWR) against a 50 Ω system.

Usage:
    python main.py
Figures written to assets/.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from cable.impedance import (
    CoaxGeometry,
    impedance_under_compression,
    reflection_coefficient,
    vswr,
)

ASSETS = "assets"


def plot_impedance_surface(geom):
    compression = np.linspace(0, 0.3, 60)      # up to 30%
    eps_r = np.linspace(1.5, 3.0, 60)
    C, E = np.meshgrid(compression, eps_r)
    Z = np.vectorize(lambda c, e: impedance_under_compression(geom, c, e))(C, E)

    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(C * 100, E, Z, cmap="viridis")
    ax.set_xlabel("Shield compression (%)")
    ax.set_ylabel("Permittivity εr")
    ax.set_zlabel("Impedance Z₀ (Ω)")
    ax.set_title("Characteristic impedance vs. compression and permittivity")
    fig.colorbar(surf, shrink=0.5, aspect=12)
    fig.tight_layout()
    fig.savefig(os.path.join(ASSETS, "impedance_surface.png"), dpi=120)
    plt.close(fig)


def plot_compression_curve(geom):
    compression = np.linspace(0, 0.3, 100)
    z = [impedance_under_compression(geom, c) for c in compression]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(compression * 100, z, lw=1.9)
    ax.axhline(50, color="r", ls="--", lw=1, label="50 Ω target")
    ax.set_xlabel("Shield compression (%)")
    ax.set_ylabel("Impedance Z₀ (Ω)")
    ax.set_title("Impedance drift as the cable is compressed")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(ASSETS, "compression_curve.png"), dpi=120)
    plt.close(fig)


def plot_mismatch(geom):
    compression = np.linspace(0, 0.3, 100)
    gamma, swr = [], []
    for c in compression:
        z = impedance_under_compression(geom, c)
        gamma.append(abs(reflection_coefficient(z, 50.0)))
        swr.append(vswr(z, 50.0))
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(compression * 100, gamma, lw=1.8, color="#1f77b4", label="|Γ|")
    ax1.set_xlabel("Shield compression (%)")
    ax1.set_ylabel("Reflection coefficient |Γ|", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
    ax1.grid(True, alpha=0.3)
    ax2 = ax1.twinx()
    ax2.plot(compression * 100, swr, lw=1.8, color="#d62728", label="VSWR")
    ax2.set_ylabel("VSWR", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax1.set_title("Impedance mismatch to a 50 Ω system vs. compression")
    fig.tight_layout()
    fig.savefig(os.path.join(ASSETS, "mismatch.png"), dpi=120)
    plt.close(fig)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    geom = CoaxGeometry()
    plot_impedance_surface(geom)
    plot_compression_curve(geom)
    plot_mismatch(geom)

    z_nom = impedance_under_compression(geom, 0.0)
    z_20 = impedance_under_compression(geom, 0.2)
    print(f"Nominal Z₀        = {z_nom:.2f} Ω")
    print(f"Z₀ at 20% squeeze = {z_20:.2f} Ω")
    print(f"VSWR at 20%       = {vswr(z_20, 50.0):.3f}")
    print("\nFigures written to assets/.")


if __name__ == "__main__":
    main()
