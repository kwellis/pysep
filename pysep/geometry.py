import math


def hydraulic_diameter(a: float, wp: float) -> float:
    """Hydraulic Diameter of Non-Filled Pipe

    According to Perry ChemE handbook Edition 9 Page 15-88
    "and Dh is the hydraulic diameter of the continuous phase layer, given
    by 4*flow area / perimeter of flow channel, including the interface".

    Args:
        a (float): Area Filled, ft2
        wp (float): Wetted Perimeter Filled, ft

    Returns:
        dhyd (float): Hydraulic Diameter, ft
    """
    return 4 * a / wp


def circle_segment_area(h: float, r: float) -> float:
    """Cross Sectional Area of Circular Segment

    The following is only valid for segments that are less than 50% full.

    Args:
        h (float): Height of the Liquid in the Vessel, feet or meters
        r (float): Radius of the Vessel, feet or meters

    Returns:
        a (float): Area of the Segment, ft2 or m2
    """
    if h > r:
        raise ValueError("Height must be less than radius for circle segment")
    a = r**2 * math.acos(1 - (h / r)) - (r - h) * math.sqrt(r**2 - (r - h) ** 2)
    return a


def circle_segment_perimeter(h: float, r: float) -> float:
    """Perimeter of Circular Segment

    The following is only valid for segments that are less than 50% full.

    Args:
        h (float): Height of the Liquid in the Vessel, feet or meters
        r (float): Radius of the Vessel, feet or meters

    Returns:
        p (float): Perimeter of the Segment, ft or m
    """
    if h > r:
        raise ValueError("Height must be less than radius for circle segment")
    p = r * 2 * math.acos((r - h) / r)
    return p


def circle_chord_length(h: float, r: float) -> float:
    """Chord Length of Circle Segment

    Used for calculating wetted perimeter in a vessel.

    Args:
        h (float): Height of the Liquid in the Vessel, feet or meters
        r (float): Radius of the Vessel, feet or meters

    Returns:
        c (float): Chord Length Across Circle, ft or m
    """
    if h > r:
        raise ValueError("Height must be less than radius for circle segment")
    c = 2 * math.sqrt(r**2 - (r - h) ** 2)
    return c


def vessel_area_three_phase(vid: float, hoil: float, hwat: float) -> tuple[float, float, float]:
    """Area of oil, water and gas in a horizontal vessel

    Args:
        vid (float): Vessel Inner Diameter, feet
        hoil (float): Height of the Oil in the Vessel, feet
        hwat (float): Height of the Water in the Vessel, feet

    Returns:
        aoil (float): Area of the Oil, ft2
        awat (float): Area of the Water, ft2
        agas (float): Area of the Gas, ft2"""

    if hwat > hoil:
        raise ValueError("Oil height must be less than water height")
    if hoil > vid:
        raise ValueError("Oil height must be less than vessel diameter")

    r = vid / 2  # radius
    atot = math.pi * r**2

    if hwat <= r:  # if less than or equal to 50% full
        awat = circle_segment_area(hwat, r)
    else:  # if above 50% full
        hwat = vid - hwat  # calculate the other side
        awat = atot - circle_segment_area(hwat, r)

    hgas = vid - hoil  # height of the gas, measured from the top down
    if hgas <= r:  # if less than or equal to 50% full
        agas = circle_segment_area(hgas, r)
    else:  # if above 50% full from the top down
        hgas = vid - hgas  # calculate the other side
        agas = atot - circle_segment_area(hgas, r)

    aoil = atot - awat - agas
    return aoil, awat, agas


def vessel_perim_three_phase(vid: float, hoil: float, hwat: float) -> tuple[float, float, float]:
    """Wetted Perimeter of oil, water and gas in a horizontal vessel

    Args:
        vid (float): Vessel Inner Diameter, feet
        hoil (float): Height of the Oil in the Vessel, feet
        hwat (float): Height of the Water in the Vessel, feet

    Returns:
        wp_oil (float): Wetted Perimeter of the Oil, ft
        wp_wat (float): Wetted Perimeter of the Water, ft
        wp_gas (float): Wetted Perimeter of the Gas, ft
    """
    if hwat > hoil:
        raise ValueError("Oil height must be less than water height")
    if hoil > vid:
        raise ValueError("Oil height must be less than vessel diameter")

    r = vid / 2  # radius
    pm_tot = math.pi * 2 * r  # perimeter of a normal circle

    if hwat <= r:  # if less than or equal to 50% full
        pm_wat = circle_segment_perimeter(hwat, r)
        ch_wat = circle_chord_length(hwat, r)
    else:  # if above 50% full
        hwat = vid - hwat  # calculate the other side
        pm_wat = pm_tot - circle_segment_perimeter(hwat, r)
        ch_wat = circle_chord_length(hwat, r)

    hgas = vid - hoil  # height of the gas, measured from the top down
    if hgas <= r:  # if less than or equal to 50% full
        pm_gas = circle_segment_perimeter(hgas, r)
        ch_gas = circle_chord_length(hgas, r)
    else:  # if above 50% full from the top down
        hgas = vid - hgas  # calculate the other side
        pm_gas = pm_tot - circle_segment_perimeter(hgas, r)
        ch_gas = circle_chord_length(hgas, r)

    pm_oil = pm_tot - pm_wat - pm_gas

    wp_oil = pm_oil + ch_wat + ch_gas
    wp_wat = pm_wat + ch_wat
    wp_gas = pm_gas + ch_gas
    return wp_oil, wp_wat, wp_gas


