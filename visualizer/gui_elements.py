from abc import ABC, abstractmethod

from matplotlib.pyplot import title
import pipeline_elements
import tkinter as tk
from tkinter import BooleanVar, StringVar, ttk, filedialog
from visualizer_core import VisualizerCore

class StyleScheme:
    # Colors
    color_background = "lightgray"
    color_foreground1 = "white"
    color_foreground2 = "blue"
    color_source_background = "lightblue"
    color_sink_background = "lightyellow"

    # Fonts
    font_title = ("Arial", 72)
    font_subtitle = ("Arial", 36)

    # Sizes
    size_element_entry_width = 40

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
        label_add_pipeline = tk.Label(frame_main, text=self.str_add_pipeline, bg=StyleScheme.color_background, font=StyleScheme.font_subtitle)
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

    def add_view_element(self, element_name):
        new_element_frame = tk.LabelFrame(self.frame_pipeline)
        
        button_delete_element = tk.Button(new_element_frame, text="×", bg="red", padx=1, pady=1, command=new_element_frame.pack_forget)
        
        new_element = PipelineElementViewRepository(new_element_frame).get_view_for(element_name, new_element_frame)
        element = new_element.get_underlying_element()
        if element.is_sink():
            new_element_frame.configure(bg=StyleScheme.color_sink_background)
        elif element.is_source():
            new_element_frame.configure(bg=StyleScheme.color_source_background)
        
        new_element_frame.configure(text=element.get_friendly_name())

        new_element_frame.pack(fill="x")
        button_delete_element.pack(side="right", anchor="nw")
        new_element.get_frame().pack()
    
    def generate_pipeline_str(self):
        for c in self.frame_pipeline.winfo_children():
            print("aaa")
            for cc in c.winfo_children():
                print("bbb")
                try:
                    print(cc.get_descriptor_str())
                except:
                    pass
    
    def get(self):
        # TODO: Actual i/o
        core = VisualizerCore(input, templog)
        core.add_pipeline(self.pipeline_name)

        self.frame_main = tk.Frame(self.root, bg=StyleScheme.color_background)
        frame_pipeline_composer = tk.LabelFrame(self.frame_main, text="Pipeline Composer")

        self.frame_pipeline = tk.LabelFrame(self.frame_main, text="Pipeline")
        label_pipelinename = tk.Label(self.frame_main, text=self.pipeline_name, font=StyleScheme.font_title)
        listbox_selector = tk.Listbox(frame_pipeline_composer, width=40, height=30)
        button_add = tk.Button(frame_pipeline_composer, text="Add selected element", command=lambda: self.add_view_element(
            listbox_selector.get(tk.ACTIVE).replace("(", "").replace(")", "").split()[-1]
        ))
        button_execute = tk.Button(self.frame_pipeline, text="Execute", command=self.generate_pipeline_str)
        
        possibilities = core.get_pipeline(self.pipeline_name).get_possibilities()
        
        for pos in possibilities:
            listbox_selector.insert(tk.END, pos.get_friendly_name() + " (" + pos.get_name() + ")")
        
        
        label_pipelinename.pack(fill="both", expand=0)
        frame_pipeline_composer.pack(side="left", fill="y")
        self.frame_pipeline.pack()
        listbox_selector.pack()
        button_add.pack()
        button_execute.pack()

        return self.frame_main

class PipelineElementViewRepository:
    __views = []
    def __init__(self, root):
        PipelineElementViewRepository.__views.append(LoadFileView(None))
        PipelineElementViewRepository.__views.append(MovingAverageView(None))
        PipelineElementViewRepository.__views.append(QuaternionPlotterView(None))
        PipelineElementViewRepository.__views.append(AccelerationPlotterView(None))
        PipelineElementViewRepository.__views.append(PositionPlotterView(None))
        PipelineElementViewRepository.__views.append(Position2DPlotterView(None))
        PipelineElementViewRepository.__views.append(Position3DPlotterView(None))
    
    @staticmethod
    def get_view_for(element_name, root):
        for v in PipelineElementViewRepository.__views:
            if v.get_underlying_element().get_name() == element_name:
                c = v.__class__
                return c(root)

class PipelineElementDescriptor:
    def __init__(self):
        self.element_name = None
        self.args = []
    
    def set_element_name(self, name):
        self.element_name = name

        return self
    
    def add_arg(self, newarg):
        self.args.append(str(newarg))

        return self
    
    def get_str(self):
        if self.element_name is None:
            raise Exception("Cannot make descriptor string: Element name is not set.")

        toreturn = self.element_name
        if len(self.args > 0):
            toreturn += " "
        for i, arg in enumerate(self.args):
            if i > 0:
                toreturn += ":"
            toreturn += arg
        
        return toreturn

class ElementView(ABC):
    def __init__(self, root):
        # This two should be in the base class constructor
        self._descriptor = PipelineElementDescriptor()
        self._root = root
    
    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def get_descriptor_str(self):
        pass

    @abstractmethod
    def get_underlying_element(self):
        pass

