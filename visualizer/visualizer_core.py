print("Core starting...")
from pipeline import Pipeline
from pipeline_elements import *

def myprint(msg):
    #print("Hello, this is my own print method", msg)
    print("<- ", msg)

p = Pipeline("TestPipeline", myprint)
p.introduce(LoadfromfileElement())
p.introduce(QuaternionPlotterElement())
p.introduce(AccelPlotterElement())
p.introduce(SliceElement())
p.introduce(PrintInfoElement())
p.introduce(MovingAverageElement())
p.introduce(AutoHeigthAdjustionElement())
p.introduce(ConvertElement())
p.introduce(ZeroizeElement())

"""p.add_step("test", "213 456 673")
p.add_step("loadf", "meres444.txt")

p.execute()
#print(p.get_data())"""

print("Core started.")
cmd = input("~> ")
while cmd != ":exit":
    if cmd == ":run":
        p.execute()
        p.clear_steps()
    else:
        p.parse_string(cmd)
    cmd = input("~> ")