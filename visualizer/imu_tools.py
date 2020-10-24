from collections import namedtuple

IMUData = namedtuple("IMUData", ["acc_x", "acc_y", "acc_z", "quat_w", "quat_x", "quat_y", "quat_z", "time1", "time2"])

acc_x = lambda data_array: [x.acc_x for x in data_array]
acc_y = lambda data_array: [x.acc_y for x in data_array]
acc_z = lambda data_array: [x.acc_z for x in data_array]
quat_w = lambda data_array: [x.quat_w for x in data_array]
quat_x = lambda data_array: [x.quat_x for x in data_array]
quat_y = lambda data_array: [x.quat_y for x in data_array]
quat_z = lambda data_array: [x.quat_z for x in data_array]
time1 = lambda data_array: [x.time1 for x in data_array]
time2 = lambda data_array: [x.time2 for x in data_array]
