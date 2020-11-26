from pipeline import Pipeline
from pipeline_elements import *

class VisualizerCore:
    def __init__(self, read_function, log_function):
        self.read = read_function
        self.log = log_function
        self.p = []

    def add_pipeline(self, name):
        self.p.append(Pipeline(name, self.log))
        self.p[-1].introduce(LoadfromfileElement())
        self.p[-1].introduce(QuaternionPlotterElement())
        self.p[-1].introduce(AccelPlotterElement())
        self.p[-1].introduce(SliceElement())
        self.p[-1].introduce(PrintInfoElement())
        self.p[-1].introduce(MovingAverageElement())
        self.p[-1].introduce(AutoHeigthAdjustionElement())
        self.p[-1].introduce(ConvertElement())
        self.p[-1].introduce(ZeroizeElement())
        self.p[-1].introduce(QuaternionAdjustionElement())
        self.p[-1].introduce(FrameOfReferenceRotationElement())
        self.p[-1].introduce(AccelToPosElement())
        self.p[-1].introduce(PosPlotElement())
        self.p[-1].introduce(ShowPos2DElement())
        self.p[-1].introduce(SecondIntegralBasedHeigthAdjustionElement())
        self.p[-1].introduce(OrientationPlotterElement())
        self.p[-1].introduce(Plot3dMovementElement())

    def get_pipeline(self, name):
        p = None
        for pipeline in self.p:
            if pipeline.get_name() == name:
                p = pipeline
                break
        
        return p

    def mainloop(self, name):
        self.log("Entered core main loop", 0)
        p = self.get_pipeline(name)
        
        if p is None:
            raise Exception("Nonexistent pipeline in pipeline repository")
        
        cmd = self.read()
        while cmd != ":exit":
            self.log("Read line: " + cmd, 0)
            try:    
                if cmd == ":run":
                    self.run_pipeline(name)
                elif cmd == ":clear":
                    self.clear_pipeline(name)
                else:
                    self.write_to_peline(name, cmd)
            except Exception as e:
                self.log("Error during executing pipeline '" + p.get_name() + "'. Cause: " + str(e))
            
            cmd = self.read()
    
    # TODO: Break down main loop to smaller functions
    # The loop functionality should be handled by the CLI module

    def run_pipeline(self, pipeline_name):
        p = self.get_pipeline(pipeline_name)
        p.execute()
        p.clear_steps()
    
    def write_to_peline(self, pipeline_name, line):
        p = self.get_pipeline(pipeline_name)
        p.parse_string(line)
    
    def clear_pipeline(self, pipeline_name):
        p = self.get_pipeline(pipeline_name)
        p.clear_steps()
            