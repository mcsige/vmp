from debugger import Debugger
from disassembler import Compiler
import traceback
import argparse

def run_debugger():
    dbg = Debugger()
    try:
        dbg.run(bp = [])
    except (ValueError) as e:
        print(e)
    except:
        traceback.print_exc()
        pass
    finally:
        dbg.log()
        print('save ./data/run_log.txt success')

def run_compiler():
    com = Compiler()
    try:
        com.run()
    except (ValueError) as e:
        print(e)
    except:
        traceback.print_exc()
        pass
    finally:
        com.log()
        print('save ./data/com_log.txt success')

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='vmp compiler&debugger')
    parser.add_argument('-c',action='store_true',help='run decompiler with data/run_opcodes')
    parser.add_argument('-d',action='store_true',help='run debugegr with data/opcodes')
    # parser.add_argument('-code',type=str,help='identification the decompiler/debugger code path')
    # parser.add_argument('-log',type=str,help='identification the decompiler/debugger log path')
    args = parser.parse_args()
    if args.c:
        run_compiler()
    elif args.d:
        run_debugger()
    


