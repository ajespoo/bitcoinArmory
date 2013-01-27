import colordefs
import os
import json
import connector
from armoryengine import *
import urllib2
from colortools import *

BDM_LoadBlockchainFile()

DEBUG = False

def get_parent_inputs (pytx, index,indent=0):
    inputs = []
    for i,inp in enumerate(pytx.inputs):
        txhash = inp.outpoint.txHash
        outindex = inp.outpoint.txOutIndex
        prevtx = TheBDM.getTxByHash(txhash)
        if not prevtx:
            raise Exception("Could not find referenced tx")
        if outindex != 4294967295: # Coinbase
          value = prevtx.getTxOut(outindex).getValue()
          inputs.append([value, i])
    outputs = []
    for outpt in pytx.outputs:
        outputs.append([outpt.value, 0])
    # A list of preceding sums by input and output
    PSI = reduce(lambda x,y: x + [x[-1]+y[0]], [[0]]+inputs)
    PSO = reduce(lambda x,y: x + [x[-1]+y[0]], [[0]]+outputs)
    
    if DEBUG:
        print "   " * indent, inputs, PSI, " | " , outputs, PSO, " (index = %d" % index

    # Get all inputs that flow into the given output
    parents = []
    for i,inp in enumerate(inputs):
        if PSI[i] < PSO[index+1] and PSI[i+1] > PSO[index]: 
            parents.append(i)
    return parents

def hextobin(x): return hex_to_binary(x,endIn=LITTLEENDIAN, endOut=BIGENDIAN)
def bintohex(x): return binary_to_hex(x,endIn=LITTLEENDIAN, endOut=BIGENDIAN)

def search_for_color_binhash (txhash,index,issues,indent=0):


    if DEBUG: 
        print "   " * indent + bintohex(txhash), "Index: " + str(index)

    mytx = TheBDM.getTxByHash(txhash)
    # Is coinbase, return uncolored
    if mytx.getTxIn(0).isCoinbase(): return None

    # Matches color issue, return color
    hexhash = bintohex(txhash)
    if hexhash+str(index) in issues: 
        return issues[hexhash+str(index)]
    
    # Get parent inputs
    parents = get_parent_inputs(PyTx().unserialize(mytx.serialize()),index,indent)

    pc = []
    for p in parents:
      # Get parent tx
      txp_outpoint = mytx.getTxIn(p).getOutPoint()


      # Recursive search is required since we need to make sure that ALL parent inputs are of the same color
      # for the output to be colored (any mixing leads to uncolored coins)
      pc.append(search_for_color_binhash(txp_outpoint.getTxHash(),txp_outpoint.getTxOutIndex(),issues,indent+1))
      if pc[-1] == None: return None
      if len(pc) > 1 and pc[-1] != pc[-2]: return None
    if len(pc) == 0: return None
    return pc[0]

def search_for_color(txhash, inp):
    issues = {}
    for cdef in color_definitions:
        for i in cdef[1]["issues"]:
            issues[i["txhash"]+str(i["outindex"])] = cdef[0]
    return search_for_color_binhash(hextobin(txhash),inp,issues)
