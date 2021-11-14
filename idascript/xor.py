import idc
import ida_bytes

ed = 0x804DF9B
st = 0x804d0fa
for i in range(st,ed,4):
    ida_bytes.patch_dword(i,idc.get_wide_dword(i)^0x174cf42)