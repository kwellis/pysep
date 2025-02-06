import numpy as np

from pysep.separator import SepThreePhase

# need to integrate woffl pvt properties into this for quicker lookup
# rates pulled on October 25th, doesn't include J-40...
j_pad_rate = {
    "oil": 3656,  # bpd
    "wat": 7500,  # bpd
    "gas": 293,  # mscfd
}

oil_props = {
    "mass_flow": 5.131e4,  # lbm/hr, 3566 BPD
    "density": 58.74,  # lbm/ft3, 100 PSIG and 120 deg F
    "viscosity": 52,  # centipoise
    "drop_io": np.nan,
    "drop_iw": 200,  # micron, smallest oil droplet to be removed from water
    "drop_ig": 100,  # micron, oil in gas, 140 and below can be caught by demister pad
}

wat_props = {
    "mass_flow": 1.11e5,  # lbm/hr, 7500 BPD
    "density": 62.46,  # lbm/ft3, 350 PSIG and 150 deg F, is this accurate?
    "viscosity": 0.75,  # centipoise
    "drop_io": 500,  # micron, smallest droplet to be removed in the process
    "drop_iw": np.nan,
    "drop_ig": 100,  # micron, water in gas, 140 and below can be caught by demister pad
}

gas_props = {
    "mass_flow": 583.2,  # lbm/hr, 0.3 MMSCFD
    "density": 0.9444,  # lbm/ft3 (300 psig, 95 deg F)
    "viscosity": 1.327e-2,  # centipoise
    "drop_io": 140,  # micron, smallest droplet to be removed in the process, 140 can be caught by demister
    "drop_iw": 140,  # micron, smallest droplet to be removed
    "drop_ig": np.nan,
}

# primary dimensions
vod = 3  # feet
wall_thk = 0.875 / 12  # feet
vid = 3 - 2 * wall_thk  # feet, this the ID, 9.5
x_area = np.pi * vid**2 / 4  # ft2, cross sectional area
vol = 360  # ft^3, vessel volume
lss = vol / x_area  # feet, actually 45 (for MEG, for similiar rates, we were looking at 45 feet...)
leff = 0.75 * lss  # how to account for weird angle?

liq_frac = 0.7
hoil = liq_frac * vid
hwat = (liq_frac - 0.2) * vid
hgas = vid - hoil

primary = SepThreePhase(vid, lss, leff, hoil, hwat, oil_props, wat_props, gas_props)
print(primary)
primary.results()

mawp = 675  # psig
wall_thk = primary.shell_thick(mawp)
bare_wgt = primary.weight_bare(wall_thk)
xtra_wgt = 5000  # lbm, weight of vessel internals and nozzles
vssl_wgt = bare_wgt + xtra_wgt

print(f"Primary MAWP: {mawp} psig, Wall Thick: {round(wall_thk, 2)} inches, Weight: {round(vssl_wgt/2000, 2)} tons\n")

coal_len = primary.coal_plate_length(150, pf=0.0)
print(f"Length of the Coalescing Plate is {round(coal_len, 2)} ft")


# note, the V-5411 is around 10' in ID and 22' in length
