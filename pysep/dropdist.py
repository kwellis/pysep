"""Droplet Distribution"""

import math

from scipy.special import erfinv


def dmax_into_d50(dmax: float, dmax_perc: float = 0.99, gsd: float = 2.0) -> float:
    """Estimate d50 from dmax

    Assumes that dmax is at the 99.9 perentile, the following function will
    reverse calculate what the d50 would need to be with a specified geometric
    standard deviation.

    Args:
        dmax (float): Maximum droplet in the distribution, microns
        dmax_perc (float): Max droplet perctile
        gsd (float): Geometric Standard Deviation

    Returns:
        d50 (float): Median droplet diameter in distribution, microns
    """
    if not (0 < dmax_perc < 1):
        raise ValueError("Percentile must be between 0 and 1.")

    z = erfinv(2 * dmax_perc - 1)
    ln_d50 = math.log(dmax) - z * math.sqrt(2) * math.log(gsd)
    return math.exp(ln_d50)


def log_norm_cum_dist_func(dmin: float, d50: float, gsd: float = 2.0) -> float:
    """Log Normal Cumulative Distribution Function

    Calculate the percentage of values left over after removing all the droplets
    that are larger than dmin.

    Args:
        dmin (float): Minimum droplet size cutoff, microns
        d50 (float): Median droplet diameter in distribution, microns
        gsd (float): Geometric Standard Deviation

    Returns:
        frac (float): Fraction of oil smaller than dmin
    """
    if dmin <= 0 or d50 <= 0 or gsd <= 0:
        raise ValueError("All inputs must be positive.")

    z = (math.log(dmin) - math.log(d50)) / (math.sqrt(2) * math.log(gsd))
    return 0.5 * (1 + math.erf(z))


if __name__ == "__main__":
    d50 = dmax_into_d50(2000, 0.99, 2)
    print(d50)
    # print(log_norm_cum_dist_func(150, 500))
