###################################################################################################
##                              Tool for automated model generation                              ##
###################################################################################################

#############
## CONTENT ##
#############

* Overview on the files contained in this package
* Required packages
* Usage


#####################################################
## Overview on the files contained in this package ##
#####################################################

This package contains:
  * generate-model.py - the entry point of this package. 

  * mars-probe.lua : an example process description in LUA
  * mars-probe.data : an example process description as a python dictionary
  * mars-probe.prism : the model of the example process description
  
  * L4.lua : Lua library that collects process data
  * extract.lua : Wrapper for the process description script
  * createModel.py : the entry point for generating the model from the .data file
  
  * Properties/*.props : some example property files for the PRISM model checker
  * Results/* : Measurement results performed in PRISM using mars-probe.prism 
    and the example property files
  * Templates : a set of MAKO-templates used to generate the model
  
  
#######################
## Required packages ##
#######################

To use the entire tool chain you need the following packages:
  * Python: https://www.python.org/
  * Lua: https://www.lua.org/
  * MAKO: a python-based template language for generating long strings
    http://www.makotemplates.org/
  * PRISM or another analysis tool understanding the PRISM language
    http://www.prismmodelchecker.org/
Parts of the tool chain can also be used without having all packages installed. See section *Usage*
for details. Python is required anyway. 

###########
## Usage ##
###########

The entry point of the tool is generate-model.py. calling generate-model.py -h provides a list of 
available command line arguments. 
Having all required packages installed, generate-model.py <lua-file> generates a model from the 
process description provided in the Lua-file. Output is written to PRISM-model.prism, if not 
specified otherwise via the --model-output argument. 
Not having Lua installed, generate-model.py -f <data-file> generates the PRISM file from a python 
dictionary describing the process structure. 
Further arguments:
  --error-prob <p> specifies the error probability. This needs to be a value 
in [0,1].
  --detectable-prob <p> specifies the (conditional) probability of an error being detectable. This 
needs to be a value in [0,1].
