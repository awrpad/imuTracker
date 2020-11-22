import tkinter as tk
from tkinter import ttk
import gui_elements

class AppWindow:
    def __init__(self):
        self.title = "Data manipulation and visualisation tool - GUI"

    def start(self):
        self.root = tk.Tk()
        self.root.title(self.title)
        # Make the window maximized
        self.root.state('zoomed')

        notebook_main = ttk.Notebook(self.root)
        notebook_main.pack(fill="both", expand=1)

        frame_start = gui_elements.StartFrame(notebook_main).get()
        frame_pipeline_test = gui_elements.PipelineFrame(notebook_main, "Test pipeline").get()

        #frame_start.pack(fill="both", expand=1)
        #frame_pipeline_test.pack(fill="both", expand=1)

        notebook_main.add(frame_start, text="Main")
        notebook_main.add(frame_pipeline_test, text="Test")

        self.root.mainloop()

