from numpy import *
from scipy.integrate import *
from scipy.interpolate import *

from globals import ifplot
if ifplot:
    import plots

def pds(infile='flux', binning=None, binlogscale=False):
    '''
    makes a power spectrum plot;
    input infile+'.dat' is an ascii, 2+column dat-file with an optional comment sign of #
    if binning is set, it should be the number of frequency bins; binlogscale makes frequency binning logarithmic
    '''
    lines = loadtxt(infile+".dat", comments="#", delimiter=" ", unpack=False)
    t=lines[:,0] ; l=lines[:,1]
    # remove linear trend!
    linfit = polyfit(t, l, 1)
    f=fft.rfft((l-linfit[0]*t-linfit[1])/l.std(), norm="ortho")
    freq=fft.rfftfreq(size(t),t[1]-t[0])
    
    pds=abs(f)**2
    if ifplot:
        plots.pdsplot(freq, pds, outfile=infile+'_pds')
    
    # additional ascii output:
    fpds=open(infile+'_pds.dat', 'w')
    for k in arange(size(freq)-1)+1:
        fpds.write(str(freq[k])+' '+str(pds[k])+'\n')
    fpds.close()

    if binning != None:
        if binlogscale:
            binfreq=(freq.max()/freq[freq>0.].min())**(arange(binning+1)/double(binning))*freq[freq>0.].min()
            binfreq[0]=0.
        else:
            binfreq=linspace(freq.min(), freq.max(), binning+1)
        binflux=zeros(binning) ; dbinflux=zeros(binning)
        binfreqc=(binfreq[1:]+binfreq[:-1])/2. # bin center
        binfreqs=(binfreq[1:]-binfreq[:-1])/2. # bin size
        for k in arange(binning):
            win=((freq<binfreq[k+1]) & (freq>=binfreq[k]))
            binflux[k]=pds[win].mean() ; dbinflux[k]=pds[win].std()/sqrt(double(win.sum()))

        fpds=open(infile+'_pdsbinned.dat', 'w')
        for k in arange(binning):
            fpds.write(str(binfreq[k])+' '+str(binfreq[k+1])+' '+str(binflux[k])+' '+str(dbinflux[k])+'\n')
        fpds.close()
        if ifplot:
            plots.binplot_short(binfreqc, binfreqs, binflux, dbinflux, outfile=infile+'_pdsbinned')

def dynspec(infile='flux', ntimes=10, nbins=10, binlogscale=False):
    '''
    makes a dynamic spectrum by making Fourier in each of the "ntimes" time bins. Fourier PDS is binned to "nbins" bins
    '''
    lines = loadtxt(infile+".dat", comments="#", delimiter=" ", unpack=False)
    t=lines[:,0] ; l=lines[:,1]
    nsize=size(t)
    tbin=linspace(t.min(), t.max(), ntimes+1)
    tcenter=(tbin[1:]+tbin[:-1])/2.
    freq1=1./(t.max())*double(ntimes)/2. ; freq2=freq1*double(nsize)/double(ntimes)/2.
    if(binlogscale):
        binfreq=logspace(log10(freq1), log10(freq2), num=nbins+1)
    else:
        binfreq=linspace(freq1, freq2, nbins+1)
    binfreqc=(binfreq[1:]+binfreq[:-1])/2.
    pds2=zeros([ntimes, nbins]) ;   dpds2=zeros([ntimes, nbins])
    t2=zeros([ntimes+1, nbins+1], dtype=double)
    nbin=zeros([ntimes, nbins], dtype=double)
    binfreq2=zeros([ntimes+1, nbins+1], dtype=double)
    fdyns=open(infile+'_dyns.dat', 'w')
    for kt in arange(ntimes):
        wt=(t<tbin[kt+1]) & (t>=tbin[kt])
        lt=l[wt]
        fsp=fft.rfft((lt-lt.mean())/lt.std(), norm="ortho")
        nt=size(lt)
        freq = fft.rfftfreq(nt, (t[wt].max()-t[wt].min())/double(nt))
        pds=abs(fsp*freq)**2
        t2[kt,:]=tbin[kt] ; t2[kt+1,:]=tbin[kt+1] 
        binfreq2[kt,:]=binfreq[:] ; binfreq2[kt+1,:]=binfreq[:] 
        for kb in arange(nbins):
            wb=((freq>binfreq[kb]) & (freq<binfreq[kb+1]))
            nbin[kt,kb] = size(pds[wb])
            #            print("size(f) = "+str(size(freq)))
            #            print("size(pds) = "+str(size(pds)))
            pds2[kt, kb]=pds[wb].mean() ; dpds2[kt, kb]=pds[wb].std()
            # ascii output:
            fdyns.write(str(tcenter[kt])+' '+str(binfreq[kb])+' '+str(binfreq[kb+1])+' '+str(pds2[kt,kb])+' '+str(dpds2[kt,kb])+" "+str(nbin[kt,kb])+"\n")
    fdyns.close()
    print(t2.max())
    plots.dynspec(t2,binfreq2, pds2, outfile=infile+'_dyns', nbin=nbin)

#############################################
def fhist(infile = "flux"):
    '''
    histogram of flux distribution (reads a two-column ascii file)
    '''
    lines = loadtxt(infile+".dat", comments="#", delimiter=" ", unpack=False)
    t=lines[:,0] ; l=lines[:,1]
    nsize=size(t)
    fn, binedges = histogram(l, bins='auto')
    binc = (binedges[1:]+binedges[:-1])/2.
    bins = (binedges[1:]-binedges[:-1])/2.
    dfn = sqrt(fn)

    medianl = median(l)
    significant = (fn > (dfn*3.)) # only high signal-to-noize points
    w = significant * (binc>(medianl*3.))
    p, cov = polyfit(log(binc[w]), log(fn[w]), 1, w = 1./dfn[w], cov=True)
    print("median flux = "+str(medianl))
    print("best-fit slope "+str(p[0])+"+/-"+str(sqrt(cov[0,0])))
                
    plots.binplot(binedges, fn, dfn, fname=infile+"_hist", fit = exp(p[0]*log(binedges)+p[1]))

