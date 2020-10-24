from pipeline import PipelineElement, PipelineReturnValue, PipelineSource, PipelineSink
from imu_tools import *
import re
import matplotlib.pyplot as plt
import pyquaternion as pq

# Source, reads from the 
class LoadfromfileElement(PipelineSource):
    def __init__(self):
        super().__init__("loadf")
    
    def apply(self, data, args = None):
        f = None
        try:
            f = open(args, "r")
        except Exception as e:
            self.log("Error during opening the file '" + args + "', cause: " + str(e))
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
        if len(data_read) <= 0:
            self.log("No lines match the required format.")
            return PipelineReturnValue(2, None)
        
        self.log("loading was successful.")
        return(PipelineReturnValue(0, data_read))

class QuaternionPlotterElement(PipelineSink):
    def __init__(self):
        super().__init__("quatplot")
    
    def apply(self, data, args = None):
        print("Quat plot...")
        plt.plot(time1(data), quat_w(data), label="QuatW")
        plt.plot(time1(data), quat_x(data), label="QuatX")
        plt.plot(time1(data), quat_y(data), label="QuatY")
        plt.plot(time1(data), quat_z(data), label="QuatZ")
        plt.legend(loc="upper left")
        plt.show()
        return PipelineReturnValue(0, None)

class AccelPlotterElement(PipelineSink):
    def __init__(self):
        super().__init__("accplot")
    
    def apply(self, data, args = None):
        print("Quat plot...")
        plt.plot(time1(data), acc_x(data), label="AccX")
        plt.plot(time1(data), acc_y(data), label="AccY")
        plt.plot(time1(data), acc_z(data), label="AccZ")
        plt.legend(loc="upper left")
        plt.show()
        return PipelineReturnValue(0, None)
    
class SliceElement(PipelineElement):
    def __init__(self):
        super().__init__("slice")
    
    def apply(self, data, args = None):
        if type(args) is not str:
            self.log("Wrong input type")
            return PipelineReturnValue(1, None)
        if len(args) <= 1 or ":" not in args:
            self.log("Syntax error")
            return PipelineReturnValue(2, None)
        args = args.strip()
        elements = args.split(":")
        if len(elements) != 2:
            self.log("Syntax error")
            return PipelineReturnValue(2, None)
        start = None
        end = None
        try:
            if not elements[0] == "":
                start = int(elements[0])
            if not elements[1] == "":
                end = int(elements[1])
        except Exception as e:
            self.log("The input '" + args + "' cannot be converted to integers. Cause: " + str(e))
            return PipelineReturnValue(3, None)
        
        self.log("Slicing ~> " + str(start) + " \|/ " + str(end))
        return PipelineReturnValue(0, data[start:end])

class PrintInfoElement(PipelineElement):
    def __init__(self):
        super().__init__("printinfo")
    
    def apply(self, data, args=None):
        siz = len(data)
        dtime = (time1(data)[-1] - time1(data)[0]) / 1000000 #Convert microsec to sec
        timediff_sum = 0
        timediff_max = -1
        timediff_min = 100000
        t1 = time1(data)
        t2 = time2(data)
        for i in range(siz):
            timediff = t2[i] - t1[i]
            if timediff < timediff_min:
                timediff_min = timediff
            if timediff > timediff_max:
                timediff_max = timediff
            timediff_sum += timediff
        timediff_min /= 1000
        timediff_max /= 1000
        timediff_sum /= 1000

        self.log("Info:")
        self.log("\tData size: " + str(siz))
        self.log("\tTime duration: " + str(dtime) + " s")
        self.log("\tSample frequency: " + str(siz/dtime) + " Hz")
        self.log("\tTime1, time2 diff min: " + str(timediff_min) + " ms")
        self.log("\tTime1, time2 diff max: " + str(timediff_max) + " ms")
        self.log("\tTime1, time2 diff avg: " + str(timediff_sum / siz) + " ms")
        self.log("End info.")
        return PipelineReturnValue(0, data)
    
class MovingAverageElement(PipelineElement):
    def __init__(self):
        super().__init__("mavg")
    
    def apply(self, data, args=None):
        if args is None or len(args) < 3:
            self.log("Syntax error in moving average: the frame length and axis enumeration are needed.")
            self.log("Correct form example: 'mavg 3:xy'")
            return PipelineReturnValue(1, None)
        argarr = args.split(":")
        if len(argarr) != 2:
            self.log("Syntax error: Exactly two parameters are needed.")
            self.log("Correct form example: 'mavg 3:xy'")
            return PipelineReturnValue(1, None)
        n = -1
        try:
            argN = argarr[0].strip()
            n = int(argN)
        except Exception as e:
            self.log("Cannot convert the parameter '" + argN + "' to integer.")
            self.log("Correct form example: 'mavg 3:xy'")
            return PipelineReturnValue(2, None)
        if "x" not in argarr[1] and "y" not in argarr[1] and "z" not in argarr[1]:
            self.log("Wrong input for axis selection. Usage: <[x][y][z]>")
            self.log("Correct form example: 'mavg 3:xy'")
            return PipelineReturnValue(1, None)
        outx = acc_x(data)
        outy = acc_y(data)
        outz = acc_z(data)
        if "x" in argarr[1]:
            outx = moving_average(n, outx)
        if "y" in argarr[1]:
            outy = moving_average(n, outy)
        if "z" in argarr[1]:
            outz = moving_average(n, outz)
        outarr = []
        for i, v in enumerate(data):
            outarr.append(IMUData(
                outx[i], outy[i], outz[i],
                data[i].quat_w, data[i].quat_x, data[i].quat_y, data[i].quat_z,
                data[i].time1, data[i].time2
            ))
        self.log("Original length: " + str(len(data)) + ". New length: " + str(len(outarr)))

        return PipelineReturnValue(0, outarr)

