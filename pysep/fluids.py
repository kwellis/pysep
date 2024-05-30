from pysep.geometry import vessel_area_three_phase, vessel_area_two_phase


def volm_flow(mflo: float, rho: float) -> float:
    """Calculate Volumetric Flow from Mass Flow / Density

    Args:
        mflo (float): Mass Flow, lbm/hr
        rho (float): Density, lbm/ft3

    Returns:
        vflo (float): Volumetric Flow, ft3/s
    """
    return (mflo / rho) * (1 / (60 * 60))  # ft3/s


def velocity_volm(vflo: float, area: float) -> float:
    """Fluid Velocity from Volumetric Flowrate

    Args:
        vflo (float): Volumetric Flowrate, ft3/s
        area (float): Cross Sectional Area, ft2

    Returns:
        vel (float): Velocity Cross Sectional, ft/s
    """
    return vflo / area


def retention(leff: float, vx: float) -> float:
    """Retention Time in Separator

    Args:
        leff (float): Vessel Effective Length, feet
        vx (float): Horizontal Velocity, ft/s

    Returns:
        ret (float): Retention Time, minutes
    """
    ret = (leff / vx) * (1 / 60)
    return ret


def reynolds(vel: float, rho: float, dhyd: float, mu: float) -> float:
    """Reynolds Number Across Piping

    Calculate the Reynolds Number for a Pipe or Separator

    Args:
        vel (float): Velocity Fluid, ft/s
        rho (float): Density Fluid, lbm/ft3
        dhyd (float): Hydraulic Diameter, ft
        mu (float): Dynamic Viscosity, lbm/(ft*s)

    Returns:
        re (float): Reynolds Number, unitless
    """
    return rho * vel * dhyd / mu


def water_fraction(qoil: float, qwat: float) -> float:
    """Water Fraction in a Oil and Water Mixture

    Args:
        qoil (float): Volumetric Flowrate Water, ft3/s
        qwat (float): Volumetric Flowrate Oil, ft3/s

    Returns:
        fw (float): Water Fraction, unitless
    """
    fw = qwat / (qoil + qwat)
    return fw


def liquid_density(fw: float, rho_oil: float, rho_wat: float) -> float:
    """Liquid Density of an Oil and Water Mixture

    Args:
        fw (float): Water Fraction, unitless
        rho_oil (float): Oil Density, lbm/ft3
        rho_wat (float): Water Density, lbm/ft3

    Returns:
        rho_liq (float): Liquid Density, lbm/ft3
    """
    rho_liq = rho_oil * (1 - fw) + rho_wat * fw
    return rho_liq


def liquid_viscosity(fw: float, mu_oil: float, mu_wat: float) -> float:
    """Liquid Viscosity of an Oil and Water Mixture

    Args:
        fw (float): Water Fraction, unitless
        mu_oil (float): Oil Viscosity, cP
        mu_wat (float): Water Viscosity, cP

    Returns:
        mu_liq (float): Liquid Viscosity, cP
    """
    mu_liq = mu_oil * (1 - fw) + mu_wat * fw
    return mu_liq


def validate_props(props: dict, req_keys: set) -> None:
    """Validate Dictionary of Stream Properties

    Ensures that the dictionaries that are fed to the class have the
    correct keys so they are recognized in the code later on.

    Args:
        props (dict): Dictionary of Properties
        req_keys (set): Set of Required Keys
    """
    missing_keys = req_keys - set(props.keys())
    if missing_keys:
        raise KeyError(f"Missing Keys from Property Dictionary: {missing_keys}")


def liquid_props(oil_props: dict, wat_props: dict) -> dict:
    """Liquid Properties Dictionary

    Input property dictionary for Oil and Water.
    Output a similiarly designed dictionary for the equivalent liquid.

    Args:
        oil_props (dict): Oil Properties
        wat_props (dict): Water Properties

    Returns:
        liq_props (dict): Liquid Properties
    """
    req_keys = {"mass_flow", "density", "viscosity"}
    validate_props(oil_props, req_keys)
    validate_props(wat_props, req_keys)

    mflo_liq = oil_props["mass_flow"] + wat_props["mass_flow"]

    qoil = volm_flow(oil_props["mass_flow"], oil_props["density"])
    qwat = volm_flow(wat_props["mass_flow"], wat_props["density"])
    fw = water_fraction(qoil, qwat)

    rho_liq = liquid_density(fw, oil_props["density"], wat_props["density"])
    mu_liq = liquid_viscosity(fw, oil_props["viscosity"], wat_props["viscosity"])

    liq_props = {
        "mass_flow": mflo_liq,  # lbm/hr, 40 MMSCFD
        "density": rho_liq,  # lbm/ft3
        "viscosity": mu_liq,  # centipoise
    }
    return liq_props


