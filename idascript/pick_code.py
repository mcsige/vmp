import idc
import os

ed = 0x804DFA0
st = 0x804d0c0
l = []
for i in range(st,ed):
    l.append(idc.get_wide_byte(i))

print(str(l)[1:-1])

# path = ''

# f = open(os.path.join(path,'data/opcodes_test'),'w')
# f.write(str(l)[1:-1])
# f.close()