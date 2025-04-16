import numpy as np

from pysep.fluids import liquid_props
from pysep.separator import SepTwoPhase

# moose pad degasser

oil_props = {
    "mass_flow": 1.407e5,  # lbm/hr, 10 MBOPD
    "density": 58.74,  # lbm/ft3, 100 PSIG and 120 deg F
    "viscosity": 52,  # centipoise
    "drop_io": np.nan,
    "drop_iw": 200,  # micron, smallest oil droplet to be removed from water
    "drop_ig": 100,  # micron, oil in gas, 140 and below can be caught by demister pad
}

wat_props = {
    "mass_flow": 7.41e5 * 6 / 5,  # lbm/hr, 50 MBWPD
    "density": 62.46,  # lbm/ft3, 350 PSIG and 150 deg F, is this accurate?
    "viscosity": 0.75,  # centipoise
    "drop_io": 500,  # micron, smallest droplet to be removed in the process
    "drop_iw": np.nan,
    "drop_ig": 100,  # micron, water in gas, 140 and below can be caught by demister pad
}

gas_props = {
    "mass_flow": 3888 * 3 / 2,  # lbm/hr, 2 MMSCFD
    "density": 0.9444,  # lbm/ft3, 350 psig
    "viscosity": 1.327e-2,  # centipoise
    "drop_io": 140,  # micron, smallest droplet to be removed in the process, 140 can be caught by demister
    "drop_iw": 140,  # micron, smallest droplet to be removed
    "drop_ig": np.nan,
}

# degasser dimensions
vid = 84 / 12  # feet, this is probably the OD, not the ID
lss = 192 / 12  # feet
leff = 0.8 * lss
hliq = 0.55 * vid  # half full with gas
hgas = vid - hliq

liq_props = liquid_props(oil_props, wat_props)

degasser = SepTwoPhase(vid, lss, leff, hliq, liq_props, gas_props)
print(degasser)
degasser.results()

mawp = 800  # psig
wall_thk = degasser.shell_thick(mawp)
bare_wgt = degasser.weight_bare(wall_thk)
xtra_wgt = 25000  # lbm, weight of vessel internals and nozzles
vssl_wgt = bare_wgt + xtra_wgt

print(f"Degasser MAWP: {mawp} psig, Wall Thick: {round(wall_thk, 2)} inches, Weight: {round(vssl_wgt/2000, 2)} tons\n")
