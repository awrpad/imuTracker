from pipeline import Pipeline
from pipeline_elements import *

p = Pipeline()
p.introduce(LoadfromfileElement())

p.add_step("loadf", "meres4.txt")

p.execute()
print(p.get_data())