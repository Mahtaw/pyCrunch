#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 11 15:36:23 2018

@author: mahtag2
"""
'''
This script is to calculate Mean travel time for the tacer & plot permeability maps
'''
import numpy as np
from glob import glob #glob will help you search!
import os
from pyCrunch.utilityFuncs import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math
 

directory= '/Users/mahtag2/Desktop/syn_inverse_test' #directory of the Crunch ouptuts
saveDir = 
 
brk= getBreakthroughFiles(directory)
print(brk)

m=[] #making an empty list of mean travel times
# #we usually have mulptiple brk files so we need to bring them all in!
for file in brk:
    m.append(getMeanTravelTime(brk2array(file)))
    
meantt=np.array(m)



np.savetxt(os.path.join(saveDir,'test.txt'), meantt, delimiter=',')



s=getS(directory)
for file in s:
    k= S2array(file)
print()




###data = dict(zip([sorterFunc(file) for file in brk], m))

 ## Permeability plotter

#perm=getPerm(directory)
#
#permeability_x=perm2array(perm[0])[:,3]
#permeability_y=perm2array(perm[0])[:,4]
#
#
#x = np.linspace(0 , 5, 10)
#y = np.linspace(0 ,5, 10)
#XX, YY = np.meshgrid(x, y)
#
#plt.pcolormesh(XX,YY,permeability_x.reshape(10,10))
#plt.colorbar()

