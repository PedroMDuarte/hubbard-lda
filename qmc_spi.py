
"""
This file provides a way to calculate the bulk spin structure factor
from a given density distribution. 

The idea is to calculate the n(r) using NLCE then pass it over to 
QMC to get Spi
"""

import numpy as np

import matplotlib.pyplot as plt
import matplotlib
from matplotlib import rc
rc('font', **{'family':'serif'})
rc('text', usetex=True)

from scipy.spatial import Delaunay
from scipy.interpolate import CloughTocher2DInterpolator, LinearNDInterpolator
from scipy.interpolate.interpnd import _ndim_coords_from_arrays

import qmc

from scipy import integrate

def integrate_sphere( r, qty):
    q = qty[ ~np.isnan(qty)]
    r = r[ ~np.isnan(qty) ]
    a = 1.064/2.
    return np.power( a,-3) * 2*np.pi * integrate.simps( q*(r**2), r)
    # Notice that the integral above is 2pi rather than 4pi because the
    # radial quantity q is defined for negative and positive radii, so 
    # the radial integral has an implicit factor of 2. 


def spi_bulk( r111, n111, T, t111, U111, **kwargs ): 
    """
    This function is used to calculate  the bulk
    spin structure factor using the QMC data
    """  

    # The max U and min t are used 
    U = U111.max()
    t = t111.min() 
    print "Calculating Spi_Bulk for " + \
          "U={:0.2f}, T={:0.2f}".format(U/t, T/t)

    inhomog = kwargs.get('inhomog', False) 

    spi = [] 
    for i,n in enumerate(n111):
        # The corrrect thing to do here is 
        if inhomog == True:
            Uval = U111[i]/t111[i] 
            Tval = T/t111[i] 
        # But since we do not have enough QMC data yet 
        # we are sticking with a single U and T value
        else:
            Uval = U/t 
            Tval = T/t 

        title_text = r'$(U/t)_{{0}}={:0.2f}$,\ '.format(Uval) \
            + '$(T/t)_{{0}}={:0.2f}$,\ $n={:.2f}$'.format(Tval,n) + '\n'
        result = qmc.find_closest_qmc( U=Uval, T=Tval, n=n, \
                              title_text = title_text)
        if result is None:
            print "Had problems finding Spi for " +  \
              " U={:02d}, T={:0.2f}".format(int(Uval), Tval)
            continue
        spi.append( result )
    spi = np.array(spi)

    number = integrate_sphere( r111, n111 ) 
    spibulk =  integrate_sphere( r111, spi * n111) / number 

    return spibulk, spi



