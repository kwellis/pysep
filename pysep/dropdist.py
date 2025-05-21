"""Droplet Distribution"""

import math

import matplotlib.pyplot as plt
import numpy as np
from scipy import special, stats


def dmax_into_d50(dmax: float, dmax_perc: float = 0.99, gsd: float = 1.59) -> float:
    """Estimate d50 from dmax

    Assumes that dmax is at the 99th perentile, the following function will
    reverse calculate what the d50 would need to be with a specified geometric
    standard deviation. Paper by Paolinelli, Rashedi and Yao states that a gsd
    of 1.59 can be used in place of quantitative data. "Characterization of droplet
    sizes in large scale oil-water downstream from globe valve".

    Args:
        dmax (float): Maximum droplet in the distribution, microns
        dmax_perc (float): Max droplet perctile
        gsd (float): Geometric Standard Deviation

    Returns:
        d50 (float): Median droplet diameter in distribution, microns
    """
    if not (0 < dmax_perc < 1):
        raise ValueError("Percentile must be between 0 and 1.")

    z = special.erfinv(2 * dmax_perc - 1)
    ln_d50 = math.log(dmax) - z * math.sqrt(2) * math.log(gsd)
    return math.exp(ln_d50)


def log_normal_pdf(dmin: np.ndarray, d50: float, gsd: float) -> np.ndarray:
    """Log Normal PDF for Droplet Diameters

    This is just the count of each droplet, it hasn't converted to to a weighted
    volumetric distribution. Converting to a volumetric distribution is important
    since a single 1000 micron droplet has more oil than multiple 100 micron droplets.

    Args:
        dmin (float): Minimum droplet size cutoff, microns
        d50 (float): Median droplet diameter in distribution, microns
        gsd (float): Geometric Standard Deviation

    Returns:
        frac (float): Fraction of oil smaller than dmin
    """
    sigma = math.log(gsd)
    return (1 / (dmin * sigma * np.sqrt(2 * np.pi))) * np.exp(-((np.log(dmin) - np.log(d50)) ** 2) / (2 * sigma**2))


def count_cdf(dcut: float, d50: float, gsd: float = 1.59) -> float:
    """Count Weighted Cumulative Distribution Function

    Calculate the percentage of values left over after removing all the droplets
    that are larger than dmin. The following is only counting the number of each
    droplet instead of looking at the volumetric / weight percentage contained in
    the various droplet distributions.
    References: "Characterization of droplet sizes in large scale oil-water downstream from globe valve".
    2017 Paolinelli, Rashedi and Yao

    Args:
        dcut (float): Minimum droplet size cutoff, microns
        d50 (float): Median droplet diameter in distribution, microns
        gsd (float): Geometric Standard Deviation

    Returns:
        frac (float): Fraction of oil smaller than dmin
    """
    if dcut <= 0 or d50 <= 0 or gsd <= 0:
        raise ValueError("All inputs must be positive.")

    z = (math.log(dcut) - math.log(d50)) / (math.sqrt(2) * math.log(gsd))
    return 0.5 * (1 + math.erf(z))


def volume_cdf(dcut: float, d50: float, gsd: float = 1.59) -> float:
    """Volume Weighted Cumulative Distribution Function

    Args:
        dcut (float): Droplet size cutoff, microns
        d50 (float): Median droplet diameter in distribution, microns
        gsd (float): Geometric Standard Deviation

    Returns:
        frac (float): Fraction of oil volume in droplets smaller than dcut
    """
    d_ray = np.logspace(np.log10(d50 / 20), np.log10(d50 * 5), 2000)
    num_pdf = stats.lognorm.pdf(d_ray, s=np.log(gsd), scale=d50)  # number pdf
    num_cdf = np.cumsum(num_pdf)
    num_cdf_norm = num_cdf / num_cdf[-1]

    vol_pdf = d_ray**3 * num_pdf
    vol_cdf = np.cumsum(vol_pdf)
    vol_cdf_norm = vol_cdf / vol_cdf[-1]  # normalized cdf

    plt.plot(d_ray, vol_cdf_norm, label="Vol-CDF", color="blue")
    plt.plot(d_ray, num_cdf_norm, label="Num-CDF", color="green")
    plt.legend()
    plt.show()

    return np.interp(dcut, d_ray, vol_cdf_norm)


if __name__ == "__main__":
    dmax = 600
    d50 = dmax_into_d50(dmax)

    # print(f"Number CDF Left: {count_cdf(350, d50):.3f}")
    # print(f"Volume CDF Left: {volume_cdf(350, d50):.3f}")

    wat_initial = 1.606e06  # lbm/hr, 110 MBWPD
    oil_initial = 6.871e05  # lbm/hr, 50 MBOPD
    oil_mass_frac_begin = oil_initial / wat_initial
    oil_perc_left = count_cdf(350, d50)  # at 350, its 8%
    oil_perc_left = volume_cdf(350, d50)
    # this calculates roughly 1.7%, which is close to mysep calculation
    oil_left = oil_initial * oil_perc_left

    oil_mass_frac_left = oil_left / wat_initial

    print(f"Initial Oil Mass Fraction: {oil_mass_frac_begin*100:.3f}%")
    print(f"After Oil Mass Fraction: {oil_mass_frac_left*100:.3f}%")

    # dmin = 10
    # d_ray = np.linspace(dmin, dmax, 100)

    # p_ray = np.asarray([count_cdf(x, d50) for x in d_ray])

    # plt.plot(d_ray, p_ray)
    # plt.show()

    # print(d50)
    # print(log_norm_cum_dist_func(150, 500))
