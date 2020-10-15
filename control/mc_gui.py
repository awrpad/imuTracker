import tkinter as tk

root = tk.Tk()
root.title("IMU Tracker Control GUI")

w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))

def start():
    root.mainloop()