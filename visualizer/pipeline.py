from collections import namedtuple

PipelineReturnValue = namedtuple("PipelineReturnValue", ["return_code", "data"])

class PipelineElement:
    def __init__(self, name, sink = False, source = False):
        self.__name = name
        self.log = print
        self.__is_source = source
        self.__is_sink = sink
    #@abstractmethod
    def apply(self, data, args = None):
        self.log("Hello, I am " + self.__name + ". Got arg: " + str(args))
        return(PipelineReturnValue(0, []))

    def get_name(self):
        return self.__name
    
    def set_log_function(self, logfun):
        self.log = logfun
    
    def is_source(self):
        return self.__is_source
    
    def is_sink(self):
        return self.__is_sink
    
    """def is_valid_with_args(self, args_in):
        return True"""

class PipelineSource(PipelineElement):
    def __init__(self, name):
        super().__init__(name, source=True)

class PipelineSink(PipelineElement):
    def __init__(self, name):
        super().__init__(name, sink=True)
        self.__out_object = None
    
    def get_output(self):
        return self.__out_object

class Pipeline:
    # Stores all known elements
    __possibilities = []

    def __init__(self, name, logfun):
        # The steps to execute in a (step, arguments) form
        self.__steps = []
        self.__data = []
        self.__name = name
        self.log = logfun
        self.__outputs = []
        self.log("Created and initialized pipeline with name '" + self.__name + "'.", loglevel = 0)
    
    def execute(self):
        self.log("Executing the pipeline '" + self.__name + "'...")
        temp_data = self.__data
        temp_outs = []
        for step in self.__steps:
            step[0].set_log_function(self.log)
            checker = step[0].apply(temp_data, step[1])
            if checker.return_code == 0:
                if step[0].is_sink():
                    temp_outs.append(step[0].get_output())
                else:
                    temp_data = checker.data
                    self.log("Data set., size: " + str(len(temp_data)))
            else:
                self.log("Error during pipeline execution in the step '" + step[0].get_name()+ "' with args '" + step[1] + "'.\nError code: " + str(checker.return_code) + "\nData was not modified.", 3)
                return
        self.__data = temp_data
        self.log("DONE.")
    
    def get_data(self):
        return self.__data
    
    def introduce(self, pipeline_element):
        for already_known in Pipeline.__possibilities:
            if already_known.get_name() == pipeline_element.get_name():
                self.log("Could not add pipeline element '" + already_known.get_name() + "' because it already exists.", 2)
                return
        Pipeline.__possibilities.append(pipeline_element)
        Pipeline.__possibilities[-1].set_log_function(self.log)
        self.log("Pipeline element added:\t" + Pipeline.__possibilities[-1].get_name() + "\t\tSink: " + str(Pipeline.__possibilities[-1].is_sink()) + "\tSource: " + str(Pipeline.__possibilities[-1].is_source()))
    
    def add_step(self, step_name, step_args = None):
        for pos in Pipeline.__possibilities:
            if(pos.get_name() == step_name):
                self.__steps.append((pos, step_args))
                return
        self.log("No step with the name '" + step_name + "'.")
    
    def parse_string(self, line):
        elements = line.split("|")
        elements = [x.strip() for x in elements]
        for e in elements:
            element_name = e.split(" ")[0]
            args = e.replace(element_name, "", 1).strip()
            self.add_step(element_name, args)
    
    def clear_steps(self):
        self.__steps.clear()
    
    def get_name(self):
        return self.__name
    
    @staticmethod
    def get_possibilities():
        return Pipeline.__possibilities