# Applies a moving average then moves the whole signal
class AutoHeigthAdjustionElement(PipelineElement):
    def __init__(self):
        super().__init__("aha")
        self.mavg_executer = MovingAverageElement()

    def apply(self, data, args=None):
        # Set parameters to a default value if none was given
        if args == "":
            args = "25:20:xyz"

        if args is None or len(args) < 5:
            self.log("Syntax error in moving AutoHeigthAdjustion: the frame and sample length and the axis selection string are required.")
            self.log("Correct form example: 'aha 3:4:xy'")
            return PipelineReturnValue(1, None)
        frame = -1
        sample_length = 0
        try:
            argarr = args.split(":")
            frame = int(argarr[0])
            sample_length = int(argarr[1])
            axes = argarr[2]
        except Exception as e:
            self.log("Error during interpreting the parameters. Cause: " + str(e))
            return PipelineReturnValue(1, None)
        if "x" not in axes and "y" not in axes and "z" not in axes:
            self.log("Wrong input for axis selection. Usage: <[x][y][z]>")
            self.log("Correct form example: 'aha 3:4:xy'")
            return PipelineReturnValue(1, None)
        
        if sample_length > len(data) or sample_length < 1:
            self.log("Invalid sample size: " + str(sample_length))
            return(2, None)
        
        temp = self.mavg_executer.apply(data, str(frame) + ":" + axes).data
        #sample_length *= -1
        #sample_arr = temp[sample_length:] #IMUData array
        sample_arr = temp[frame:(sample_length + frame)]
        adjx = acc_x(data)
        adjy = acc_y(data)
        adjz = acc_z(data)
        if "x" in axes:
            nX = sum(acc_x(sample_arr)) / len(sample_arr)
            adjx = adjust(nX, adjx)
        if "y" in axes:
            nY = sum(acc_y(sample_arr)) / len(sample_arr)
            adjy = adjust(nY, adjy)
        if "z" in axes:
            nZ = sum(acc_z(sample_arr)) / len(sample_arr)
            adjz = adjust(nZ, adjz)
        toreturn = []
        for i, v in enumerate(data):
            toreturn.append(IMUData(
                adjx[i], adjy[i], adjz[i],
                data[i].quat_w, data[i].quat_x, data[i].quat_y, data[i].quat_z,
                data[i].time1, data[i].time2
            ))
        
        return PipelineReturnValue(0, toreturn)

class ConvertElement(PipelineElement):
    def __init__(self):
        super().__init__("convert")
        self.__quaternion_multiplier = 1.0 / (1 << 14)
        self.__acceleration_multiplier = 1.0 / 100.0
    
    def apply(self, data, args=None):
        modified = []
        for d in data:
            # Convert the quaternion values to unit
            unit_quat = pq.Quaternion(d.quat_w, d.quat_x, d.quat_y, d.quat_z).unit
            modified.append(IMUData(
                d.acc_x * self.__acceleration_multiplier,
                d.acc_y * self.__acceleration_multiplier,
                d.acc_z * self.__acceleration_multiplier,
                unit_quat.w,
                unit_quat.x,
                unit_quat.y,
                unit_quat.z,
                d.time1,
                d.time2
            ))
        
        return PipelineReturnValue(0, modified)

class ZeroizeElement(PipelineElement):
    def __init__(self):
        super().__init__("zeroize")
    
    def apply(self, data, args=None):
        if args is None or len(args) < 3 or "=" not in args:
            self.log("Syntax error in moving zeroizing: The parameter is not in the right format.")
            self.log("Correct form example: 'zeroize i=73'")
            return PipelineReturnValue(1, None)
        zeroizer_data = None
        argparts = args.strip().split("=")
        self.log(str(argparts))
        # Get the corresponding quaternion according to the first part of the argument
        try:
            if argparts[0] == "i":
                zeroizer_data = data[int(argparts[1])]
                self.log("Selected data element: " + str(zeroizer_data))
        except Exception as e:
            self.log("Error during searching for the zeroizer measurement. Cause: " + str(e))
        
        zeroizer = pq.Quaternion(-1.0 + zeroizer_data.quat_w, zeroizer_data.quat_x, zeroizer_data.quat_y, zeroizer_data.quat_z)
        self.log("Zeroizer quaternion: " + str(zeroizer))

        # Modify each data element with the zeroizer
        newarr = []
        for d in data:
            self.log("Orig: " + str(d))
            newarr.append(IMUData(
                d.acc_x, d.acc_y, d.acc_z,
                d.quat_w - zeroizer.w,
                d.quat_x - zeroizer.x,
                d.quat_y - zeroizer.y,
                d.quat_z - zeroizer.z,
                d.time1, d.time2
            ))
            self.log("Modi: " + str(newarr[-1]))
        
        return PipelineReturnValue(0, newarr)


# Functions for use in the classes
def moving_average(n, array):
    smoothened = []
    for i, v in enumerate(array):
        if i < n:
            smoothened.append(v)
            continue
        helper = array[i - n : i + n + 1]
        smoothened.append(sum(helper) / float(len(helper)))
    
    return smoothened

adjust = lambda n, array: [x - n for x in array]
        