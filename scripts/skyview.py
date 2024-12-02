"""
    Description: Plot the Sky region for a given RA and DEC.

    Author: Ramon Gargalhone <ramones@ita.br>
    @ Instituto Tecnologico de Aeronautica - ITA

    Usage: python plot_skyview.py --ra="20:32:54" --dec="-22:32:22"
    Hint: Use = when using the + or - signs for declination

"""

import matplotlib.pyplot as plt

import astropy.units as u
from astropy.coordinates import SkyCoord

from astroplan.plots import plot_finder_image
from astroplan import FixedTarget

import argparse

def plot_skyview(ra, dec, fov, display=False):
    tg = FixedTarget(coord=SkyCoord(ra=ra, dec=dec, unit=(u.hourangle, u.deg)))

    fig, ax = plt.subplots()

    ax, hdu = plot_finder_image(tg, fov_radius=(fov/2)*u.arcmin)
    if display:
        plt.show()

    return fig

def main():
    parser = argparse.ArgumentParser(description="Plots the SkyView given RA and DEC")
    
    parser.add_argument(
        '--ra', '-r',
        type=str,
        default="12h 39m 59.4314s",
        help="Right Ascension in format hh:mm:ss"
    )

    parser.add_argument(
        '--dec', '-d',
        type=str,
        default="−11d 37m 23.118s",
        help="Declination in format hh:mm:ss"
    )

    parser.add_argument(
        '--fov',
        type=float,
        default=11,
        help="FOV in arcmin"
    )

    args = parser.parse_args()
    ra = args.ra
    dec = args.dec
    fov = args.fov
    plot_skyview(ra, dec, fov, display=True)

if __name__ == "__main__":
    main()