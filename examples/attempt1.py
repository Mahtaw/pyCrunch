#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 15:23:36 2018

@author: mahtag2
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pyPCGA import PCGA
import math
import datetime as dt
import os
import pyCrunch
from glob import glob


files = glob('simul*.txt') #Delete the old files to start fresh
for file in files:
    os.remove(file)

# model domain and discretization
Lx = 5.; Ly = 5.; Lz = 1; nlay = 1; nrow = 10; ncol = 12
#ztop = 0.; zbot = -1

N = np.array([ncol, nrow, nlay])
m = np.prod(N) #multiply*
dx = np.array([0.5, 0.5, 1.])#Why do you have to put"." after each number?
xmin = np.array([0. + dx[0] / 2., 0. + dx[1] / 2., 0. + dx[2] / 2.])
xmax = np.array([Lx - dx[0] / 2., Ly - dx[1] / 2., Lz - dx[2] / 2.])

# covairance kernel and scale parameters
prior_std =0.0001
prior_cov_scale = np.array([0.0001, 0.0001, 0.0001])

def kernel(r): return (prior_std ** 2) * np.exp(-r)

# for plotting
x = np.linspace(0. + dx[0] / 2., Lx - dx[0] / 2., N[0])
y = np.linspace(0. + dx[1] / 2., Ly - dx[1] / 2., N[1])
XX, YY = np.meshgrid(x, y)
pts = np.hstack((XX.ravel()[:, np.newaxis], YY.ravel()[:, np.newaxis]))

inputDirectory = '/Users/mahtag2/syn_inverse_guess/'
inputFileName = '2DCr.in'

directory= '/Users/mahtag2/syn_inverse_test' #directory of the Crunch ouptuts
perm=pyCrunch.getPerm(directory)
#
#permeability_x=perm2array(perm[0])[:,3]
#permeability_y=perm2array(perm[0])[:,4]

s_true= pyCrunch.S2array(pyCrunch.getS(directory)[0])
#!s_true = sss.reshape(-1, 1)  # make it 2D array

 
brk= pyCrunch.getBreakthroughFiles(directory)

obs_true=[] #making an empty list of mean travel times
#we usually have multiple brk files so we need to bring them all in!
for file in brk:
    
    obs_true.append(pyCrunch.getMeanTravelTime(pyCrunch.brk2array(file)))
    
obs_true=np.array(obs_true)



def forward_model(s_true,par,ncores = None):
    if par == True:
        raise ValueError("This crunchflow forward model does not support parallelization.")
    inputDirectory = '/Users/mahtag2/syn_inverse_guess/'
    inputFileName = '2DCr.in'
    directory= '/Users/mahtag2/syn_inverse_test' #directory of the Crunch ouptuts
    # Update make a new permeability files from s before running crunch
    pyCrunch.runCrunch(inputDirectory,inputFileName)
    bk= pyCrunch.getBreakthroughFiles(directory)

    obs_s=[] #making an empty list of mean travel times
# #we usually have mulptiple brk files so we need to bring them all in!
    for file in bk:
        obs_s.append(pyCrunch.getMeanTravelTime(pyCrunch.brk2array(file)))
    simul_obs=np.array(obs_s)
    
    
    Old_s=pyCrunch.getS(directory)
    assert len(Old_s) == 1
    k = pyCrunch.S2array(Old_s[0])
    np.savetxt(os.path.join(directory,'PermField.x'),k)
    return simul_obs


##s_init = np.copy(s_true) # you can try with s_true!
##s_init = s_init.reshape((s_init.shape[0],1))
    
s_true = s_true.reshape((s_true.shape[0],1))
s_init = np.ones((m, 1))


params = {'R': (0.5) ** 10, 'n_pc': 5,
          'maxiter': 10, 'restol': 0.01,
          'matvec': 'FFT', 'xmin': xmin, 'xmax': xmax, 'N': N,
          'prior_std': prior_std, 'prior_cov_scale': prior_cov_scale,
          'kernel': kernel, 'post_cov': "diag",
          'precond': True, 'LM': True,
          'parallel': False, 'linesearch': True,
          'forward_model_verbose': False, 'verbose': False,
          'iter_save': True}

## initialize
pcga = PCGA(forward_model, s_init, pts, params, s_true, obs_true)
#out = pcga.CreateSyntheticData (s_true, noise = False)



## run inversion
#input("Press enter to continue")
s_hat, simul_obs, post_diagv, iter_best = pcga.Run() 
#
#s_hat3d = s_hat.reshape(nlay, nrow, ncol)
#s_hat2d = s_hat3d[0,:,:]
#s_true3d = s_true.reshape(nlay, nrow, ncol)
#s_true2d = s_true3d[0,:,:]

#post_diagv[post_diagv < 0.] = 0.  # just in case we have stuff that is negavtive
## it is a way for selecting stuff in the array that are smaller than zero
#post_std = np.sqrt(post_diagv)
#post_std3d = post_std.reshape(nlay, nrow, ncol)
#post_std2d = post_std3d[0,:,:]

