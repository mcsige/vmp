import sys
import os
from util import readcode

class Compiler:
    def __init__(self):
        self.opcodes = []
        try:
            self.opcodes = readcode('run_opcodes.txt')
        except:
            print('no file data/run_opcodes.txt')
        self.rip = 0
        self.rip0 = 0
        self.err_code = 'wrong analyse at %s'
        self.cs = 0x1000
        self.ds = 0xf000
        self.comcode = []

    def dword(self,p):
        s = 0
        for i in range(4):
            s+=self.opcodes[self.rip+p+i]*256**i
        return hex(s)

    def alu(self,test = False,name = 'add'):
        sign = self.opcodes[self.rip+1]
        self.rip0 = self.rip
        s = ''
        ss = ' '
        off = 0
        if not test:
            off = self.opcodes[self.rip+2]
            ss += 'reg%d,'%off
            self.rip+=1
            if name=='div':
                self.rip+=1
        if sign==0:
            s = '{}{}reg{},reg{}'.format(name,ss,self.opcodes[self.rip+2],self.opcodes[self.rip+3])
            self.rip+=4
        elif sign==1:
            s = '{}{}reg{},{}'.format(name,ss,self.opcodes[self.rip+2],self.dword(3))
            self.rip+=7
        elif sign==2:
            s = '{}{}{},reg{}'.format(name,ss,self.dword(2),self.opcodes[self.rip+6])
            self.rip+=7
        elif sign==4:
            s = '{}{}{},{}'.format(name,ss,self.dword(2),hex(self.dword(6)))
            self.rip+=10
        else:
            self.wrong()
        return(s)

    def log(self,out = 'com_log.txt'):
        f = open(os.path.join(sys.path[0],'data',out),'w')
        f.writelines(i+'\n' for i in self.comcode)
        f.close()

    def wrong(self):
        print(self.err_code %hex(self.cs+self.rip0))
        exit(0)

    def run(self,time = -1):
        t = 0
        while self.rip<len(self.opcodes) and (time==-1 or t<time):
            t+=1
            self.rip0 = self.rip
            s = ''
            if self.opcodes[self.rip]==0:
                s = 'nop'
                self.rip+=1
            elif self.opcodes[self.rip]==1:
                s = 'ret'
                self.rip+=1
            elif self.opcodes[self.rip]==2:
                s = self.alu(False,'add')
            elif self.opcodes[self.rip]==3:
                s = self.alu(False,'sub')
            elif self.opcodes[self.rip]==4:
                s = self.alu(False,'mul')
            elif self.opcodes[self.rip]==5:
                s = self.alu(False,'div')
            elif self.opcodes[self.rip]==6:
                s = self.alu(False,'xor')
            elif self.opcodes[self.rip]==7:
                s = 'neg reg{},reg{}'.format(self.opcodes[self.rip+1],self.opcodes[self.rip+2])
                self.rip+=3
            elif self.opcodes[self.rip]==8:
                s = 'not reg{},reg{}'.format(self.opcodes[self.rip+1],self.opcodes[self.rip+2])
                self.rip+=3
            elif self.opcodes[self.rip]==9:
                s = self.alu(False,'and')
            elif self.opcodes[self.rip]==0xa:
                s = self.alu(False,'or')
            elif self.opcodes[self.rip]==0xb:
                s = 'isz reg{},reg{}'.format(self.opcodes[self.rip+1],self.opcodes[self.rip+2])
                self.rip+=3
            elif self.opcodes[self.rip]==0xc:
                s = self.alu(False,'shl')
            elif self.opcodes[self.rip]==0xd:
                s = self.alu(False,'shr')
            elif self.opcodes[self.rip]==0xe:
                s = 'jmp {}'.format(self.dword(1))
                self.rip+=5
            elif self.opcodes[self.rip]==0xf:
                s = 'call {}'.format(self.dword(1))
                self.rip+=5
            elif self.opcodes[self.rip]==0x10:
                s = 'jz {}'.format(self.dword(1))
                self.rip+=5
            elif self.opcodes[self.rip]==0x11:
                s = 'jl {}'.format(self.dword(1))
                self.rip+=5
            elif self.opcodes[self.rip]==0x12:
                s = 'jle {}'.format(self.dword(1))
                self.rip+=5
            elif self.opcodes[self.rip]==0x13:
                s = 'jg {}'.format(self.dword(1))
                self.rip+=5
            elif self.opcodes[self.rip]==0x14:
                s = 'jge {}'.format(self.dword(1))
                self.rip+=5
            elif self.opcodes[self.rip]==0x15:
                s = 'jnz {}'.format(self.dword(1))
                self.rip+=5
            elif self.opcodes[self.rip]==0x16:
                s = self.alu(True,'test')
            elif self.opcodes[self.rip]==0x17:
                s = self.alu(True,'cmp')
            elif self.opcodes[self.rip]==0x18:
                sign =self.opcodes[self.rip+1]
                if sign==1:
                    s = 'mov reg{},{}'.format(self.opcodes[self.rip+2],self.dword(3))
                    self.rip+=7
                else:
                    s = 'mov reg{},reg{}'.format(self.opcodes[self.rip+2],self.opcodes[self.rip+3])
                    self.rip+=4
            elif self.opcodes[self.rip]==0x19:
                s = 'inc reg{}'.format(self.opcodes[self.rip+1])
                self.rip+=2
            elif self.opcodes[self.rip]==0x1a:
                s = 'dec reg{}'.format(self.opcodes[self.rip+1])
                self.rip+=2
            elif self.opcodes[self.rip]==0x1b:
                s = 'mov reg{},[reg{}]'.format(self.opcodes[self.rip+1],self.opcodes[self.rip+2])
                self.rip+=3
            elif self.opcodes[self.rip]==0x1c:
                s = 'mov [reg{}],reg{}'.format(self.opcodes[self.rip+1],self.opcodes[self.rip+2])
                self.rip+=3
            elif self.opcodes[self.rip]==0x1d:
                s = 'nop'
                self.rip+=1
            elif self.opcodes[self.rip]==0x1e:
                sign = self.opcodes[self.rip+1]
                if sign==1:
                    s = 'push {}'.format(self.dword(2))
                    self.rip+=6
                else:
                    s = 'push reg{}'.format(self.opcodes[self.rip+2])
                    self.rip+=3
            elif self.opcodes[self.rip]==0x1f:
                s = 'pop reg{}'.format(self.opcodes[self.rip+1])
                self.rip+=2
            elif self.opcodes[self.rip]==0x20:
                s = 'syscall {}'.format(hex(self.opcodes[self.rip+1]))
                self.rip+=2
            else:
                self.wrong()
            hex_code = ''
            for i in range(self.rip0,self.rip):
                hex_code+=str(hex(self.opcodes[i]))+' '
            self.comcode.append('{name: <8}{ase: <30}{hex}'.format(name=hex(self.cs+self.rip0),ase=s,hex=hex_code))

""" 
mov reg[0],0x103a
mov reg[1],0x1edb
mov reg[3],reg[0]
mov reg[5],0x0174cf42
loc_1019:
mov reg[4],[reg[3]]
xor reg[4],reg[4],reg[5]
mov [reg[3]],reg[4]
add reg[3],reg[3],0x4
cmp reg[1],reg[3]
jle 0x1019
jmp 0x103a
loc_103a:
"""
