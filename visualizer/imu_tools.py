from collections import namedtuple

IMUData = namedtuple("IMUData", ["acc_x", "acc_y", "acc_z", "quat_w", "quat_x", "quat_y", "quat_z", "time1", "time2"])