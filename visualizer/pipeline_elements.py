from pipeline import PipelineElement, PipelineReturnValue, PipelineSource, PipelineSink
from imu_tools import *
import re
import matplotlib.pyplot as plt
import pyquaternion as pq
import numpy as np
import vpython as vp
import time

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

class PosPlotElement(PipelineSink):
    def __init__(self):
        super().__init__("posplot")
    
    def apply(self, data, args=None):
        plt.plot(ptime(data), pos_x(data), label="PosX")
        plt.plot(ptime(data), pos_y(data), label="PosY")
        plt.plot(ptime(data), pos_z(data), label="PosZ")
        plt.legend(loc="upper left")
        plt.show()
        return PipelineReturnValue(0, None)

class OrientationPlotterElement(PipelineSink):
    def __init__(self):
        super().__init__("orplot")
    
    def __quaternion_rotate_vpvector__(self, vector, quaternion):
        new_x, new_y, new_z = quaternion.rotate((vector.x, vector.y, vector.z))
        new_vec = vp.vector(new_x, new_y, new_z)

        return new_vec
    
    def apply(self, data, args=None):
        vp.scene.width = 500
        vp.scene.height = 500

        arrow_worldframe_x = vp.arrow(axis=vp.vector(1, 0, 0), color=vp.color.red, length=2, shaftwidth=0.075)
        arrow_worldframe_y = vp.arrow(axis=vp.vector(0, 1, 0), color=vp.color.green, length=2, shaftwidth=0.075)
        arrow_worldframe_z = vp.arrow(axis=vp.vector(0, 0, 1), color=vp.color.blue, length=2, shaftwidth=0.075)
        label_wfx = vp.text(text="WX", pos=vp.vector(2.15, -0.1, -0.1), billboard=True, height=0.15)
        label_wfy = vp.text(text="WY", pos=vp.vector(-0.1, 2.15, -0.1), billboard=True, height=0.15)
        label_wfz = vp.text(text="WZ", pos=vp.vector(-0.1, -0.1, 2.15), billboard=True, height=0.15)

        vec_ex = vp.vector(1, 0, 0)
        vec_ey = vp.vector(0, 1, 0)
        vec_ez = vp.vector(0, 0, 1)

        arrow_objframe_x = vp.arrow(axis=vec_ex, color=vp.color.cyan, length=1, shaftwidth=0.1)
        arrow_objframe_y = vp.arrow(axis=vec_ey, color=vp.color.magenta, length=1, shaftwidth=0.1)
        arrow_objframe_z = vp.arrow(axis=vec_ez, color=vp.color.yellow, length=1, shaftwidth=0.1)

        self.log("Starting in 10s...")
        time.sleep(10)
        self.log("Starting")

        counter = 0
        for d in data:
            time.sleep(0.1)
            self.log("i = " + str(counter) + "; t = " + str(d.time2))
            quatcurrent = pq.Quaternion(d.quat_w, d.quat_x, d.quat_y, d.quat_z)
            rotated_vec_x = self.__quaternion_rotate_vpvector__(vec_ex, quatcurrent)
            rotated_vec_y = self.__quaternion_rotate_vpvector__(vec_ey, quatcurrent)
            rotated_vec_z = self.__quaternion_rotate_vpvector__(vec_ez, quatcurrent)

            arrow_objframe_x.axis = rotated_vec_x
            arrow_objframe_y.axis = rotated_vec_y
            arrow_objframe_z.axis = rotated_vec_z
            counter += 1
        
        return PipelineReturnValue(0, None)

