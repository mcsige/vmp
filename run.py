from debugger import Debugger
from compiler import Compiler
import traceback

dbg = Debugger()
try:
    dbg.run(bp = [0x1d8e])
except:
    dbg.log()
    traceback.print_exc()
    dbg.wrong()

# com = Compiler()
# try:
#     com.run()
# except:
#     traceback.print_exc()
#     com.log()

11111111111111111111111111111
