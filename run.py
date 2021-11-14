from debugger import Debugger
from compiler import Compiler
import traceback

# dbg = Debugger()
# try:
#     dbg.run(bp = [0x103a])
# except:
#     traceback.print_exc()
#     dbg.log()
#     dbg.wrong()

com = Compiler()
try:
    com.run()
except:
    traceback.print_exc()
    com.log()
    com.wrong()


