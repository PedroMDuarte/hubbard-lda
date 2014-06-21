
"""
This file provides a way to obtain thermodynamic quantities from an 
interpolation of available QMC solutions 
"""

import numpy as np

import matplotlib.pyplot as plt
import matplotlib

from matplotlib import rc
rc('font', **{'family':'serif'})
rc('text', usetex=True)

import glob 
import os 

from scipy.spatial import Delaunay
from scipy.interpolate import CloughTocher2DInterpolator, LinearNDInterpolator
from scipy.interpolate.interpnd import _ndim_coords_from_arrays


def find_closest_qmc( U=8, T=0.67, n=1.0, **kwargs):
    """
    This function finds the closest values of U and T in the QMC data 
    that straddle the values U and T given as arguments.
    
    Notice that this one searches by density rather than by chemical
    potential.  The NLCE find closest searches by chemical potential. 
    """
    
    #datadir = '/home/pmd/sandbox/hubbard-lda/QMC_Final/'
    datadir = '/home/pmd/sandbox/hubbard-lda/COMBINED_Final/'
    
    fname = datadir + 'U*'
    us = [ float(u.split('/U')[-1]) for u in glob.glob(fname) ] 
    du = [ np.abs(U-u) for u in us ]
    index = np.argsort(du)
    us = [ us[index[i]] for i in range(4)] 
    #print us
    #print du
    #print index
    #print "Closest Us = ", us
    
    datfiles = []
    for u in us:    
    
        # For the Spi and Stheta data 
        fname = datadir + 'U{U:02d}/T*dat'.format(U=int(u))
        fs = sorted(glob.glob(fname))
        Ts = [ float(f.split('T')[1].split('.dat')[0]) for f in fs ]

        Ts_g = [] ; Ts_l = []; 
        for t in Ts:
            if t > T:
                Ts_g.append(t) 
            else:
                Ts_l.append(t) 
        
        order_g = np.argsort( [ np.abs( T -t ) for t in Ts_g ] )
        order_l = np.argsort( [ np.abs( T -t ) for t in Ts_l ] )

        try:
            Tpts = [ Ts_g[ order_g[0]] , Ts_l[ order_l[0]]   ] 
        except:
            print 
            print "problem adding U=",u, "T=",Ts
            print "available T data does not stride the point"
            print "T  =", T
            print "Ts =", Ts
            print  
            raise ValueError("QMC data not available.")


        dT = [ np.abs( T - t) for t in Ts ] 
        index = np.argsort(dT)
        for i in range( min(3, len(Ts))):
            Tnew = Ts[index[i]] 
            if Tnew not in Tpts:
                Tpts.append(Tnew) 
        for Tpt in Tpts: 
            index = Ts.index( Tpt )  
            try:
                datfiles.append( [ fs[ index ], u, Ts[index] ] ) 
            except:
                print "problem adding U=",u, "T=",Ts
                raise
          

        # Need to make sure that selected T values stride both
        # sides of the point 
        
        #print
        #print u
        #print Ts
        #print dT
        #print index
        #print fs

#        for i in range(min(3, len(Ts))):
#            try:
#                datfiles.append( [ fs[index[i]], u, Ts[index[i]] ] ) 
#            except:
#                print "problem adding U=",u, "T=",Ts
#                raise
#        
            #datfiles.append( [ fs[index[1]], u, Ts[index[1]] ] ) 
        
    #print datfiles
    DENSCOL = 1 
    SPICOL = 3 
    SPIERR = 4
    STHCOL = 5 
    STHERR = 6 

    # Control the interpolation between availble
    # density points here 
    #~spinterp = 'nearest' 
    spinterp = 'linear' 
       
 
    basedat = []
    for f in datfiles:
        # f[0] is the datafile name
        # f[1] is U
        # f[2] is T 
#        try:
            dat = np.loadtxt( f[0], skiprows=1 ) 
            if spinterp == 'nearest':
                index = np.argmin( np.abs(dat[:, DENSCOL] - n )) 
                basedat.append( [f[1], f[2], dat[index, SPICOL]] )
            else:
                # find the two closest densities that stride the point  
                densdat = dat[:,DENSCOL] 

                # since the densities are ordered we can do:
                index0 = np.where( densdat <= n )[0][-1]     
                index1 = np.where( densdat >  n )[0][0] 
               
                spi0 = dat[ index0, SPICOL ] 
                spi1 = dat[ index1, SPICOL ] 
   
                dens0 = dat[ index0, DENSCOL ] 
                dens1 = dat[ index1, DENSCOL ]

                spiresult =  spi0 +  (n-dens0) * (spi1-spi0) / (dens1-dens0) 
                basedat.append( [f[1], f[2], spiresult] )

                print
                print "U={:02d}, T={:0.2f}".format( int(f[1]), f[2] )
                print "  dens = ", n
                print "index0 = ", index0
                print "index1 = ", index1
                print "Doing linear interpolation for Spi"
                print " dens0 = ", dens0
                print " dens1 = ", dens1
                print "  Spi0 = ", spi0
                print "  Spi1 = ", spi1
                print "spiresult = ", spiresult
                raise
#        except Exception as e :
#            print "Failed to get data from file = ", f
#            raise e 

    basedat =   np.array(basedat)
    points = _ndim_coords_from_arrays(( basedat[:,0] , basedat[:,1]))
    #print "Closest dat = ", basedat
    
    
    #finterp = CloughTocher2DInterpolator(points, basedat[:,2])
    finterp = LinearNDInterpolator( points, basedat[:,2] )
        
    error = False
    try:
        result = finterp( U,T )
        if np.isnan(result):
            raise Exception("!!!! Invalid result !!!!\n")
    except Exception as e:
        print e
        error = True
        
    if error or kwargs.get('showinterp',False):
        print "Interp points:"
        print basedat
        
        tri = Delaunay(points)
        fig = plt.figure( figsize=(3.5,3.5))
        gs = matplotlib.gridspec.GridSpec( 1,1 ,\
                left=0.15, right=0.96, bottom=0.12, top=0.88)
        ax = fig.add_subplot( gs[0] )
        ax.grid(alpha=0.5)
        ax.triplot(points[:,0], points[:,1], tri.simplices.copy())
        ax.plot(points[:,0], points[:,1], 'o')
        ax.plot( U, T, 'o', ms=6., color='red')
        xlim = ax.get_xlim()
        dx = (xlim[1]-xlim[0])/10.
        ax.set_xlim( xlim[0]-dx, xlim[1]+dx )
        ylim = ax.get_ylim()
        dy = (ylim[1]-ylim[0])/10.
        ax.set_ylim( ylim[0]-dy, ylim[1]+dy )
        ax.set_xlabel('$U/t$')
        ax.set_ylabel('$T/t$',rotation=0,labelpad=8)
        
        tt = kwargs.get('title_text','')
        ax.set_title( tt + '$U/t={:.2f}$'.format(U) + \
                      ',\ \ ' + '$T/t={:.2f}$'.format(T), \
                ha='center', va='bottom', fontsize=10)
        save_err = kwargs.get('save_err',None) 
        if save_err is not None:
            print "Saving png." 
            fig.savefig( save_err, dpi=300)
        plt.show()
        raise ValueError("Could not interpolate using QMC data.")
    
    return result

        
        
