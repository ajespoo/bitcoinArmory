import colordefs
import os
import json
import connector
from armoryengine import *
from heapq import *
import urllib2
from colortools import *

BDM_LoadBlockchainFile()

def get_parent_inputs (pytx, index):
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

    compute_colors(inputs,outputs)
    parents = []
    for i,inp in enumerate(inputs):
      if inp[1] == outputs[index][1]: parents.append(i)
    return parents

def search_for_color (txhash,index):
    issues = {}
    for cdef in color_definitions:
        for i in cdef[1]["issues"]:
            issues[i["txhash"]+str(i["outindex"])] = cdef[0]
    heap = []

    mytx = TheBDM.getTxByHash(hex_to_binary(txhash))
    if mytx.getTxIn(0).isCoinbase(): return -1

    heappush(heap,[0,mytx,index])

    while len(heap) > 0:
        top = heappop(heap)
        # Matches color issue, return color
        if top[1].getThisHash()+str(top[2]) in issues: 
            return issues[top[1].getThisHash()+str(top[2])]
        # Get parent tx
        txp_outpoint = top[1].getTxIn(top[2]).getOutPoint()
        txparent = TheBDM.getTxByHash(txp_outpoint.getTxHash())
        # Is parent coinbase, return -1
        if txparent.getTxIn(0).isCoinbase():
            return -1
        print binary_to_hex(txp_outpoint.getTxHash()),txp_outpoint.getTxOutIndex()
        for p in get_parent_inputs(PyTx().unserialize(txparent.serialize()),txp_outpoint.getTxOutIndex()):
            # Modify the top[0] + 1 to make a different search algorithm
            heappush(heap,[top[0]+1,txparent,p])

print search_for_color('6e48773b62a6f4a784d8fa75911859cb8de5eb3f9a6eb89587f7320bd16c58b1',0)
print search_for_color('8f6c8751f39357cd42af97a67301127d497597ae699ad0670b4f649bd9e39abf',0)
