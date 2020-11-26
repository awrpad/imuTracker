from abc import ABC, abstractmethod
import pipeline_elements
import tkinter as tk
from tkinter import BooleanVar, StringVar, ttk, filedialog
from visualizer_core import VisualizerCore

# This is an implementation for a scrollable tkinter Frame
# It is from here: https://blog.tecladocode.com/tkinter-scrollable-frames/
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self._canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self.scrollable_frame = tk.Frame(self._canvas, background="red")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda _: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )

        self._canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self._canvas.configure(yscrollcommand=scrollbar.set)

        self._canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
    
    def __add_pipeline_page__(self, name):
        new_page = PipelineFrame(self.root, name).get()
        self.root.add(new_page, text=name)
        self.root.select(self.root.index(tk.END) - 1)
    
    def get(self):
        frame_main = tk.Frame(self.root, bg=StyleScheme.color_background)
        label_welcome = tk.Label(frame_main, text=self.str_welcome, bg=StyleScheme.color_background, fg=StyleScheme.color_foreground1)
        label_add_pipeline = tk.Label(frame_main, text=self.str_add_pipeline, bg=StyleScheme.color_background, font=StyleScheme.font_subtitle)
        label_newpipeline_name = tk.Label(frame_main, text=self.str_newpipeline_name, bg=StyleScheme.color_background)
        button_create = ttk.Button(frame_main, text=self.str_create, command=lambda: self.__add_pipeline_page__(entry_newpipeline_name.get()))
        entry_newpipeline_name = tk.Entry(frame_main, width=40, bg=StyleScheme.color_background, fg=StyleScheme.color_foreground2)

        label_welcome.configure(font=StyleScheme.font_title)

        label_welcome.grid(row=0, column=0, columnspan=3, sticky="wens")
        label_add_pipeline.grid(row=1, column=0, columnspan=3, sticky="wens")
        label_newpipeline_name.grid(row=2, column=0, sticky="wens")
        entry_newpipeline_name.grid(row=2, column=1, sticky="wens")
        button_create.grid(row=2, column=2, sticky="wens")

        return frame_main

class PipelineFrame:
    def __init__(self, root, pipeline_name):
        self.pipeline_name = pipeline_name
        self.root = root
        self.__elements = {}
    
    def log(self, msg, loglevel = 1):
        tag = None
        if loglevel < 1:
            tag = "debug"
        elif loglevel == 2:
            tag = "warning"
        elif loglevel > 2:
            tag = "error"

        self.text_output.config(state=tk.NORMAL)
        self.text_output.insert("end", msg + "\n", tag)
        self.text_output.see("end")
        self.text_output.config(state=tk.DISABLED)
        self.text_output.update()
        print(msg)

    def __delete_element__(self, element):
        del(self.__elements[element])
        element.destroy()
    
    def add_element_view(self, element_name):
        new_element_frame = tk.LabelFrame(self.frame_pipeline.scrollable_frame)
        
        button_delete_element = tk.Button(new_element_frame, text="×", bg="red", padx=1, pady=1, command=lambda: self.__delete_element__(new_element_frame))

        new_element = PipelineElementViewRepository().get_view_for(element_name, new_element_frame)
        element = new_element.get_underlying_element()
        if element.is_sink():
            new_element_frame.configure(bg=StyleScheme.color_sink_background)
        elif element.is_source():
            new_element_frame.configure(bg=StyleScheme.color_source_background)
        
        new_element_frame.configure(text=element.get_friendly_name())

        new_element_frame.pack(fill="x")
        button_delete_element.pack(side="right", anchor="nw")
        new_element.get_frame().pack(fill="x")

        self.__elements[new_element_frame] = new_element
    
    def generate_pipeline_str(self):        
        pipeline_str = ""
        try:
            for i, key in enumerate(self.__elements):
                pipeline_str += self.__elements[key].get_descriptor_str() + " | "
        except Exception as e:
            self.log("Could not generate pipeline string.\nCause: " + str(e) + "\nAt position: " + str(i + 1), 3)
            return
        
        # Not the most beautiful piece of code I've ever written
        pipeline_str = pipeline_str.strip().strip("|").strip()

        self.log("GENERATED PIPELINE:\n'" + pipeline_str + "'", 0)
        return pipeline_str
    
    def execute_pipeline(self):
        line = self.generate_pipeline_str()
        if line is None:
            self.log("Execution failed. Cause: No pipeline string was generated", 3)
            return
        
        self.core.write_to_peline(self.pipeline_name, line)
        self.core.run_pipeline(self.pipeline_name)
        self.core.clear_pipeline(self.pipeline_name)
    
    def get(self):
        self.frame_main = tk.Frame(self.root, bg=StyleScheme.color_background)
        
        frame_pipeline_composer = tk.LabelFrame(self.frame_main, text="Pipeline Composer", bg="yellow")
        frame_container = tk.LabelFrame(self.frame_main, text="Pipeline", bg="black")
        self.frame_pipeline = ScrollableFrame(frame_container)
        self.frame_pipeline_execution = tk.LabelFrame(self.frame_main, text="Execution", bg="blue")

        label_pipelinename = tk.Label(self.frame_main, text=self.pipeline_name, font=StyleScheme.font_title)
        listbox_selector = tk.Listbox(frame_pipeline_composer, width=40, height=30)
        button_add = tk.Button(frame_pipeline_composer, text="Add selected element", command=lambda: self.add_element_view(
            listbox_selector.get(tk.ACTIVE).replace("(", "").replace(")", "").split()[-1]
        ))
        button_execute = tk.Button(self.frame_pipeline, text="Execute", command=self.execute_pipeline)
        self.text_output = tk.Text(self.frame_pipeline_execution, bg="black", fg="white")

        # Welcome message on the pipeline output
        self.text_output.insert(tk.END, "Welcome! The output of the pipeline will be shown here.\n")
        self.text_output.tag_config("debug", foreground="cyan")
        self.text_output.tag_config("warning", foreground="yellow")
        self.text_output.tag_config("error", foreground="red")
        self.text_output.see(tk.END)
        self.text_output.config(state=tk.DISABLED)
        self.text_output.update()

        self.core = VisualizerCore(input, self.log)
        self.core.add_pipeline(self.pipeline_name)
        
        possibilities = self.core.get_pipeline(self.pipeline_name).get_possibilities()
        
        for pos in possibilities:
            listbox_selector.insert(tk.END, pos.get_friendly_name() + " (" + pos.get_name() + ")")
        
        label_pipelinename.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)
        frame_pipeline_composer.grid(row=1, column=0, sticky=tk.NSEW)
        frame_container.grid(row=1, column=1, sticky=tk.NSEW)
        self.frame_pipeline.pack(fill="both", expand=True)
        self.frame_pipeline_execution.grid(row=1, column=2, sticky=tk.NSEW)

        self.frame_main.grid_rowconfigure(0, weight=0)
        self.frame_main.grid_rowconfigure(1, weight=1)
        self.frame_main.grid_columnconfigure(0, weight=1)
        self.frame_main.grid_columnconfigure(1, weight=3)
        self.frame_main.grid_columnconfigure(2, weight=3)

        listbox_selector.pack()
        button_add.pack()
        button_execute.pack(fill="x")
        self.text_output.pack()

        return self.frame_main

