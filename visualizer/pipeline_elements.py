from pipeline import PipelineElement, PipelineReturnValue
from imu_tools import IMUData
import re
class LoadfromfileElement(PipelineElement):
    def __init__(self):
        super().__init__("loadf")
    
    def apply(self, data, args = None):
        f = None
        try:
            f = open(args, "r")
        except Exception as identifier:
            print("Error during opening the file '" + args + "', cause: ", identifier)
            return PipelineReturnValue(1, None)
        temp = f.readlines()
        filtered = filter(lambda line: re.match(r"^(-?\d+(\.\d+)?\t){7}\d+\t\d+$", line.strip("\r")), temp)
        
        data_read = []
        for x in filtered:
            splitted = x.split("\t")
            data_read.append(
                IMUData(
                    float(splitted[0]),
                    float(splitted[1]),
                    float(splitted[2]),
                    float(splitted[3]),
                    float(splitted[4]),
                    float(splitted[5]),
                    float(splitted[6]),
                    int(splitted[7]),
                    int(splitted[8])
                )
            )
            print(data_read[-1])
        if len(data_read) <= 0:
            print("No lines match the required format.")
            return PipelineReturnValue(2, None)
        
        return(PipelineReturnValue(0, data_read))