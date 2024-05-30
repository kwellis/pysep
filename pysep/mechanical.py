"""Storing all the mechanical and pressure rating equations for a separator"""

from math import log, pi, sqrt


def sep_shell_thick(vid: float, mawp: float, sv: float = 20000, eff: float = 1, corr: float = 0.125) -> float:
    """Separator Shell Thickness

    Calculate the separator shell thickness. UG-27c Eqn. 1

    Args:
        vid (float): Vessel Inner Diameter, feet
        mawp (float): Max Allowable Working Pressure, psig
        sv (float): Material Max Allowable Stress, psig
        eff (float): Joint Efficiency Factor
        corr (float): Corrosion Allowance, inches

    Returns:
        thk (float): Shell Thickness, inches
    """
    vir = 12 * vid / 2  # vessel inner radius, inches
    thk_base = mawp * vir / (sv * eff - 0.6 * mawp)
    thk = thk_base + corr
    return thk


def surface_spheroid_oblate(x_radius: float, y_radius: float) -> float:
    """Surface Area of an Oblate Spheroid

    https://mathworld.wolfram.com/SurfaceofRevolution.html
    An oblate spheroid is chubbier than it is tall.

    Args:
        x_radius (float): Radius of Spheroid in the x-direction
        y_radius (float): Radius of Spheroid in the y-direction

    Returns:
        a_surf (float): Surface Area of Oblate Spheroid
    """
    if x_radius <= y_radius:
        raise ValueError("X-Radius needs to be bigger than Y-Radius for an Oblate Spheroid")
    ecc = sqrt(1 - (y_radius**2 / x_radius**2))
    a_surf = 2 * pi * x_radius**2 + (pi * y_radius**2 / ecc) * log((1 + ecc) / (1 - ecc))
    return a_surf


def surface_cylinder(diam: float, height: float) -> float:
    """Surface Area of a Cylinder

    Args:
        diam (float): Diameter of Cylinder
        height (float): Height of Cylinder

    Returns:
        a_surf (float): Surface Area of Cylinder
    """
    return pi * diam * height


def surface_elliptical_head(vid: float) -> float:
    """Surface Area of 2:1 Elliptical Head

    The following equation is an approximation and does not following
    the ASME code to totallity. Code should be consulted for higher accuracy

    Args:
        vid (float): Vessel Inner Diameter, feet

    Returns
        a_head (float): Surface Area of One Elliptical Head, ft2
    """
    x_radius = vid / 2  # diameter to radius
    y_radius = x_radius / 2  # for the 2:1 aspect flair
    a_surf = surface_spheroid_oblate(x_radius, y_radius)  # this gives the entire spheroid, we need half of it
    return a_surf / 2


def vessel_bare_weight(vid: float, lss: float, thk: float, rho_metal: float = 490) -> float:
    """Vessel Bare Weight

    Weight of the Vessel with just the body and elliptical heads. Doesn't
    include the weights of any internals, insulation, nozzles, or supports.

    Args:
        vid (float): Vessel Inner Diameter, feet
        lss (float): Vessel Seam to Seam Length, feet
        thk (float): Vessel Thickness, inches
        rho_metal (float): Density of Metal, lbm/ft3

    Return:
        wbv (float): Weight of Bare Vessel, lbm"""

    as_cyli = surface_cylinder(vid, lss)  # surface area of cylinder
    vs_cyli = as_cyli * thk / 12
    wg_cyli = rho_metal * vs_cyli
    as_head = surface_elliptical_head(vid)  # surface area of elliptical head
    vs_head = as_head * thk / 12
    wg_head = rho_metal * vs_head
    return wg_cyli + 2 * wg_head


if __name__ == "__main__":

    thk = sep_shell_thick(10.5, 900)
    print(f"Vessel Thickness is {round(thk,2)} inches")

    fpad_vid = 126 / 12
    fpad_lss = 40
    fpad_thk = 2.39  # inches

    fpad_bare = vessel_bare_weight(fpad_vid, fpad_lss, fpad_thk)

    print(f"F-Pad Bare Vessel Weight: {round(fpad_bare, 0)} lbm")

    ben_vid = 150.376 / 12
    ben_lss = 10
    ben_thk = 2.812

    ben_bare = vessel_bare_weight(ben_vid, ben_lss, ben_thk)
    print(f"Ben Vessel Weight: {round(ben_bare, 0)} lbm")
