#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 20:46:14 2018

@author: mahtag2
"""
##Run Crunchflow
import pyCrunch.utilityFuncs as uf
import os;



#Where input file is
inputDirectory = '/Users/mahtag2/Desktop/CrunchTope-InstallMac/Inversion_test/'
inputFileName = '2DCr.in'

#templatePath='/Users/mahtag2/Desktop/CrunchTope-InstallMac/Inversion_att1/'
templateFile = '/Users/mahtag2/Desktop/CrunchTope-InstallMac/Inversion_att1/2DCra.in'
##
dataDict = {'pressure':[1000,0],'permeability_x':[1500,300]}
#
#dataDict ={'pressure':[1000,0]}
#This is to over write the input files 

uf.generateInputFile(os.path.join(inputDirectory,inputFileName),templateFile,dataDict)

#uf.dbsPopulater (inputDirectory,templatePath)##copying the .dbs files for Crunch

#uf.runCrunch(inputDirectory,inputFileName)##run Crunch

