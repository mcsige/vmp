import sys
import os
import queue
from util import readcode
from disassembler import Compiler

class Debugger:
    def __init__(self):    
        self.opcodes = readcode()
        self.data = {}
        self.rip = 0
        self.rip0 = 0
        self.ripj = -1
        self.err_code = 'wrong analyse at %s'
        self.cs = 0x1000
        self.ds = 0xf000
        self.flag = 0
        self.stack = [0xed5]
        self.reg = [0]*32
        self.magic = 0x10000
        self.buffer = queue.Queue()
        self.runcode = []
        self.exe_cmd = ['regs','stack','quit','run','continue','opcode',
        'data','next','for','breakpoint','delete','klear','help']
        self.next_bp = True
        self.for_time = 0
        self.for_cmd_list = []
        self.for_p = 0
        self.inuse_reg = []
        self.bp = []

    def syscall(self,order):
        if order==0:
            print(chr(self.reg[0]),end='')
        elif order==4:
            if self.buffer.empty():
                # x = 'packers_and_vms_and_xors_oh_my'
                x = input()
                for i in x:
                    self.buffer.put(ord(i))
                self.buffer.put(ord('\n'))
            self.reg[0] = self.buffer.get()

        elif order==0x11:
            t = self.magic
            self.magic+=self.reg[0]
            self.reg[0] = t

    def dword(self,p):
        s = 0
        for i in range(4):
            s+=self.opcodes[self.rip+p+i]*256**i
        return s

    def alu(self,test = False,name = 'add'):
        sign = self.opcodes[self.rip+1]
        self.rip0 = self.rip
        s = ''
        ss = ' '
        op = '+'
        if name=='add':
            op = '+'
        elif name=='sub' or name=='cmp':
            op = '-'
        elif name=='mul':
            op = '*'
        elif name=='div':
            op = '//'
        elif name=='xor':
            op = '^'
        elif name=='and' or name=='test':
            op = '&'
        elif name=='or':
            op = '|'
        elif name=='shl':
            op = '<<'
        elif name=='shr':
            op = '>>'
        a = 0
        b = 0
        off = 0
        off_mod = 0
        if not test:
            off = self.opcodes[self.rip+2]
            ss += 'reg%d,'%off
            self.rip+=1
            if name=='div':
                off_mod = self.opcodes[self.rip+2]
                self.rip+=1
        if sign==0:
            a = self.reg[self.opcodes[self.rip+2]]
            b = self.reg[self.opcodes[self.rip+3]]
            self.inuse_reg = [self.opcodes[self.rip+2],self.opcodes[self.rip+3]]
            s = '{}{}reg{},reg{}'.format(name,ss,self.opcodes[self.rip+2],self.opcodes[self.rip+3])
            self.rip+=4
        elif sign==1:
            a = self.reg[self.opcodes[self.rip+2]]
            b = self.dword(3)
            self.inuse_reg = [self.opcodes[self.rip+2]]
            s = '{}{}reg{},{}'.format(name,ss,self.opcodes[self.rip+2],hex(b))
            self.rip+=7
        elif sign==2:
            a = self.dword(2)
            b = self.reg[self.opcodes[self.rip+6]]
            self.inuse_reg = [self.opcodes[self.rip+6]]
            s = '{}{}{},reg{}'.format(name,ss,hex(a),self.opcodes[self.rip+6])
            self.rip+=7
        elif sign==4:
            a = self.dword(2)
            b = self.dword(6)
            s = '{}{}{},{}'.format(name,ss,hex(a),hex(b))
            self.rip+=10
        else:
            self.wrong()
        if test:
            self.flag = eval('{}{}{}'.format(a,op,b))
        else:
            self.reg[off] = eval('{}{}{}'.format(a,op,b))
            self.inuse_reg.append(off)
            if name=='div':
                self.reg[off_mod] = a%b
                self.inuse_reg.append(off_mod)
        return(s)

    def log(self,out = 'run_log.txt'):
        f = open(os.path.join(sys.path[0],'data',out),'w')
        f.writelines(i+'\n' for i in self.runcode)
        f.close()

    def log_run_code(self,out = 'run_opcodes.txt'):
        f = open(os.path.join(sys.path[0],'data',out),'w')
        f.write(str(self.opcodes)[1:-1])
        f.close()

    def wrong(self):
        raise ValueError(self.err_code %hex(self.cs+self.rip0))

    def run(self,bp = []):
        self.bp = [i-self.cs for i in bp]
        while self.opcodes[self.rip]!=0x1d:
            self.rip0 = self.rip
            self.ripj = -1
            s = ''
            if self.opcodes[self.rip]==0:
                s = 'nop'
                self.rip+=1
            elif self.opcodes[self.rip]==1:
                s = 'ret'
                self.ripj = self.rip+1
                self.rip = self.stack.pop()
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
                self.reg[self.opcodes[self.rip+1]] = -self.reg[self.opcodes[self.rip+2]]
                self.inuse_reg = [self.opcodes[self.rip+1],self.opcodes[self.rip+2]]
                self.rip+=3
            elif self.opcodes[self.rip]==8:
                s = 'not reg{},reg{}'.format(self.opcodes[self.rip+1],self.opcodes[self.rip+2])
                self.reg[self.opcodes[self.rip+1]] = ~self.reg[self.opcodes[self.rip+2]]
                self.inuse_reg = [self.opcodes[self.rip+1],self.opcodes[self.rip+2]]
                self.rip+=3
            elif self.opcodes[self.rip]==9:
                s = self.alu(False,'and')
            elif self.opcodes[self.rip]==0xa:
                s = self.alu(False,'or')
            elif self.opcodes[self.rip]==0xb:
                s = 'isz reg{},reg{}'.format(self.opcodes[self.rip+1],self.opcodes[self.rip+2])
                self.reg[self.opcodes[self.rip+1]] = self.reg[self.opcodes[self.rip+2]]==0
                self.inuse_reg = [self.opcodes[self.rip+1],self.opcodes[self.rip+2]]
                self.rip+=3
            elif self.opcodes[self.rip]==0xc:
                s = self.alu(False,'shl')
            elif self.opcodes[self.rip]==0xd:
                s = self.alu(False,'shr')
            elif self.opcodes[self.rip]==0xe:
                s = 'jmp {}'.format(hex(self.dword(1)))
                self.ripj = self.rip+5
                self.rip = self.dword(1)-self.cs
            elif self.opcodes[self.rip]==0xf:
                s = 'call {}'.format(hex(self.dword(1)))
                self.ripj = self.rip+5
                self.stack.append(self.rip+5)
                self.rip = self.dword(1)-self.cs
            elif self.opcodes[self.rip]==0x10:
                s = 'jz {}'.format(hex(self.dword(1)))
                self.ripj = self.rip+5
                if self.flag==0:
                    self.rip = self.dword(1)-self.cs
                else:
                    self.rip+=5
            elif self.opcodes[self.rip]==0x11:
                s = 'jl {}'.format(hex(self.dword(1)))
                self.ripj = self.rip+5
                if self.flag<0:
                    self.rip = self.dword(1)-self.cs
                else:
                    self.rip+=5
            elif self.opcodes[self.rip]==0x12:
                s = 'jle {}'.format(hex(self.dword(1)))
                self.ripj = self.rip+5
                if self.flag<=0:
                    self.rip = self.dword(1)-self.cs
                else:
                    self.rip+=5
            elif self.opcodes[self.rip]==0x13:
                s = 'jg {}'.format(hex(self.dword(1)))
                self.ripj = self.rip+5
                if self.flag>0:
                    self.rip = self.dword(1)-self.cs
                else:
                    self.rip+=5
            elif self.opcodes[self.rip]==0x14:
                s = 'jge {}'.format(hex(self.dword(1)))
                self.ripj = self.rip+5
                if self.flag>=0:
                    self.rip = self.dword(1)-self.cs
                else:
                    self.rip+=5
            elif self.opcodes[self.rip]==0x15:
                s = 'jnz {}'.format(hex(self.dword(1)))
                self.ripj = self.rip+5
                if self.flag!=0:
                    self.rip = self.dword(1)-self.cs
                else:
                    self.rip+=5
            elif self.opcodes[self.rip]==0x16:
                s = self.alu(True,'test')
            elif self.opcodes[self.rip]==0x17:
                s = self.alu(True,'cmp')
            elif self.opcodes[self.rip]==0x18:
                sign = self.opcodes[self.rip+1]
                if sign==1:
                    s = 'mov reg{},{}'.format(self.opcodes[self.rip+2],hex(self.dword(3)))
                    self.reg[self.opcodes[self.rip+2]] = self.dword(3)
                    self.inuse_reg = [self.opcodes[self.rip+2]]
                    self.rip+=7
                else:
                    s = 'mov reg{},reg{}'.format(self.opcodes[self.rip+2],self.opcodes[self.rip+3])
                    self.reg[self.opcodes[self.rip+2]] = self.reg[self.opcodes[self.rip+3]]
                    self.inuse_reg = [self.opcodes[self.rip+2],self.opcodes[self.rip+3]]
                    self.rip+=4
            elif self.opcodes[self.rip]==0x19:
                s = 'inc reg{}'.format(self.opcodes[self.rip+1])
                self.reg[self.opcodes[self.rip+1]]+=1
                self.inuse_reg = [self.opcodes[self.rip+1]]
                self.rip+=2
            elif self.opcodes[self.rip]==0x1a:
                s = 'dec reg{}'.format(self.opcodes[self.rip+1])
                self.reg[self.opcodes[self.rip+1]]-=1
                self.inuse_reg = [self.opcodes[self.rip+1]]
                self.rip+=2
            elif self.opcodes[self.rip]==0x1b:
                s = 'mov reg{},[reg{}]'.format(self.opcodes[self.rip+1],self.opcodes[self.rip+2])
                self.inuse_reg = [self.opcodes[self.rip+1],self.opcodes[self.rip+2]]
                if self.reg[self.opcodes[self.rip+2]]<self.ds:
                    self.reg[self.opcodes[self.rip+1]] = self.dword(self.reg[self.opcodes[self.rip+2]]-self.cs-self.rip)
                else:
                    if self.data.get(self.reg[self.opcodes[self.rip+2]]-self.ds)==None:
                        self.reg[self.opcodes[self.rip+1]] = 0
                    else:
                        self.reg[self.opcodes[self.rip+1]] = self.data.get(self.reg[self.opcodes[self.rip+2]]-self.ds)
                self.rip+=3
            elif self.opcodes[self.rip]==0x1c:
                s = 'mov [reg{}],reg{}'.format(self.opcodes[self.rip+1],self.opcodes[self.rip+2])
                self.inuse_reg = [self.opcodes[self.rip+1],self.opcodes[self.rip+2]]
                if self.reg[self.opcodes[self.rip+1]]<self.ds:
                    for i in range(4):
                        by = int.to_bytes(self.reg[self.opcodes[self.rip+2]],length=4,byteorder='little')
                        self.opcodes[self.reg[self.opcodes[self.rip+1]]-self.cs+i] = by[i]
                else:
                    self.data[self.reg[self.opcodes[self.rip+1]]-self.ds] = self.reg[self.opcodes[self.rip+2]]
                self.rip+=3
            elif self.opcodes[self.rip]==0x1d:
                s = 'exit'
                self.rip+=1
            elif self.opcodes[self.rip]==0x1e:
                sign = self.opcodes[self.rip+1]
                if sign==1:
                    s = 'push {}'.format(hex(self.dword(2)))
                    self.stack.append(self.dword(2))
                    self.rip+=6
                else:
                    s = 'push reg{}'.format(self.opcodes[self.rip+2])
                    self.stack.append(self.reg[self.opcodes[self.rip+2]])
                    self.inuse_reg = [self.opcodes[self.rip+2]]
                    self.rip+=3
            elif self.opcodes[self.rip]==0x1f:
                s = 'pop reg{}'.format(self.opcodes[self.rip+1])
                self.reg[self.opcodes[self.rip+1]] = self.stack.pop()
                self.inuse_reg = [self.opcodes[self.rip+1]]
                self.rip+=2
            elif self.opcodes[self.rip]==0x20:
                s = 'syscall {}'.format(hex(self.opcodes[self.rip+1]))
                self.syscall(self.opcodes[self.rip+1])
                self.rip+=2
            else:
                self.wrong()
            hex_code = ''
            if self.ripj==-1:
                for i in range(self.rip0,self.rip):
                    hex_code+=str(hex(self.opcodes[i]))+' '
            else:
                for i in range(self.rip0,self.ripj):
                    hex_code+=str(hex(self.opcodes[i]))+' '
                self.ripj = -1
            self.runcode.append('{name: <8}{ase: <30}{hex}'.format(name=hex(self.cs+self.rip0),ase=s,hex=hex_code))
            if self.rip in self.bp or self.next_bp:
                self.next_bp = False
                print()
                for i in range(len(self.runcode)-min(3,len(self.runcode)),len(self.runcode)):
                    print('     '+self.runcode[i])
                try:
                    com = Compiler()
                    com.opcodes = self.opcodes[self.rip:]
                    com.cs = self.cs+self.rip
                    com.run(3)
                    print(' --> '+com.comcode[0])
                    for i in range(1,3):
                        print('     '+com.comcode[i])
                except:
                    pass
                self.inuse_reg = list(set(self.inuse_reg))
                print('\nInuse regs:')
                for i in self.inuse_reg:
                    print('reg{} {}'.format(i,hex(self.reg[i])))
                self.cmd()
            if s == 'exit':
                raise ValueError('debugger exit')
        self.log()

    def cmd(self):
        while True:
            if self.for_time==0:
                cmd0 = input('>>')
            else:
                cmd0 = self.for_cmd_list[self.for_p]
                self.for_p+=1
                if self.for_p==len(self.for_cmd_list):
                    self.for_p = 0
                    self.for_time-=1
            cmd0 = cmd0.split(' ')
            cmd = []
            for i in cmd0:
                if i!='':
                    cmd.append(i)
            prob_cmd = []
            for i in self.exe_cmd:
                if i.startswith(cmd[0]):
                    prob_cmd.append(i)
            if len(prob_cmd)==1:
                cmd[0] = prob_cmd[0]
                if cmd[0]=='regs':
                    if len(cmd)==1:
                        for i in range(32):
                            print('reg{} {}'.format(i,hex(self.reg[i])))
                        print('rip {}'.format(hex(self.cs+self.rip)))
                        print('flag {}'.format(hex(self.flag)))
                    else:
                        if cmd[1].startswith('reg'):
                            p = int(cmd[1][3:])
                            print('reg{} {}'.format(p,hex(self.reg[p])))
                        elif cmd[1]=='rip':
                            print('rip {}'.format(hex(self.cs+self.rip)))
                        elif cmd[1]=='flag':
                            print('flag {}'.format(hex(self.cs+self.rip)))
                elif cmd[0]=='stack':
                    print(','.join(hex(c) for c in self.stack)+' -->')
                elif cmd[0]=='data':
                    if len(cmd)>1:
                        a = self.data.get(eval(cmd[1])-self.ds)
                        if a==None:
                            print(0)
                        else:
                            print(hex(a))
                elif cmd[0]=='opcode':
                    try:
                        self.log_run_code()
                        print('sava data/run_opcodes.txt success')
                    except:
                        print('sava data/run_opcodes.txt fail')
                elif cmd[0]=='breakpoint':
                    if len(cmd)>1:
                        bp = eval(cmd[1])
                        bp-=self.cs
                        self.bp.append(bp)
                        print('set breakpoint{} at {}'.format(len(self.bp),hex(bp+self.cs)))
                    else:
                        for i in range(len(self.bp)):
                            print('breakpoint{} at {}'.format(1+i,hex(self.bp[i]+self.cs)))
                elif cmd[0]=='delete':
                    if len(cmd)>1:
                        p = int(cmd[1])
                        print('delete breakpoint{} at {}'.format(p,hex(self.bp[p])))
                        self.bp.remove(self.bp[p])
                elif cmd[0]=='klear':
                    self.bp = []
                    print('clear the breakpoints')
                elif cmd[0]=='for':
                    self.for_time = int(cmd[1])
                    self.for_p = 0
                    self.for_cmd_list = []
                    while True:
                        for_cmd = input('    ')
                        if 'exit'==(for_cmd):
                            self.for_p = 0
                            break
                        else:
                            self.for_cmd_list.append(for_cmd)
                elif cmd[0]=='next':
                    self.next_bp = True
                    break
                elif cmd[0]=='run':
                    t = self.bp
                    self.__init__()
                    self.bp = t
                    self.next_bp = False
                    break
                elif cmd[0]=='continue':
                    break
                elif cmd[0]=='quit':
                    raise ValueError('debugger exit')
                elif cmd[0]=='help':
                    print("""
    regs [reg_name]  Print the values in the register.
    stack            Print current stack data.
    quit             Exit program.
    run              Restart the program.
    continue         Continue running.
    opcode           Write the runtime code to./data/run_opcode.txt.
    data <address>   Print the value of the data segment address.
    next             Run to next command.
    for <time>       Write a command segment that loops time times.
    breakpoint       Set a breakpoint at address.
    delete <index>   Delete the breakpoint number index.
    klear            Clear all breakpoints.""")
                else:
                    print('Unknown command')
            else:
                print('Do you mean the below cmd')
                print('\n'.join(prob_cmd))


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
