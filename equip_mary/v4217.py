import numpy as np

from pysep.separator import SepThreePhase

# moose pad main sepration vessels

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
    "mass_flow": 3888,  # lbm/hr, 2 MMSCFD
    "density": 0.9444,  # lbm/ft3, 350 psig
    "viscosity": 1.327e-2,  # centipoise
    "drop_io": 140,  # micron, smallest droplet to be removed in the process, 140 can be caught by demister
    "drop_iw": 140,  # micron, smallest droplet to be removed
    "drop_ig": np.nan,
}

# primary dimensions
vid = 78.74 / 12  # feet
lss = 480 / 12  # feet
leff = 0.8 * lss
liq_frac = (78.74 / 2 + 23.556) / 78.74
print(f"Oil Height is {liq_frac:.3f}% of Total Height")
hoil = liq_frac * vid
hwat = (liq_frac - 0.1) * vid  # just 10% volume for water
hgas = vid - hoil

primary = SepThreePhase(vid, lss, leff, hoil, hwat, oil_props, wat_props, gas_props)
print(primary)
primary.results()

mawp = 1075  # psig
wall_thk = primary.shell_thick(mawp)
bare_wgt = primary.weight_bare(wall_thk)
xtra_wgt = 25000  # lbm, weight of vessel internals and nozzles
vssl_wgt = bare_wgt + xtra_wgt

print(f"Primary MAWP: {mawp} psig, Wall Thick: {round(wall_thk, 2)} inches, Weight: {round(vssl_wgt/2000, 2)} tons\n")

coal_len = primary.coal_plate_length(150, pf=0.0)
print(f"Length of the Coalescing Plate is {round(coal_len, 2)} ft")


# note, the V-5411 is around 10' in ID and 22' in length
