"""Code for Unit Conversions"""


def volm_mass_conversion(volm_flow: float, units: str, rho_fld: float) -> float:
    """Volumetric to Mass Flow Conversion

    Convert from a volumetric flow in units of bpd, gpm, mscfd or mmscfd
    to a mass flow, in lbm/hour. If using mscfd or mmscfd, need to use the
    density that is at standard conditions.

    Args:
        volm_flow (float): Volumetric Flow
        units (str): bpd, gpm, mscfd or mmscfd
        rho_fld (float): Density of Fluid, lbm/ft3

    Returns:
        mass_flow (float): Mass Flow, lbm/hr
    """
    conv_dict = {"bpd": 42 / (24 * 7.48), "gpm": 60 / 7.48, "mscfd": 1e3 / 24, "mmscfd": 1e6 / 24}
    mass_flow = volm_flow * conv_dict[units] * rho_fld
    return mass_flow


if __name__ == "__main__":
    oil_volm = 50000  # bpd
    oil_unit = "bpd"
    oil_rho = 58.74  # lbm/ft3
    oil_mass = volm_mass_conversion(oil_volm, oil_unit, oil_rho)
    print(f"\nOil Mass Flow is {oil_mass:.3e} lbm/ft3")

    water_volm = 110000  # bpd
    water_unit = "bpd"
    water_rho = 62.4  # lbm/ft3
    water_mass = volm_mass_conversion(water_volm, water_unit, water_rho)
    print(f"Water Mass Flow is {water_mass:.3e} lbm/ft3")

    gas_volm = 40  # mmscfd
    gas_unit = "mmscfd"
    gas_rho = 0.0415  # standard conditions, lbm/ft3
    gas_mass = volm_mass_conversion(gas_volm, "mmscfd", gas_rho)
    print(f"Gas Mass Flow is {gas_mass:.3e} lbm/ft3\n")
