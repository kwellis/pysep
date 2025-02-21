import numpy as np

from pysep.separator import SepThreePhase

# need to integrate woffl pvt properties into this for quicker lookup
j_pad_rate = {
    "oil": 8500,  # bpd
    "wat": 30000,  # bpd
    "gas": 1900,  # mscfd
}

oil_props = {
    "mass_flow": 1.19e5,  # lbm/hr, 8500 BPD
    "density": 59.88,  # lbm/ft3, 100 PSIG and 120 deg F
    "viscosity": 213,  # centipoise
    "drop_io": np.nan,
    "drop_iw": 200,  # micron, smallest oil droplet to be removed from water
    "drop_ig": 100,  # micron, oil in gas, 140 and below can be caught by demister pad
}

wat_props = {
    "mass_flow": 4.45e5,  # lbm/hr, 30000 BPD
    "density": 62.85,  # lbm/ft3, 350 PSIG and 150 deg F, is this accurate?
    "viscosity": 0.8,  # centipoise
    "drop_io": 500,  # micron, smallest droplet to be removed in the process
    "drop_iw": np.nan,
    "drop_ig": 100,  # micron, water in gas, 140 and below can be caught by demister pad
}

gas_props = {
    "mass_flow": 4.47e3,  # lbm/hr, 1.9 MMSCFD
    "density": 1.191,  # lbm/ft3 (350 psig, 95 deg F)
    "viscosity": 1.18e-2,  # centipoise
    "drop_io": 140,  # micron, smallest droplet to be removed in the process, 140 can be caught by demister
    "drop_iw": 140,  # micron, smallest droplet to be removed
    "drop_ig": np.nan,
}

# primary dimensions, same as F and E-POPS
vod = 10.5  # feet
wall_thk = 2.4 / 12  # feet
vid = vod - 2 * wall_thk  # feet, vessel inner diameter
lss = 40  # feet
leff = 0.8 * lss

hoil = (96 + 6) / 12
hwat = 96 / 12
hgas = vid - hoil

primary = SepThreePhase(vid, lss, leff, hoil, hwat, oil_props, wat_props, gas_props)
print(primary)
primary.results()

mawp = 700  # psig
wall_thk = primary.shell_thick(mawp)
bare_wgt = primary.weight_bare(wall_thk)
xtra_wgt = 5000  # lbm, weight of vessel internals and nozzles
vssl_wgt = bare_wgt + xtra_wgt

print(f"Primary MAWP: {mawp} psig, Wall Thick: {round(wall_thk, 2)} inches, Weight: {round(vssl_wgt/2000, 2)} tons\n")

coal_len = primary.coal_plate_length(50, pf=0.0)
print(f"Length of the Coalescing Plate is {round(coal_len, 2)} ft")


# note, the V-5411 is around 10' in ID and 22' in length
