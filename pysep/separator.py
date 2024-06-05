import numpy as np

import pysep.drops as drp
import pysep.fluids as fld
import pysep.mechanical as mech
from pysep.geometry import (
    vessel_area_three_phase,
    vessel_area_two_phase,
    vessel_dhyd_three_phase,
    vessel_dhyd_two_phase,
)


class SepMech:
    """Parent Class for inheritting mechanical methods that are the same in either a two or three phase sep."""

    def __init__(self, vid: float, lss: float) -> None:
        """Parent Class of Separator

        Used for mechanical parameters and equations of a two or three phase separator

        Args:
            vid (float): Vessel Inner Diameter, feet
            lss (float): Vessel Length Seam to Seam, feet
        """
        self.vid = vid
        self.lss = lss

    def __repr__(self) -> str:
        return f"\nType: {self.__class__.__name__}, Vessel ID: {self.vid} feet, Seam-Seam Length: {self.lss} feet\n"

    def shell_thick(self, mawp: float, sv: float = 20000, eff: float = 1, corr: float = 0.125) -> float:
        """Separator Shell Thickness

        Calculate the separator shell thickness. UG-27c Eqn. 1

        Args:
            mawp (float): Max Allowable Working Pressure, psig
            sv (float): Material Max Allowable Stress, psig
            eff (float): Joint Efficiency Factor
            corr (float): Corrosion Allowance, inches

        Returns:
            thk (float): Shell Thickness, inches
        """
        self.mawp = mawp
        return mech.sep_shell_thick(self.vid, mawp, sv, eff, corr)

    def weight_bare(self, thk: float, rho_metal: float = 490) -> float:
        """Separator Bare Weight

        Weight of the Vessel with just the body and elliptical heads. Doesn't
        include the weights of any internals, insulation, nozzles, or supports.

        Args:
            thk (float): Vessel Thickness, inches
            rho_metal (float): Density of Metal, lbm/ft3

        Return:
            wbv (float): Weight of Bare Vessel, lbm
        """
        return mech.vessel_bare_weight(self.vid, self.lss, thk, rho_metal)


class SepTwoPhase(SepMech):
    def __init__(self, vid: float, lss: float, leff: float, hliq: float, liq_props: dict, gas_props: dict) -> None:
        """Two Phase Separator of Gas and Liquid

        Args:
            vid (float): Vessel Inner Diameter, feet
            lss (float): Length Seam to Seam, feet
            leff (float): Vessel Effective Length, feet
            hliq (float): Height of the Liquid in Vessel, feet
            liq_props (dict): Liquid Properties
            gas_props (dict): Gas Properties
        """

        req_keys = {"mass_flow", "density", "viscosity"}
        fld.validate_props(liq_props, req_keys)
        fld.validate_props(gas_props, req_keys)

        self.vid = vid
        self.lss = lss
        self.leff = leff
        self.hliq = hliq
        self.liq_props = liq_props
        self.gas_props = gas_props

        aliq, agas = vessel_area_two_phase(vid, hliq)
        dhyd_liq, dhyd_gas = vessel_dhyd_two_phase(vid, hliq)

        qliq = fld.volm_flow(liq_props["mass_flow"], liq_props["density"])
        qgas = fld.volm_flow(gas_props["mass_flow"], gas_props["density"])

        vx_liq = fld.velocity_volm(qliq, aliq)
        vx_gas = fld.velocity_volm(qgas, agas)

        ret_liq = fld.retention(leff, vx_liq)
        ret_gas = fld.retention(leff, vx_gas)

        mu_liq = drp.centipoise_to_lbm(liq_props["viscosity"])  # proper units
        mu_gas = drp.centipoise_to_lbm(gas_props["viscosity"])

        re_liq = fld.reynolds(vx_liq, liq_props["density"], dhyd_liq, mu_liq)
        re_gas = fld.reynolds(vx_gas, gas_props["density"], dhyd_gas, mu_gas)

        dh_gas = vid - hliq  # differential height of gas
        vt_gas_req = dh_gas / (ret_gas * 60)  # used to calculate smallest droplet that can come out of gravity

        g = 32.174  # ft/s2
        drop_liq = drp.droplet_diameter(vt_gas_req, liq_props["density"], gas_props["density"], mu_gas, g)

        self.g = g
        self.aliq, self.agas = aliq, agas
        self.vx_liq, self.vx_gas = vx_liq, vx_gas
        self.re_liq, self.re_gas = re_liq, re_gas
        self.ret_liq, self.ret_gas = ret_liq, ret_gas
        self.drop_liq = drp.feet_to_micron(drop_liq)

    def results(self) -> None:
        """Show Results of the Two Phase Separator"""

        labels = ["X-Area", "Velocity", "Retention", "Reynolds", "Min_Drop"]
        units = ["ft2", "ft/s", "min", "none", "µm"]

        liq_results = [self.aliq, self.vx_liq, self.ret_liq, self.re_liq, np.nan]
        gas_results = [self.agas, self.vx_gas, self.ret_gas, self.re_gas, self.drop_liq]

        sformat = "{:>9} | {:>8} | {:>8} | {:>8} \n"  # string format
        nformat = "{:>9} | {:>8} | {:>8.2f} | {:>8.2f} \n"  # number format
        re_format = "{:>9} | {:>8} | {:>8.0f} | {:>8.0f} \n"  # reynolds format
        spc = 43 * "-" + "\n"  # spacing
        pout = sformat.format("Tags", "Units", "Liquid", "Vapor") + spc
        for label, unit, liq, gas in zip(labels, units, liq_results, gas_results):
            if label == "Reynolds":
                pout += re_format.format(label, unit, liq, gas)
            else:
                pout += nformat.format(label, unit, liq, gas)
        print(pout)

    def terminal_lig(self, dm: float) -> float:
        """Terminal Velocity of Liquid in Gas

        Args:
            dm (float): Droplet Diameter, micron

        Returns:
            vt_liq (float): Terminal Velocity of Liquid in Gas, ft/s
        """
        dd = drp.micron_to_feet(dm)
        mu_gas = drp.centipoise_to_lbm(self.gas_props["viscosity"])
        vt_liq = drp.velocity_terminal(dd, self.liq_props["density"], self.gas_props["density"], mu_gas, self.g)
        return vt_liq


