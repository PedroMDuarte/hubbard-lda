
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


def spi_bulk( r111, n111, mu111, T, t111, U111, **kwargs ): 
    """
    This function is used to calculate  the bulk
    spin structure factor using the QMC data
    """  

    # The max U and min t are used 
    U = U111.max()
    t = t111.min() 
    print "Calculating Spi_Bulk for " + \
          "U={:0.2f}, T={:0.2f}".format(U/t, T/t)
    print "Central chemical potential = ", mu111.max()

    inhomog = kwargs.get('inhomog', False)
    spiextents = kwargs.get('spiextents', 100.) 
    entextents = kwargs.get('entextents', 100.) 

    #subset = np.where( np.abs(r111) < spiextents )[0] 

    spi = np.ones_like( mu111 ) 
    entropy = np.zeros_like( mu111 ) 
    density = np.zeros_like( mu111 )  

    posr111 = np.abs(r111) 
 
#    for i in subset:
    for i in range(len(r111)):
        mu = mu111[i] 
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
            + '$(T/t)_{{0}}={:0.2f}$,\ $\mu={:.2f}$,\ $r={:.2f}$'.\
                       format(Tval,mu,r111[i]) + '\n'
        

        if posr111[i] <= spiextents:
            # Find the Spi
            result = qmc.find_closest_qmc( U=Uval, T=Tval, mu=mu, \
                         title_text = title_text, radius=r111[i] )
            if result is None:
                print "Had problems finding Spi for " +  \
                  " U={:02d}, T={:0.2f}".format(int(Uval), Tval)
                continue
            spi[ i ] =  result

            # Find the density 
            result = qmc.find_closest_qmc( U=Uval, T=Tval, mu=mu, \
                                  title_text = title_text, \
                         QTY='density', radius=r111[i], error_nan=True)
            if result == 'out-of-bounds':
                density[ i ] = np.nan
                continue 
            elif result is None:
                print "Had problems finding Density for " +  \
                  " U={:0.2f}, T={:0.2f}".format(Uval, Tval)
                continue
            density[ i ] =  result

        else:
            density[ i ] = np.nan 

   
        if posr111[i] <= entextents:
            # Find the entropy 
            result = qmc.find_closest_qmc( U=Uval, T=Tval, mu=mu, \
                         title_text = title_text, radius=r111[i],\
                         QTY='entropy', error_nan=True)
            if result is None:
                print "Had problems finding Entropy for " +  \
                  " U={:0.2f}, T={:0.2f}".format(Uval, Tval)
                continue
            entropy[ i ] =  result 

            if r111[i] > 20. and mu < 0. and result > 0.3:
                print '==== ALERT HIGH ENTROPY ====' 
                print 'r={:.1f}, U={:0.2f}, T={:0.3f}, mu={:0.3f}'.\
                      format(r111[i],Uval, Tval, mu),
                print '  ==> s={:0.2f}'.format( float(result ) )

            
        else: 
            entropy[ i ] = np.nan
 

    number = integrate_sphere( r111, n111 ) 
    spibulk =  integrate_sphere( r111, spi * n111) / number 
    overall_entropy = integrate_sphere( r111, entropy ) / number

    lda_number = integrate_sphere( r111, density ) 

    return spibulk, spi, overall_entropy, entropy, lda_number, density