class LoadFileView(ElementView):
    def __init__(self, root):
        super().__init__(root)
        
    def get_frame(self):
        self.frame_main = tk.Frame(self._root)
        self.label_name = tk.Label(self.frame_main, text="Filename")
        self.entry_filename = tk.Entry(self.frame_main, width=StyleScheme.size_element_entry_width)
        self.button_file_from_dialog = tk.Button(self.frame_main, text="Browse", command=self.__file_from_dialog)

        self.label_name.pack(fill="both")
        self.entry_filename.pack(fill="both")
        self.button_file_from_dialog.pack()

        return self.frame_main
    
    def get_descriptor_str(self):
        return self._descriptor.set_element_name("loadf").add_arg(self.entry_filename.get()).get_str()

    def get_underlying_element(self):
        return pipeline_elements.LoadfromfileElement()
    
    def __file_from_dialog(self):
        dialogresult = filedialog.askopenfilename(title="Select file to read values from", filetypes=(("TXT files", "*.txt"), ("All files", "*.*")))
        if dialogresult is None or dialogresult == "":
            return
        
        # Here we are sure that the result contains a filename
        self.entry_filename.delete(0, tk.END)
        self.entry_filename.insert(0, dialogresult)

class MovingAverageView(ElementView):
    def __init__(self, root):
        super().__init__(root)
        
        self.frame_main = tk.Frame(self._root)
        self.label_window = tk.Label(self.frame_main, text="Window")
        self.entry_window = tk.Entry(self.frame_main, width=StyleScheme.size_element_entry_width)
        self.applytox = BooleanVar()
        self.applytoy = BooleanVar()
        self.applytoz = BooleanVar()
        self.label_name = tk.Label(self.frame_main, text="Apply to axis:")
        self.cb_applytox = tk.Checkbutton(self.frame_main, text="X", variable=self.applytox, onvalue=True, offvalue=False)
        self.cb_applytoy = tk.Checkbutton(self.frame_main, text="Y", variable=self.applytoy, onvalue=True, offvalue=False)
        self.cb_applytoz = tk.Checkbutton(self.frame_main, text="Z", variable=self.applytoz, onvalue=True, offvalue=False)
        self.cb_applytox.select()
        self.cb_applytoy.select()
        self.cb_applytoz.select()

        self.label_window.pack()
        self.entry_window.pack()
        self.cb_applytox.pack()
        self.cb_applytoy.pack()
        self.cb_applytoz.pack()

    def get_frame(self):
        return self.frame_main
    
    def get_descriptor_str(self):
        apply_to_axes = ""
        if self.applytox.get():
            apply_to_axes += "x"
        if self.applytoy.get():
            apply_to_axes += "y"
        if self.applytoz.get():
            apply_to_axes += "z"
        
        return self._descriptor.set_element_name("mavg").add_arg(self.entry_window.get()).add_arg(apply_to_axes)
    
    def get_underlying_element(self):
        return pipeline_elements.MovingAverageElement()

class QuaternionPlotterView(ElementView):
    def __init__(self, root):
        super().__init__(root)
    
    def get_frame(self):
        self.frame_main = tk.Frame(self._root)
        self.label_title = tk.Label(self.frame_main, text="Quaternion plot")
        self.frame_main.pack(fill="both")
        self.label_title.pack(fill="both")

        return self.frame_main
    
    def get_descriptor_str(self):
        return self._descriptor.set_element_name(self.get_underlying_element().get_name())
    
    def get_underlying_element(self):
        return pipeline_elements.QuaternionPlotterElement()

class AccelerationPlotterView(ElementView):
    def __init__(self, root):
        super().__init__(root)

    def get_frame(self):
        self.frame_main = tk.Frame(self._root)
        self.label_title = tk.Label(self.frame_main, text="Acceleration plot")
        self.frame_main.pack(fill="both")
        self.label_title.pack(fill="both")

        return self.frame_main
    
    def get_descriptor_str(self):
        return self._descriptor.set_element_name(self.get_underlying_element().get_name())
    
    def get_underlying_element(self):
        return pipeline_elements.AccelPlotterElement()

class PositionPlotterView(ElementView):
    def __init__(self, root):
        super().__init__(root)

    def get_frame(self):
        self.frame_main = tk.Frame(self._root)
        self.label_title = tk.Label(self.frame_main, text="xxxxxPosition plot")
        self.frame_main.pack(fill="both")
        self.label_title.pack(fill="both")

        return self.frame_main
    
    def get_descriptor_str(self):
        return self._descriptor.set_element_name(self.get_underlying_element().get_name())
    
    def get_underlying_element(self):
        return pipeline_elements.PosPlotElement()

class Position2DPlotterView(ElementView):
    def __init__(self, root):
        super().__init__(root)

    def get_frame(self):
        self.frame_main = tk.Frame(self._root)
        self.label_title = tk.Label(self.frame_main, text="2D Position plot")
        self.var_axes = StringVar()
        self.var_axes.set("xy")
        self.om_axes_select = tk.OptionMenu(self.frame_main, self.var_axes, "xy", "xz", "yz")
        self.om_axes_select.configure(width=StyleScheme.size_element_entry_width)
        self.frame_main.pack(fill="both")
        self.label_title.pack(fill="both")
        self.om_axes_select.pack()

        return self.frame_main
    
    def get_descriptor_str(self):
        return self._descriptor.set_element_name(self.get_underlying_element().get_name()).add_arg(self.var_axes.get())
    
    def get_underlying_element(self):
        return pipeline_elements.ShowPos2DElement()

class Position3DPlotterView(ElementView):
    def __init__(self, root):
        super().__init__(root)
    
    def get_frame(self):
        self.frame_main = tk.Frame(self._root)
        self.label_title = tk.Label(self.frame_main, text="3D Position plot")
        self.frame_main.pack(fill="both")
        self.label_title.pack(fill="both")

        return self.frame_main
    
    def get_descriptor_str(self):
        return self._descriptor.set_element_name(self.get_underlying_element().get_name())
    
    def get_underlying_element(self):
        return pipeline_elements.Plot3dMovementElement()