class SepThreePhase(SepMech):
    def __init__(
        self,
        vid: float,
        lss: float,
        leff: float,
        hoil: float,
        hwat: float,
        oil_props: dict,  # make these classes?
        wat_props: dict,
        gas_props: dict,
    ) -> None:
        """Two Phase Separator of Gas and Liquid

        Args:
            vid (float): Vessel Inner Diameter, feet
            lss (float): Length Seam to Seam, feet
            leff (float): Vessel Effective Length, feet
            hoil (float): Height of the Oil in Vessel, feet
            hwat (float): Height of the Water in Vessel, feet
            oil_props (dict): Oil Properties
            wat_props (dict): Water Properties
            gas_props (dict): Gas Properties
        """

        req_keys = {"mass_flow", "density", "viscosity"}
        fld.validate_props(oil_props, req_keys)
        fld.validate_props(wat_props, req_keys)
        fld.validate_props(gas_props, req_keys)

        self.vid = vid
        self.lss = lss
        self.leff = leff
        self.hoil = hoil
        self.hwat = hwat
        self.oil_props = oil_props
        self.wat_props = wat_props
        self.gas_props = gas_props

        aoil, awat, agas = vessel_area_three_phase(vid, hoil, hwat)
        dhyd_oil, dhyd_wat, dhyd_gas = vessel_dhyd_three_phase(vid, hoil, hwat)

        qoil = fld.volm_flow(oil_props["mass_flow"], oil_props["density"])
        qwat = fld.volm_flow(wat_props["mass_flow"], wat_props["density"])
        qgas = fld.volm_flow(gas_props["mass_flow"], gas_props["density"])

        vx_oil = fld.velocity_volm(qoil, aoil)
        vx_wat = fld.velocity_volm(qwat, awat)
        vx_gas = fld.velocity_volm(qgas, agas)

        ret_oil = fld.retention(leff, vx_oil)
        ret_wat = fld.retention(leff, vx_wat)
        ret_gas = fld.retention(leff, vx_gas)

        mu_oil = drp.centipoise_to_lbm(oil_props["viscosity"])  # proper units
        mu_wat = drp.centipoise_to_lbm(wat_props["viscosity"])
        mu_gas = drp.centipoise_to_lbm(gas_props["viscosity"])

        re_oil = fld.reynolds(vx_oil, oil_props["density"], dhyd_oil, mu_oil)
        re_wat = fld.reynolds(vx_wat, wat_props["density"], dhyd_wat, mu_wat)
        re_gas = fld.reynolds(vx_gas, gas_props["density"], dhyd_gas, mu_gas)

        dh_gas = vid - hoil  # differential height of gas
        dh_oil = hoil - hwat  # differential height of oil

        vt_oiw_req = hwat / (ret_wat * 60)  # terminal velocity required for oil in water
        vt_wio_req = dh_oil / (ret_oil * 60)  # terminal velocity required for water in oil
        vt_oig_req = dh_gas / (ret_gas * 60)  # terminal velocity required for oil in gas

        g = 32.174  # ft/s2
        drop_oiw = drp.droplet_diameter(vt_oiw_req, oil_props["density"], wat_props["density"], mu_wat, g)
        drop_wio = drp.droplet_diameter(vt_wio_req, wat_props["density"], oil_props["density"], mu_oil, g)
        drop_oig = drp.droplet_diameter(vt_oig_req, oil_props["density"], gas_props["density"], mu_gas, g)

        self.g = g
        self.aoil, self.awat, self.agas = aoil, awat, agas
        self.vx_oil, self.vx_wat, self.vx_gas = vx_oil, vx_wat, vx_gas
        self.re_oil, self.re_wat, self.re_gas = re_oil, re_wat, re_gas
        self.ret_oil, self.ret_wat, self.ret_gas = ret_oil, ret_wat, ret_gas
        self.drop_oiw = drp.feet_to_micron(drop_oiw)
        self.drop_wio = drp.feet_to_micron(drop_wio)
        self.drop_oig = drp.feet_to_micron(drop_oig)

    def results(self) -> None:
        """Show Results of the Two Phase Separator"""

        labels = ["X-Area", "Velocity", "Retention", "Reynolds", "Min_Drop"]
        units = ["ft2", "ft/s", "min", "none", "µm"]

        oil_results = [self.aoil, self.vx_oil, self.ret_oil, self.re_oil, self.drop_wio]
        wat_results = [self.awat, self.vx_wat, self.ret_wat, self.re_wat, self.drop_oiw]
        gas_results = [self.agas, self.vx_gas, self.ret_gas, self.re_gas, self.drop_oig]

        sformat = "{:>9} | {:>8} | {:>8} | {:>8} | {:>8} \n"  # string format
        nformat = "{:>9} | {:>8} | {:>8.2f} | {:>8.2f} | {:>8.2f} \n"  # number format
        re_format = "{:>9} | {:>8} | {:>8.0f} | {:>8.0f} | {:>8.0f} \n"  # reynolds format
        spc = 54 * "-" + "\n"  # spacing
        pout = sformat.format("Tags", "Units", "Oil", "Water", "Vapor") + spc
        for label, unit, oil, wat, gas in zip(labels, units, oil_results, wat_results, gas_results):
            if label == "Reynolds":
                pout += re_format.format(label, unit, oil, wat, gas)
            else:
                pout += nformat.format(label, unit, oil, wat, gas)
        print(pout)

    def coal_plate_length(self, dm: float, pgap: float = 0.75, angl: float = 45, pf: float = 0.6) -> float:
        """Coalescing Plate Length

        Calculates the length of coalescing plates required. Assumes the plates will be totally
        submerged inside water. Only looks at pulling droplets of oil out from water. Does not
        look at pulling droplets of water out from oil.

        Args:
            dm (float): Droplet Diameter, microns
            pgap (float): Gap Between Coalescing Plates, inches
            angl (float): Angle of Coalescing Plates off Horizontal, degrees
            pf (float): Performance Factor, adds fraction of extra length

        Returns:
            plen (float): Plate Length, feet
        """
        dd = drp.micron_to_feet(dm)
        vt_oil = drp.velocity_terminal(
            dd,
            self.oil_props["density"],
            self.wat_props["density"],
            drp.centipoise_to_lbm(self.wat_props["viscosity"]),
            32.174,
        )
        coal_len = drp.coal_plate_length(vt_oil, self.vx_wat)
        return coal_len