class PipelineElementViewRepository:
    __views = []
    def __init__(self):
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
        if len(self.args) > 0:
            toreturn += " "
        for i, arg in enumerate(self.args):
            if i > 0:
                toreturn += ":"
            toreturn += arg
        
        return toreturn
    
    def clear(self):
        self.element_name = None
        self.args.clear()

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
        self._descriptor.clear()
        filename = self.entry_filename.get()
        if filename is None or filename == "":
            raise Exception("loadf: Filename is not set.")
        return self._descriptor.set_element_name(self.get_underlying_element().get_name()).add_arg(filename).get_str()

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
        self._descriptor.clear()
        apply_to_axes = ""
        if self.applytox.get():
            apply_to_axes += "x"
        if self.applytoy.get():
            apply_to_axes += "y"
        if self.applytoz.get():
            apply_to_axes += "z"

        window = self.entry_window.get()

        try:
            int(window)
        except:
            raise Exception("mavg: Window has to be an integer")

        if apply_to_axes == "":
            raise Exception("mavg: No axis is set")
        
        return self._descriptor.set_element_name(self.get_underlying_element().get_name()).add_arg(window).add_arg(apply_to_axes).get_str()
    
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
        return self._descriptor.set_element_name(self.get_underlying_element().get_name()).get_str()
    
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
        return self._descriptor.set_element_name(self.get_underlying_element().get_name()).get_str()
    
    def get_underlying_element(self):
        return pipeline_elements.AccelPlotterElement()

class PositionPlotterView(ElementView):
    def __init__(self, root):
        super().__init__(root)

    def get_frame(self):
        self.frame_main = tk.Frame(self._root)
        self.label_title = tk.Label(self.frame_main, text="Position plot")
        self.frame_main.pack(fill="both")
        self.label_title.pack(fill="both")

        return self.frame_main
    
    def get_descriptor_str(self):
        return self._descriptor.set_element_name(self.get_underlying_element().get_name()).get_str()
    
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
        self._descriptor.clear()
        return self._descriptor.set_element_name(self.get_underlying_element().get_name()).add_arg(self.var_axes.get()).get_str()
    
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
        return self._descriptor.set_element_name(self.get_underlying_element().get_name()).get_str()
    
    def get_underlying_element(self):
        return pipeline_elements.Plot3dMovementElement()