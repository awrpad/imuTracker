import tkinter as tk
from tkinter import ttk
from visualizer_core import VisualizerCore

class StyleScheme:
    # Colors
    color_background = "lightgray"
    color_foreground1 = "white"
    color_foreground2 = "blue"

    # Fonts
    font_title = ("Arial", 72)
    font_subtitle = ("Arial", 36)

class StartFrame:
    def __init__(self, root):
        self.root = root
        self.str_welcome = "Welcome"
        self.str_add_pipeline = "Add pipeline"
        self.str_newpipeline_name = "New pipeline name"
        self.str_create = "Create"
    
    def get(self):
        frame_main = tk.Frame(self.root, bg=StyleScheme.color_background)
        label_welcome = tk.Label(frame_main, text=self.str_welcome, bg=StyleScheme.color_background, fg=StyleScheme.color_foreground1)
        label_add_pipeline = ttk.Label(frame_main, text=self.str_add_pipeline, bg=StyleScheme.color_background, font=StyleScheme.font_subtitle)
        label_newpipeline_name = tk.Label(frame_main, text=self.str_newpipeline_name, bg=StyleScheme.color_background)
        button_create = ttk.Button(frame_main, text=self.str_create)
        entry_newpipeline_name = tk.Entry(frame_main, width=40, bg=StyleScheme.color_background, fg=StyleScheme.color_foreground2)

        label_welcome.configure(font=StyleScheme.font_title)

        label_welcome.grid(row=0, column=0, columnspan=3, sticky="wens")
        label_add_pipeline.grid(row=1, column=0, columnspan=3, sticky="wens")
        label_newpipeline_name.grid(row=2, column=0, sticky="wens")
        entry_newpipeline_name.grid(row=2, column=1, sticky="wens")
        button_create.grid(row=2, column=2, sticky="wens")

        return frame_main

def templog(msg, loglevel = 0):
    print(msg)

class PipelineFrame:
    def __init__(self, root, pipeline_name):
        self.pipeline_name = pipeline_name
        self.root = root
    
    def get(self):
        # TODO: Actual i/o
        core = VisualizerCore(input, templog)
        core.add_pipeline(self.pipeline_name)

        frame_main = tk.Frame(self.root, bg=StyleScheme.color_background)
        label_pipelinename = tk.Label(frame_main, text=self.pipeline_name, font=StyleScheme.font_title)
        listbox_selector = tk.Listbox(frame_main, width=25)
        
        possibilities = core.get_pipeline(self.pipeline_name).get_possibilities()
        
        for pos in possibilities:
            listbox_selector.insert(tk.END, pos.get_name())
        
        label_pipelinename.pack(fill="both", expand=0)
        listbox_selector.pack()

        return frame_main

class PipelineElementViewRepository:
    def __init__(self):
        self.a = "b"
    
    # TODO: Implement
    def get_view_for(self, element_name):
        return True