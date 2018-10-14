#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edited on Sun Aug 16 12:33:45 2018

@author: mahtag2
"""
from glob import glob
import os
import numpy as np
import subprocess
import shutil
import fileinput
import matplotlib.pyplot as plt 
import math

#importing brk files,it is important to have them sorted
def getBreakthroughFiles(directory):
    brk = glob(os.path.join(directory,'breakthrough*.out')) #makes a list of all the breakthrough output files
    #glob on its own doesnt sort the files, it is important to sort them because each belongs to specific grid block
    #here we are defining a function! (lambda works like def function!)
    sorterFunc = lambda brkname: int(os.path.split(brkname)[-1][12:-4]) #split will give us the name of the brk file ans split the whole string!
    #this function cuts "breakthrough" and ".out" from all the names in brk list
    #int makes everything into integer! 
    brk.sort(key = sorterFunc) #here we are sorting the brk list according to sorterfunction values
    return brk

#converting the files to array
def brk2array(fileName):
    return np.loadtxt(fileName,skiprows=2)# works like importer function in MATLab

def getMeanTravelTimes(directory):
    '''Get and sort the list of the breakthrough files in the working directory'''
    brk = getBreakthroughFiles(directory)
    '''Generate arrays from the breakthrough files'''
    arrs = []
    for file in brk:
        arrs.append(brk2array(file))
    '''Generate mean travel times from the arrays'''
    obs = []
    for arr in arrs:
        obs.append(getMeanTravelTime(arr))
    return np.array(obs)
    
'''Given a numpy array generated from the brk2array function, this function will return the mean travel time.'''
def getMeanTravelTime(array):
    #Since the values in brk files are seperated with spaces we need to count the characters in between the columns! It is called 
    #fixed width file! The first two rows of the files are strings
    time=array[:,0]
    tracer_conc=array[:,-1]
    
    #mean travel time calculator
    return np.trapz(time*tracer_conc,x=time)/np.trapz(tracer_conc,x=time)#append will save m everytime it goes through the loop
    #integral of t*c/integral of c

#importing permeability files
def getPerm(directory):           
    perm = glob(os.path.join(directory,'permeability*.tec'))  
    sorterFunc = lambda permname: int(os.path.split(permname)[-1][12:-4])  
    perm.sort(key = sorterFunc)
    return perm

def getS(directory):   
    files=glob(os.path.join(directory, 'PermField.x'))
    assert len(files) == 1
    s = np.genfromtxt(files[0])
    s = s.reshape((s.shape[0],1))
    return s

    

#making the permeability files into an array
def perm2array(fileName):
    return np.genfromtxt(fileName,delimiter = [20,17,16,17, 17],skip_header=3)           
    
    #Creating new input files based on a template
def generateInputFile(outputPath,templatePath, d):#output path: directory of the new file, Templatepth: directory of the template
    #d is a dictionary it can only have two variables,
    if os.path.exists(outputPath):
        if input("Output file already exists, do you want to overwrite? (y/n)").strip().lower() != 'y': #to make sure that you are on the right track
            print("Cancelling")
            return
    for key,value in d.items():#key is the name of the parameter etc permeability , pressure ...
        d[key] = (value, 0) #each key has a value and an index, indexing is important because it will overwrite every value associate with pressure but we doent want  than!
    shutil.copyfile(templatePath,outputPath)#make a copy of the template
    with fileinput.input(outputPath, inplace=True) as f: #with makes sure that if an error doesnt happen it exits the loop 
        for line in f: #f is all the contents of the newinput file , here we want to search all the lines
            newline = [] #empty array for the new line
            for i in line.split(' '): #problem is that all the files for Crunch are seperated with space, we are spliting the string into its characters
                        if i != '':# if the character is not space
                            newline.append(i)#then add it to the newline array
            for key,(value,index) in d.items():
                if key == newline[0]: #so if the key matches the line 
                    newValue = value[index]#it will asign a value with index to it
                    newline[1] = str(newValue)# in newline the first thing right after the key would get that string which is number
                    d[key] = (value,index+1)# this will add to the index and go to the next one.
                    break
            newline = str.join(' ',newline) #this will add back the white spaces to the line so that crunch could read it.      
            print(newline)#this will actually overwrite the values in the input file

def generatePermeabilityFile(s: np.ndarray, outputPath: str, fileName:str) -> None:
    path = os.path.join(outputPath, fileName)
    s = s.squeeze()
    assert len(s.shape) == 1
    np.savetxt(path,s)
        
  #Copying all the .dbs files needed to a new folder so that Crunch could run in it!          
def dbsPopulater (outputPath,templatePath):  
    folders_src=glob(templatePath+'*.dbs')
    fileNames = [os.path.split(i)[-1] for i in folders_src]
    for i in fileNames:
        print('Attempting to copy: ',os.path.join(outputPath,i))
        if not os.path.exists(os.path.join(outputPath,i)):
            shutil.copy(os.path.join(templatePath,i),outputPath)   
        else:
            print("it already exists!")
            
def fromPermtoPCGATrue(inPath,outPath):
    inPerm = np.genfromtxt(inPath) #the log10 permeability from a crunchflowrun
    outPerm = np.log(10**inPerm) #PCGA wants it's true permeability value as the natural log.
    np.savetxt(outPath, outPerm)


class CrunchRun:
    def __init__(self, initialInputDirectory, inputFileName, workingDirectory, libraryPath ):
        if not (initialInputDirectory == workingDirectory): #The working directory needs to be initialized
            if os.path.exists(workingDirectory):
                if input("The working directory: {} already exists. Do you want to overwrite? (y/n)".format(workingDirectory)).strip().lower() == 'y':
                    shutil.rmtree(workingDirectory)
                else:
                    raise RuntimeError("Execution Cancelled")
            shutil.copytree(initialInputDirectory, workingDirectory)
        self.inputFileName = inputFileName
        self.libraryPath = libraryPath
        self.workingDirectory = workingDirectory

    def run(self, verbose = False):
        if self.libraryPath is None:
            raise ValueError("libraryPath has not been specified.")
        if self.workingDirectory is None:
            raise ValueError("The working directory has not been initialized.")
        crunchPath = os.path.join(self.libraryPath,'CrunchTope-Mac') #Actual directory of Crunch executable
        #here were combining all the directories 
        cmd = 'export DYLD_LIBRARY_PATH=' + self.libraryPath + '&&' + crunchPath + ' ' + os.path.join(self.workingDirectory, self.inputFileName)
        #'export DYLD_LIBRARY_PATH=' works as source .bashrc in terminal. It is needed so that crunch can find the other libraries it needs.
        # && combines the two commmands on a single line. Add DYLD libraries to the environment and then running crunch with the name of the input file
        proc = subprocess.Popen(cmd, shell=True, stdout = subprocess.PIPE, stderr= subprocess.PIPE, cwd = self.workingDirectory)# subprocess execute the above command.
        # stdout gets the output from the run, stderr gets the possible errors.
        if verbose:
            for l in proc.stdout:
                print(l.decode()[:-1])
        msg = proc.communicate() #communicate is when we need to see the outputs! This blocks until crunchflow completes
        #I took out the timeout=10 because Crunch would take much longer 
        if msg[1] != b'':
            raise RuntimeError("Crunchflow returned the following error: ", msg[1].decode())
            #importing brk files,it is important to have them sorted


       