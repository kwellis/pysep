import numpy as np

from pysep.separator import SepThreePhase

oil_props = {
    "mass_flow": 1.374e04,  # lbm/hr, 1 MBOPD
    "density": 58.74,  # lbm/ft3
    "viscosity": 52,  # centipoise
    "drop_io": np.nan,
    "drop_iw": 200,  # micron, smallest oil droplet to be removed from water
    "drop_ig": 100,  # micron, oil in gas, 140 and below can be caught by demister pad
}

wat_props = {
    "mass_flow": 5.840e05 / 2,  # lbm/hr, 40 MBWPD
    "density": 62.46,  # lbm/ft3
    "viscosity": 0.75,  # centipoise
    "drop_io": 500,  # micron, smallest droplet to be removed in the process
    "drop_iw": np.nan,
    "drop_ig": 100,  # micron, water in gas, 140 and below can be caught by demister pad
}

gas_props = {
    "mass_flow": 8.646e02,  # lbm/hr, 0.5 MMSCFD
    "density": 0.069,  # lbm/ft3 (what pressure and temperature?)
    "viscosity": 1.327e-2,  # centipoise
    "drop_io": 140,  # micron, smallest droplet to be removed in the process, 140 can be caught by demister
    "drop_iw": 140,  # micron, smallest droplet to be removed
    "drop_ig": np.nan,
}

# primary dimensions
vid = 12  # feet
lss = 20  # feet
leff = 0.8 * lss
# liq_frac = 0.8
hoil = 7.2  # hhll is at seven feet
hwat = 7  # right at the "weir" height
hgas = vid - hoil

primary = SepThreePhase(vid, lss, leff, hoil, hwat, oil_props, wat_props, gas_props)
print(primary)
primary.results()

mawp = 125  # psig
wall_thk = primary.shell_thick(mawp)
bare_wgt = primary.weight_bare(wall_thk)
xtra_wgt = 25000  # lbm, weight of vessel internals and nozzles
vssl_wgt = bare_wgt + xtra_wgt

print(f"Primary MAWP: {mawp} psig, Wall Thick: {round(wall_thk, 2)} inches, Weight: {round(vssl_wgt/2000, 2)} tons\n")

coal_len = primary.coal_plate_length(100, pf=0.0)
print(f"Length of the Coalescing Plate is {round(coal_len, 2)} ft")
# the coalescing plate is small because the vessel ID is large, so you don't need thick plates