class ShowPos2DElement(PipelineSink):
    def __init__(self):
        super().__init__("pos2d")
    
    def __get_axis__(self, data, axis_str):
        if axis_str == "x":
            return pos_x(data)
        if axis_str == "y":
            return pos_y(data)
        if axis_str == "z":
            return pos_z(data)
    
    def apply(self, data, args=None):
        args = args.strip()
        if args is None or len(args) != 2:
            self.log("Syntax error in 2D pos plot: The parameter should contain exactly two from the characters 'x', 'y' and 'z'")
            return PipelineReturnValue(1, None)
        a1 = self.__get_axis__(data, args[0])
        a2 = self.__get_axis__(data, args[1])

        plt.scatter(a1, a2)
        plt.title("Position of the object on the " + args[0] + "-" + args[1] + " plane.")
        plt.axes().set_aspect('equal', 'datalim')
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
            #new_quat = pq.Quaternion(d.quat_w, d.quat_x, d.quat_y, d.quat_z).unit
            new_quat = pq.Quaternion(d.quat_w * self.__quaternion_multiplier,
                d.quat_x * self.__quaternion_multiplier,
                d.quat_y * self.__quaternion_multiplier,
                d.quat_z * self.__quaternion_multiplier
            ).unit
            modified.append(IMUData(
                d.acc_x * self.__acceleration_multiplier,
                d.acc_y * self.__acceleration_multiplier,
                d.acc_z * self.__acceleration_multiplier,
                new_quat.w,
                new_quat.x,
                new_quat.y,
                new_quat.z,
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
            newarr.append(IMUData(
                d.acc_x, d.acc_y, d.acc_z,
                d.quat_w - zeroizer.w,
                d.quat_x - zeroizer.x,
                d.quat_y - zeroizer.y,
                d.quat_z - zeroizer.z,
                d.time1, d.time2
            ))
        
        return PipelineReturnValue(0, newarr)

class QuaternionAdjustionElement(PipelineElement):
    def __init__(self):
        super().__init__("quatadj")
    
    def apply(self, data, args=None):
        new_quaternions = []
        new_time2s= [data[0].time1]
        n = 10
        for i, v in enumerate(data):
            if i == 0:
                new_quaternions.append(pq.Quaternion(v.quat_w, v.quat_x, v.quat_y, v.quat_z))
            else:
                quat_before = pq.Quaternion(data[i - 1].quat_w, data[i - 1].quat_x, data[i - 1].quat_y, data[i - 1].quat_z)
                quat_current = pq.Quaternion(data[i].quat_w, data[i].quat_x, data[i].quat_y, data[i].quat_z)
                qtime_before = data[i - 1].time2
                qtime_current = data[i].time2
                atime_current = data[i].time1
                t_diff_sum = qtime_current - qtime_before
                t_diff = t_diff_sum / n
                k = 0
                while qtime_before + k * t_diff < atime_current:
                    k += 1
                qadjusted = list(pq.Quaternion.intermediates(quat_before, quat_current, n))[k]
                new_quaternions.append(qadjusted)
                new_time2s.append(qtime_before + k * t_diff)
        # New quaternions generated, adjust the data
        new_data = []
        for i, v in enumerate(data):
            qnew = new_quaternions[i]
            new_data.append(IMUData(
                v.acc_x, v.acc_y, v.acc_z,
                qnew.w, qnew.x, qnew.y, qnew.z,
                v.time1, new_time2s[i]
            ))
            if data[i].quat_w - new_data[i].quat_w > 0.0001:
                self.log("Modified quaternion: ")
                self.log("O: " + str(data[i]))
                self.log("M: " + str(new_data[i]))
        
        return PipelineReturnValue(0, new_data)

class FrameOfReferenceRotationElement(PipelineElement):
    def __init__(self):
        super().__init__("forr")
    
    def apply(self, data, args=None):
        new_data = []
        for d in data:
            quat = pq.Quaternion(d.quat_w, d.quat_x, d.quat_y, d.quat_z)
            new_vec = quat.rotate([d.acc_x, d.acc_y, d.acc_z])
            new_data.append(IMUData(
                new_vec[0], new_vec[1], new_vec[2],
                1, 0, 0, 0, # The quaternion now is the same as the non-changing frame of reference
                d.time1, d.time2
            ))
        
        return PipelineReturnValue(0, new_data)

class AccelToPosElement(PipelineElement):
    def __init__(self):
        super().__init__("atop")
    
    def apply(self, data, args=None):
        posx = second_integral(acc_x(data), time1(data))
        posy = second_integral(acc_y(data), time1(data))
        posz = second_integral(acc_z(data), time1(data))

        new_data = []
        for i, _ in enumerate(posx):
            new_data.append(PositionData(posx[i], posy[i], posz[i], data[i].time1))
        
        return PipelineReturnValue(0, new_data)

class SecondIntegralBasedHeigthAdjustionElement(PipelineElement):
    def __init__(self):
        super().__init__("sibha")
    
    def sibha(self, acc_values, time_values, value_wanted, tolerance = 0.001):
        adjusted = acc_values
        pos_values = integrate(integrate(adjusted, time_values), time_values)
        sum_adjust = 0
        
        while abs(value_wanted - pos_values[-1]) > tolerance:
            diff = value_wanted - pos_values[-1]
            adjust = diff / 100.0
            sum_adjust += adjust
            adjusted = apply_offset(adjusted, adjust)
            pos_values = integrate(integrate(adjusted, time_values), time_values)
        
        self.log("Sum adjustion: " + str(sum_adjust))
        return adjusted
    
    def apply(self, data, args=None):
        wanted_x = wanted_y = wanted_z = 0
        try:
            argarr = args.split(":")
            if len(argarr) != 3:
                raise Exception("Wrong number of arguments.")
            wanted_x = float(argarr[0])
            wanted_y = float(argarr[1])
            wanted_z = float(argarr[2])
        except Exception as e:
            self.log("Error during SIBHA. Cause: " + str(e))
        
        self.log("Adjusting X axis...")
        newx = self.sibha(acc_x(data), time1(data), wanted_x)
        self.log("Adjusting Y axis...")
        newy = self.sibha(acc_y(data), time1(data), wanted_y)
        self.log("Adjusting Z axis...")
        newz = self.sibha(acc_z(data), time1(data), wanted_z)

        newarr = []
        for i, _ in enumerate(data):
            newarr.append(IMUData(
                newx[i], newy[i], newz[i],
                data[i].quat_w,  data[i].quat_x,  data[i].quat_y,  data[i].quat_z,
                data[i].time1, data[i].time2
            ))
        
        return PipelineReturnValue(0, newarr)

class Plot3dMovementElement(PipelineSink):
    def __init__(self):
        super().__init__("pos3d")
    
    def apply(self, data, args=None):
        f = plt.figure()
        ax = f.gca(projection="3d")
        ax.plot(pos_x(data), pos_y(data), pos_z(data), label="Position in 3D")
        ax.legend()
        ax.set_xlim3d([-1, 1])
        ax.set_ylim3d([-1, 1])
        ax.set_zlim3d([-1, 1])
        plt.show()

        return PipelineReturnValue(0, None)

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

def integrate(values, times):
    integrals = []
    multiplier_mictosec_to_sec = 10 ** -6
    for i, _ in enumerate(times):
        currTimes = [(multiplier_mictosec_to_sec) * x for x in times[:i + 1]]
        currValues = values[:i + 1]
        integrals.append(np.trapz(
            x = currTimes,
            y = currValues
        ))
        
    return integrals

second_integral = lambda values, times: integrate(integrate(values, times), times)

def apply_offset(array, n):
	offsetted = []
	
	for x in array:
		offsetted.append(x + n)
		
	return offsetted

    