"""Droplet Equations for Separation Design and Analysis"""

import math


def micron_to_feet(dm: float) -> float:
    """Convert Microns to Feet

    Used for performing droplet calcs in American Units

    Args:
        dm (float): Droplet Diameter, microns

    Returns:
        df (float): Droplet Diameter, feet
    """
    return dm / 304800


def feet_to_micron(df: float) -> float:
    """Convert Feet to Micron

    Used for performing droplet calcs in American Units

    Args:
        df (float): Droplet Diameter, feet

    Returns:
        dm (float): Droplet Diameter, micron
    """
    return df * 304800


def centipoise_to_lbm(mu_cp: float) -> float:
    """Centipoise to lbm/(ft*s)

    Convert Dynamic Viscosity in Centipoise to lbm/(ft*s)

    Args:
        mu_cp (float): Viscosity Dynamic, cp

    Returns:
        mu_lbm (float): Viscosity Dynamic, lbm/(ft*s)
    """
    return mu_cp / 1488.2


def velocity_drop(dd: float, cd: float, rho_drop: float, rho_fld: float, g: float) -> float:
    """Terminal Velocity of a Droplet moving through a Fluid

    Calculate the Terminal Velocity of a Droplet moving through a Fluid.
    Requires a drag coefficient to be provided for the calculation.

    Args:
        dd (float): Droplet Diameter, feet
        cd (float): Droplet Drag Coefficient, unitless
        rho_drop (float): Droplet Density, lbm/ft3
        rho_fld (float): Fluid Density, lbm/ft3
        g (float): Gravitational Acceleration, ft/s2

    Returns:
        vt (float): Terminal Velocity of Droplet, ft/s
    """
    drho = abs((rho_drop - rho_fld) / rho_fld)  # incase droplet is rising
    vt = math.sqrt((4 * g / 3) * (dd / cd) * drho)
    return vt


def diameter_drop(vt: float, cd: float, rho_drop: float, rho_fld: float, g: float) -> float:
    """Droplet Diameter for specified terminal velocity

    Calculate the droplet diameter to achieve a specified terminal velocity
    Requires a drag coefficient to be provided for the calculation.

    Args:
        vt (float): Terminal Velocity of Droplet, ft/s
        cd (float): Droplet Drag Coefficient, unitless
        rho_drop (float): Droplet Density, lbm/ft3
        rho_fld (float): Fluid Density, lbm/ft3
        g (float): Gravitational Acceleration, ft/s2

    Returns:
        dd (float): Droplet Diameter, feet
    """
    drho = abs(rho_fld / (rho_drop - rho_fld))  # incase droplet is rising
    dd = vt**2 * (3 / (4 * g)) * cd * drho
    return dd


def reynolds_sphere(dd: float, vd: float, rho_fld: float, mu_fld: float) -> float:
    """Reynolds Number for Flow Past a Sphere

    Calculate the Reynolds number for flow past a sphere or droplet.
    Requires a droplet velocity to be provided for the calculation.

    Args:
        dd (float): Droplet Diameter, feet
        vd (float): Droplet Velocity, ft/s
        rho_fld (float): Density of Fluid, lbm/ft3
        mu_fld (float): Viscosity of Fluid, lbm/(ft*s)

    Returns:
        re (float): Reynolds Number of Sphere through a fluid, unitless
    """
    re = dd * vd * rho_fld / mu_fld
    return re


def drag_coeff(re: float) -> float:
    """Drag Coefficient of a Sphere

    Sphere moving through a fluid.

    Args:
        re (float): Reynolds Number, unitless

    Returns:
        cd (float): Drag Coefficient, unitless
    """
    if re == 0:
        return float("inf")
    cd = 24 / re + 3 / math.sqrt(re) + 0.34
    return cd


def velocity_terminal(dd: float, rho_drop: float, rho_fld: float, mu_fld: float, g: float) -> float:
    """Terminal Velocity of Droplet moving through a Fluid

    Calculate the terminal velocity of a droplet moving through a fluid.
    Will iterate on the velocity and drag coefficient until convergance occurs.

    Args:
        dd (float): Droplet Diameter, feet
        rho_drop (float): Droplet Density, lbm/ft3
        rho_fld (float): Density of Fluid, lbm/ft3
        mu_fld (float): Viscosity of Fluid, lbm/(ft*s)
        g (float): Gravity Acceleration, ft/s2

    Returns:
        vt (float): Terminal Velocity of Droplet, ft/s
    """

    cd = 0.34  # starting drag coeff guess
    vt = velocity_drop(dd, cd, rho_drop, rho_fld, g)

    while True:  # create an undefined while loop
        re = reynolds_sphere(dd, vt, rho_fld, mu_fld)
        cd = drag_coeff(re)
        vt_new = velocity_drop(dd, cd, rho_drop, rho_fld, g)

        if abs(vt_new - vt) < 0.001:  # convergence check
            break
        vt = vt_new

    return vt_new  # the final vt iteration value


def droplet_diameter(vt: float, rho_drop: float, rho_fld: float, mu_fld: float, g: float) -> float:
    """Droplet Diameter for specified Terminal Velocity

    Calculate the required droplet diameter for specific terminal velocity.
    Will iterate on droplet diameter and drag coefficient until convergence.

    Args:
        vt (float): Terminal Velocity, ft/s
        rho_drop (float): Droplet Density, lbm/ft3
        rho_fld (float): Density of Fluid, lbm/ft3
        mu_fld (float): Viscosity of Fluid, lbm/(ft*s)
        g (float): Gravity Acceleration, ft/s2

    Returns:
        dd (float): Droplet Diameter, feet
    """
    cd = 0.34
    dd = diameter_drop(vt, cd, rho_drop, rho_fld, g)

    while True:
        re = reynolds_sphere(dd, vt, rho_fld, mu_fld)
        cd = drag_coeff(re)
        dd_new = diameter_drop(vt, cd, rho_drop, rho_fld, g)

        if abs(dd_new - dd) < 1e-9:  # how small since we are dealing with tiny numbers in feet...?
            break
        dd = dd_new

    return dd_new  # final dd iteration value
