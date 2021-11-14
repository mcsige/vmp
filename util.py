import sys
import os

def readcode(path='opcodes'):
    f = open(os.path.join(sys.path[0],'data',path),'r')
    opcodes = f.read().split(',')
    for i in range(len(opcodes)):
        opcodes[i] = int(opcodes[i])
    f.close()
    return opcodes
