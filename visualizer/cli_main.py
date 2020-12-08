from visualizer_core import *

def read(msg = ""):
    return input(msg + "~> ")

class AppCLI:
    def __init__(self, logfun):
        self.log = logfun
        self.core = VisualizerCore(read, logfun)
    
    def mainloop(self, name = None):
        if name is None:
            name = "cli_pipeline"
        self.log("Entered CLI main loop", 0)
        self.core.add_pipeline(name)
        p = self.core.get_pipeline(name)
        
        if p is None:
            raise Exception("Nonexistent pipeline in pipeline repository")
        
        cmd = self.core.read()
        while cmd != ":exit":
            self.log("Read line: " + cmd, 0)
            try:    
                if cmd == ":run":
                    self.core.run_pipeline(name)
                elif cmd == ":clear":
                    self.core.clear_pipeline(name)
                else:
                    self.core.write_to_peline(name, cmd)
            except Exception as e:
                self.log("Error during executing pipeline '" + p.get_name() + "'. Cause: " + str(e))
            
            cmd = self.core.read()