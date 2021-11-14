# vmp
vmp debugger&amp;compiler

## Usage

请先看Quick Start。

```shell
python3 run.py -d # run dubgger
python3 run.py -c # run compiler
```

### compiler

运行后日志输出到./data/com_log.txt，格式为地址、汇编码、虚拟机16进制指令。

### debugger

运行后进入交互界面。

实现了['regs','stack','quit','run','continue','opcode','data','next','for','breakpoint','delete','klear']的功能，只需输入前几位即可执行指令。

regs [reg0~32] or regs flag or regs rip：打印寄存器内数值，当仅输入regs时打印所有寄存器数值。

stack：打印当前栈内数据。

quit：程序退出。

run：重新运行程序。

continue：继续运行。

opcode：将运行时的代码写入./data/run_opcode.txt。

data < address >：打印数据段address的值。

next：运行至下一条指令。

for < time >：自由编写一个循环time次的命令段。

```
>>for 5
    reg reg0
    exit
reg0 0x103a
reg0 0x103a
reg0 0x103a
reg0 0x103a
reg0 0x103a
```

breakpoint [address]：在address处下一个断点，没有address时，打印所有断点信息。

delete < index >：删除编号为index的断点。

klear：清除全部断点。

help：打印帮助文档。

运行后日志输出到./data/run_log.txt。

## Quick Start

IDA打开./file/VMP，IDA(version>=7.5) File->Script file，选择./idascript/pick_code.py，把输出写入新建路文件./data/opcodes.txt，然后就可以run debugger，并在0x103a处下断点。然后使用opcode命令输出运行时指令到./data/run_opcodes.txt。

```
>>b 0x103a
>>o
```

之后就可以运行compiler了。

获取run_opcodes也可以直接File->Script file，选择./idascript/xor.py，然后再选择./idascript/pick_code.py，把输出写入文件 ./data/run_opcodes.txt。
