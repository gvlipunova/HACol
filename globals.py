from numpy import *
# All the global parameters used in the code
# let us assume GM=1, c=1, kappa=1; this implies Ledd=4.*pi

nx=1000 # the actual number of points in use
nx0=nx*20 # first we make a finer mesh for interpolation

b12=10.
m1=1.4
mdot=100./4./pi # mass accretion rate
rstar=6. # GM/c**2 units
# vout=-0.5/sqrt(re) # initial poloidal velocity at the outer boundary 
eta=0.5 # self-illumination efficiency 
mfloor=1e-25  # crash floor for mass per unit length
rhofloor=1e-25 # crash floor for density
ufloor=1e-25 # crash floor for energy density
afac=0.5 # part of the longitudes subtended by the flow
re = 123. * ((b12*rstar**3)**2/mdot)**(2./7.)*m1**(2./7.) # magnetospheric radius
dre=minimum(mdot, re*0.5) # radial extent of the flow at re
print("magnetospheric radius re = "+str(re))
print("Delta re = "+str(dre))

# conversion to CGS units:
tscale=4.92594e-06*m1 # GMsun/c**3
rscale=1.47676e5*m1 # GMsun/c**2
rhoscale=1.93474e-05/m1 # c**2 / GMsun kappa, for kappa=0.35 (Solar metallicity, complete ionization)
uscale=1.73886e16/m1 # c**4/GMsun kappa
mdotscale=1.26492e16*m1 # G Msun / c kappa
lscale=1.13685e37*m1 # G Msun c / kappa luminosity scale 
#

tmax=1000./tscale # maximal time in tscales
dtout=1000. # output time step in tscales

omega=0.9*re**(-1.5) # in Keplerian units on the outer rim
umag=b12**2*3.2e6 # magnetic energy density at the surface, for a 1.4Msun accretor
pmagout=umag*(rstar/re)**6 # magnetic field pressure at the outer rim of the disc
vout=-0.05*pmagout*4.*pi*re*dre*afac/mdot # initial poloidal velocity at the outer boundary ; set to scale with magnetic pressure. 

xirad=0.25 # radiation loss scaling

# plotting options:
ifplot = True
plotalias = 10 # plot every Nth output step 

# output options:
ifhdf = True # if we are writing to HDF5 instead of ascii (flux is always outputted as ascii)