def two_phase_velocities(
    vid: float,
    hliq: float,
    vflo_liq: float,
    vflo_gas: float,
) -> tuple[float, float]:
    """Two Phase Velocities in Separator

    Calculate the liquid and gas bulk velocity inside a separator.

    Args:
        vid (float): Vessel Inner Diameter, feet
        hliq (float): Height of the Liquid in Vessel, feet
        vflo_liq (float): InSitu Volume Liquid Flow, ft3/s
        vflo_gas (float): InSitu Volume Gas Flow, ft3/s

    Returns:
        vx_liq (float): Liquid Horizontal Velocity, ft/s
        vx_gas (float): Gas Horizontal Velocity, ft/s
    """
    aliq, agas = vessel_area_two_phase(vid, hliq)
    vx_liq = vflo_liq / aliq
    vx_gas = vflo_gas / agas
    return vx_liq, vx_gas


def two_phase_retention(leff: float, vx_liq: float, vx_gas: float) -> tuple[float, float]:
    """Two Phase Retention Time in Separator

    Args:
        leff (float): Vessel Effective Length, feet
        vx_liq (float): Liquid Horizontal Velocity, ft/s
        vx_gas (float): Gas Horizontal Velocity, ft/s

    Returns:
        ret_liq (float): Liquid Retention Time, minutes
        ret_gas (float): Gas Retention Time, minutes
    """
    ret_liq = (leff / vx_liq) * (1 / 60)
    ret_gas = (leff / vx_gas) * (1 / 60)
    return ret_liq, ret_gas


def two_phase_reynolds(
    dhyd_liq: float,
    dhyd_gas: float,
    vel_liq: float,
    vel_gas: float,
    rho_liq: float,
    rho_gas: float,
    mu_liq: float,
    mu_gas: float,
) -> tuple[float, float]:
    """Two Phase Reynolds Number in Separator

    Calculate the Two Phase Reynolds Number for a Gas - Liquid Separator

    Args:
        dhyd_liq (float): Hydraulic Diameter Liquid, feet
        dhyd_gas (float): Hydraulic Diameter Gas, feet
        vel_liq (float): InSitu Velocity Liquid Flow, ft/s
        vel_gas (float): InSitu Velocity Gas Flow, ft/s
        rho_liq (float): Density Liquid, lbm/ft3
        rho_gas (float): Density Gas, lbm/ft3
        mu_liq (float): Viscosity Dynamic Liquid, lbm/(ft*s)
        mu_gas (float): Viscosity Dynamic Gas, lbm/(ft*s)

    Returns:
        re_liq (float): Liquid Reynolds Number, unitless
        re_gas (float): Gas Reynolds, unitless
    """
    re_liq = reynolds(vel_liq, rho_liq, dhyd_liq, mu_liq)
    re_gas = reynolds(vel_gas, rho_gas, dhyd_gas, mu_gas)
    return re_liq, re_gas


def three_phase_velocities(
    vid: float, lss: float, hoil: float, hwat: float, vflo_oil: float, vflo_wat: float, vflo_gas: float
) -> tuple[float, float, float, float, float, float]:
    """Three Phase Velocities in Separator

    Calculate the oil, water and gas bulk velocities inside a separator. Use the calculated
    velocities to also calculate how long each phase sits inside the separator. EG Retention Time.
    Future work, calculate the smallest liquid droplet that should be able to come out of the gas phase?
    Assume zero gas is carried over inside the liquid? Also, add Reynolds # calculation for gas / liquid?

    Args:
        vid (float): Vessel Inner Diameter, feet
        lss (float): Vessel Seam to Seam Length, feet
        hwat (float): Height of the Water in Vessel, feet
        hoil (float): Height of the Oil in Vessel, feet
        vflo_oil (float): InSitu Volume Oil Flow, ft3/s
        vflo_wat (float): InSitu Volume Water Flow, ft3/s
        vflo_gas (float): InSitu Volume Gas Flow, ft3/s

    Returns:
        vx_oil (float): Oil Horizontal Velocity, ft/s
        vx_wat (float): Water Horizontal Velocity, ft/s
        vx_gas (float): Gas Horizontal Velocity, ft/s
        ret_oil (float): Oil Retention Time, minutes
        ret_wat (float): Water Retention Time, minutes
        ret_gas (float): Gas Retention Time, minutes
    """
    aoil, awat, agas = vessel_area_three_phase(vid, hoil, hwat)
    vx_oil = vflo_oil / aoil
    vx_wat = vflo_wat / awat
    vx_gas = vflo_gas / agas

    ret_oil = (lss / vx_oil) * (1 / 60)
    ret_wat = (lss / vx_wat) * (1 / 60)
    ret_gas = (lss / vx_gas) * (1 / 60)

    return vx_oil, vx_wat, vx_gas, ret_oil, ret_wat, ret_gas
