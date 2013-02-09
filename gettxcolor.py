import colordefs
import os
import json
import connector
from armoryengine import *
import urllib2
import heapq
from colortools import *

BDM_LoadBlockchainFile()

DEBUG = False

COLOR_UNKNOWN = -2
COLOR_UNCOLORED = None

def get_matching_inputs (pytx, index):
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
        print inputs, PSI, " | " , outputs, PSO, " (index = %d" % index

    # Get all inputs that flow into the given output
    children = []
    for i,inp in enumerate(inputs):
        if PSI[i] < PSO[index+1] and PSI[i+1] > PSO[index]: 
            children.append(i)
    return children

def hextobin(x): return hex_to_binary(x,endIn=LITTLEENDIAN, endOut=BIGENDIAN)
def bintohex(x): return binary_to_hex(x,endIn=LITTLEENDIAN, endOut=BIGENDIAN)

# Debugging method
def print_tree(t,visited,indent=0):
    print " "*(indent*3) + str(t["color"]) + " " + bintohex(t["txhash"]) + " " + str(t["index"])
    for c in [visited[x] for x in t["children"]]:
      print_tree(c,visited,indent+1)

def search_for_color (hex_txhash,index):
    issues = {}
    for cdef in color_definitions:
        for i in cdef[1]["issues"]:
            issues[i["txhash"]+str(i["outindex"])] = cdef[0]

    txhash = hextobin(hex_txhash)

    def key(txhash,index): return txhash + " " + str(index)

    visited = {key(txhash,index): {"parent":None,
                                   "txhash":txhash,
                                   "index":index,
                                   "color":COLOR_UNKNOWN,
                                   "children":[]}}

    heap = [(txhash, index)]
    root = visited[key(txhash,index)]

    def visit_node(vindex):
        full_eval = True
        node = visited[vindex]
        while node["parent"]:
            p = visited[node["parent"]]
            if p["color"] == COLOR_UNKNOWN: p["color"] = node["color"]
            elif p["color"] != node["color"]: p["color"] == COLOR_UNCOLORED
            node = p
        return node["color"]

    while len(heap) > 0:
        curtx, curind = heapq.heappop(heap)
        curnode = visited[key(curtx, curind)]
        mytx = TheBDM.getTxByHash(curtx)
        # Is coinbase, return uncolored
        if mytx.getTxIn(0).isCoinbase():
            return COLOR_UNCOLORED
        # Matches color issue, return color
        hexhash = bintohex(curtx)
        if hexhash+str(curind) in issues: 
            curnode["color"] = issues[hexhash+str(curind)]
            visit_node(key(curtx,curind))
            if root["color"] == COLOR_UNCOLORED: return None
        else:
        # Get children of node
            children = get_matching_inputs(PyTx().unserialize(mytx.serialize()),curind)
            for c in children:
                txp_outpoint = mytx.getTxIn(c).getOutPoint()
                newhash, newind = txp_outpoint.getTxHash(), txp_outpoint.getTxOutIndex()
                newnode = {"txhash":newhash,
                           "index":newind,
                           "color":COLOR_UNKNOWN,
                           "parent":key(curtx,curind),
                           "children":[]}
                if (key(newhash,newind)) not in visited:
                    heapq.heappush(heap,(newhash,newind))
                    visited[key(newhash,newind)] = newnode
                curnode["children"].append(newhash)
    if DEBUG: print_tree(visited[txhash],visited)
    return None if root["color"] in (COLOR_UNKNOWN, COLOR_UNCOLORED) else root["color"]