def vessel_dhyd_three_phase(vid: float, hoil: float, hwat: float) -> tuple[float, float, float]:
    """Hydraulic Diameter of oil, water and gas in a horizontal vessel

    Args:
        vid (float): Vessel Inner Diameter, feet
        hoil (float): Height of the Oil in the Vessel, feet
        hwat (float): Height of the Water in the Vessel, feet

    Returns:
        dhyd_oil (float): Hydraulic Diameter of the Oil, ft2
        dhyd_wat (float): Hydraulic Diameter of the Water, ft2
        dhyd_gas (float): Hydraulic Diameter of the Gas, ft2
    """
    aoil, awat, agas = vessel_area_three_phase(vid, hoil, hwat)
    wpoil, wpwat, wpgas = vessel_perim_three_phase(vid, hoil, hwat)
    dhyd_oil = hydraulic_diameter(aoil, wpoil)
    dhyd_wat = hydraulic_diameter(awat, wpwat)
    dhyd_gas = hydraulic_diameter(agas, wpgas)
    return dhyd_oil, dhyd_wat, dhyd_gas


def vessel_area_two_phase(vid: float, hliq: float) -> tuple[float, float]:
    """Area of liquid and gas in a horizontal vessel

    Args:
        vid (float): Vessel Inner Diameter, feet
        hliq (float): Height of the Liquid in the Vessel, feet

    Returns:
        aliq (float): Area of the Liquid, ft2
        agas (float): Area of the Gas, ft2"""

    if hliq > vid:
        raise ValueError("Liquid height must be less than vessel diameter")

    r = vid / 2  # radius
    atot = math.pi * r**2

    if hliq <= r:  # if less than or equal to 50% full
        aliq = circle_segment_area(hliq, r)
    else:  # if above 50% full
        hliq = vid - hliq  # calculate the other side
        aliq = atot - circle_segment_area(hliq, r)

    agas = atot - aliq
    return aliq, agas


def vessel_perim_two_phase(vid: float, hliq: float) -> tuple[float, float]:
    """Wetted Perimeter of liquid and gas in a horizontal vessel

    Args:
        vid (float): Vessel Inner Diameter, feet
        hliq (float): Height of the Liquid in the Vessel, feet

    Returns:
        wpliq (float): Wetted Perimeter of the Liquid, ft2
        wpgas (float): Wetted Perimeter of the Gas, ft2
    """
    if hliq > vid:
        raise ValueError("Liquid height must be less than vessel diameter")

    r = vid / 2  # radius
    pm_tot = math.pi * 2 * r  # perimeter of a normal circle

    if hliq <= r:  # if less than or equal to 50% full
        pm_liq = circle_segment_perimeter(hliq, r)
        ch_liq = circle_chord_length(hliq, r)
    else:  # if above 50% full
        hliq = vid - hliq  # calculate the other side
        pm_liq = pm_tot - circle_segment_perimeter(hliq, r)
        ch_liq = circle_chord_length(hliq, r)

    pm_gas = pm_tot - pm_liq
    wp_liq = pm_liq + ch_liq
    wp_gas = pm_gas + ch_liq
    return wp_liq, wp_gas


def vessel_dhyd_two_phase(vid: float, hliq: float) -> tuple[float, float]:
    """Hydraulic Diameter of liquid and gas in horizontal vessel

    Args:
        vid (float): Vessel Inner Diameter, feet
        hliq (float): Height of the Liquid in the Vessel, feet

    Returns:
        dhyd_liq (float): Hydraulic Diameter of the Liquid, ft
        dhyd_gas (float): Hydraulic Diameter of the Gas, ft
    """
    aliq, agas = vessel_area_two_phase(vid, hliq)
    wpliq, wpgas = vessel_perim_two_phase(vid, hliq)
    dhyd_liq = hydraulic_diameter(aliq, wpliq)
    dhyd_gas = hydraulic_diameter(agas, wpgas)
    return dhyd_liq, dhyd_gas
