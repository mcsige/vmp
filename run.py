from debugger import Debugger
from compiler import Compiler
import traceback
import argparse

def run_debugger():
    dbg = Debugger()
    try:
        dbg.run(bp = [])
    except:
        # traceback.print_exc()
        dbg.wrong()
    finally:
        dbg.log()
        print('save ./data/run_log success')

def run_compiler():
    com = Compiler()
    try:
        com.run()
    except:
        # traceback.print_exc()
        com.wrong()
    finally:
        com.log()
        print('save ./data/com_log success')

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='vmp compiler&debugger')
    parser.add_argument('-c',action='store_true',help='run compiler with data/run_opcodes')
    parser.add_argument('-d',action='store_true',help='run debugegr with data/opcodes')
    args = parser.parse_args()
    if args.c:
        run_compiler()
    elif args.d:
        run_debugger()
    


