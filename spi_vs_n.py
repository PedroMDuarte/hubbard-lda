
import numpy as np
import matplotlib.pyplot as plt
import matplotlib 

import scubic
import lda
    


def Spi_vs_N( aS=200., Spi_inhomog=False, Tspi=0.9):

    s       = 7.
    g       = 3.666
    wIR     = 47.
    wGR     = 47./1.175
    T       = 0.035
    extents = 30.
    direc   = '111'
    mu0     = 'halfMott'

    spis = [] 
    select = 'nlce'

    for tag, muPlus in enumerate([-0.15, -0.075, 0., 0.10, 0.2, 0.25, 0.3]):
        print 
        print "muPlus = ", muPlus
        pot = scubic.sc(allIR=s, allGR=g, allIRw=wIR, allGRw=wGR)

        lda0 = lda.lda(potential = pot, Temperature=T, a_s=aS, extents=extents, \
                       globalMu=mu0, halfMottPlus=muPlus,\
                       verbose=True, \
                       select = select,\
                       ignoreExtents=False, ignoreSlopeErrors=True, \
                       ignoreMuThreshold=True)

        spibulk, spi, r111, n111, U111, t111 = \
            lda0.getBulkSpi(Tspi=Tspi, inhomog=Spi_inhomog)

        spis.append( {'SpiBulk':spibulk,\
                      'spi111':spi,\
                      'r111':r111,\
                      'n111':n111,\
                      'U111':U111,\
                      't111':t111,\
                      'Number':lda0.Number,\
                      'Tn':T,\
                      'Tspi':Tspi,\
                      } ) 

        # Figure to check inhomogeneity
        fig111, binresult, peak_dens, radius1e, peak_t, output = \
            lda.CheckInhomog( lda0, closefig = True, n_ylim=(-0.1,2.0) ) ;

        figfname = 'dataplots/Basic05/{:0.3f}gr_{:03d}_{}_T{:0.4f}Er.png'.\
                   format(g,tag,select,T)

        fig111.savefig(figfname, dpi=300)

    plot_spis( spis, inhomog=Spi_inhomog)



def plot_spis( spis,  inhomog=False):
    """ This function makes a nice plot of the results of 
    the studies of Spi_vs_n""" 

    from matplotlib import rc
    rc('font', **{'family':'serif'})
    rc('text', usetex=True)

    fig = plt.figure(figsize=(7.,4))
    gs = matplotlib.gridspec.GridSpec(2,3,\
            wspace=0.45, hspace=0.08,\
            left=0.075, right=0.96, bottom=0.12, top=0.9)

    axn = fig.add_subplot( gs[0,0])
    axSpi = fig.add_subplot( gs[1,0])
    axT = fig.add_subplot( gs[0,1])
    axU = fig.add_subplot( gs[1,1])

    axSpiB = fig.add_subplot(gs[0,2])
    axFrac = fig.add_subplot(gs[1,2])

    U0 = spis[0]['U111'].max()
    T0 = spis[0]['Tspi']
    t0 = spis[0]['t111'].min()
    T0dens = spis[0]['Tn']/t0 
    
    titletext = r'$\mathrm{{density\ at\ }} [T/t]_{{0}}={:0.2f}$\, \ \ \ '\
               .format(T0dens)
    titletext += r'$S_{{\pi}}\ \mathrm{{at}}\ \ [U/t]_{{0}}={:0.1f}\ , \  \ $'\
                 .format(U0) + \
                 r'$[T/t]_{{0}}={:0.2f}\ \ $'.format(T0) 

    if inhomog:
        titletext = titletext + r'$\mathrm{{Inhomogeneous}}$'
    
    fig.text(0.5, 0.98, titletext, ha='center', va='top', fontsize=13) 

    results = [] 
    for spi in spis:
        spiB = spi['SpiBulk']
        spi0 = spi['spi111'].max()

        # effective contributing fraction
        x = (spiB - 1.)/(spi0-1.)


        results.append( [spi['Number']/1e5, spiB, x*100.] )

        t0 = spi['t111'].min()
        #print "T (density) = ", spi['Tn']/t0
        Tspi = spi['Tspi']

        axn.plot(spi['r111'], spi['n111'])
        axSpi.plot(spi['r111'], spi['spi111'])
        axT.plot( spi['r111'], Tspi * t0 / spi['t111']  )
        axU.plot( spi['r111'], spi['U111'])
    results = np.array(results)
    axSpiB.plot( results[:,0], results[:,1],'.-')
    axFrac.plot( results[:,0], results[:,2],'.-')

    axn.set_ylabel('$n$', rotation=0, labelpad=12, fontsize=13)
    axT.set_ylabel('$T/t$', rotation=0, labelpad=12, fontsize=13)
    axU.set_ylabel('$U/t$', rotation=0, labelpad=12, fontsize=13)
    axSpi.set_ylabel(r'$\frac{S_{\pi}}{n}$', rotation=0, labelpad=12, \
                     fontsize=13)
    axSpiB.set_ylabel(r'$\bar{S_{\pi}}$', rotation=0, labelpad=12, \
                     fontsize=13)
    axFrac.set_ylabel('Effective fraction (\%)')
    axFrac.set_xlabel('$N/10^{5}$')
    
    axSpiB.set_ylim(0.5,2.0)
    axFrac.set_ylim(-20., 60.)

    for ax in [axn, axT, axSpiB]:
        ax.xaxis.set_ticklabels([])
    for ax in [axSpi, axU]:
        ax.set_xlabel('$r_{111}\ (\mu\mathrm{m})$')


    for ax in [axn, axSpi, axT, axU, axSpiB, axFrac]:
        ax.grid(alpha=0.5)

    if inhomog:
        inhomog_tag = 'inhomog'
    else:
        inhomog_tag = '' 
    fig.savefig('dataplots/VaryN_Spi/Tn{:0.2f}_U{:04.1f}_T{:0.2f}'.\
                 format(T0dens,U0,T0) + inhomog_tag +'.png', dpi=300)


import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser('spi_vs_n.py')
    parser.add_argument('SCATTLEN', action="store", type=float, \
        help='Scattering length') 
    parser.add_argument('TSPI', action="store", type=float, \
        help='The value of [T/t]_0 used for Spi')
    parser.add_argument('--inhomog', action="store_true", \
        help='Whether or not to use inhomogeneous U/t and T/t in Spi') 

    args = parser.parse_args()

    print args  


    #Spi_inhomog = False
    #aS      = 200. 
    #Ts      = 0.9 
    Spi_vs_N( aS=args.SCATTLEN, \
              Spi_inhomog=args.inhomog, \
              Tspi = args.TSPI) 
