from collections import namedtuple

PipelineReturnValue = namedtuple("PipelineReturnValue", ["return_code", "data"])

class PipelineElement:
    def __init__(self, name):
        self.__name = name
    #@abstractmethod
    def apply(self, data, args = None):
        print("Hello, I am " + self.__name + ". Got arg: ", args)
        return(PipelineReturnValue(0, []))

    def get_name(self):
        return self.__name

class Pipeline:
    # Stores all known elements
    __possibilities = []

    def __init__(self):
        # The steps to execute in a (step, arguments) form
        self.__steps = []
        self.__data = []
    
    def execute(self):
        temp_data = self.__data
        for step in self.__steps:
            checker = step[0].apply(temp_data, step[1])
            if checker.return_code == 0:
                temp_data = checker.data
            else:
                print("Error during pipeline execution in the step '" + step[0].get_name()+ "' with args '" + step[1] + "'.\nError code: " + str(checker.return_code) + "\nData was not modified.")
                return
        self.__data = temp_data
        print("DONE.")
    
    def get_data(self):
        return self.__data
    
    def introduce(self, pipeline_element):
        for already_known in Pipeline.__possibilities:
            if already_known.get_name() == pipeline_element.get_name():
                print("I already know an element with the name of '" + already_known.get_name() + "'.")
                return
        Pipeline.__possibilities.append(pipeline_element)
    
    def add_step(self, step_name, step_args = None):
        for pos in Pipeline.__possibilities:
            if(pos.get_name() == step_name):
                self.__steps.append((pos, step_args))
                return
        print("No step with the name '" + step_name + "'.")
    
    def parse_string(self, line):
        pass
    
a = PipelineElement("AAA")
b = PipelineElement("BBB")
c = PipelineElement("BBB")

p = Pipeline()
p.introduce(a)
p.introduce(b)
p.introduce(c)
p.add_step("AAA")
p.add_step("BBB")
p.add_step("BBB")
p.add_step("AAA")
p.add_step("BBB")
p.add_step("BBB")
p.add_step("CDC")
p.add_step("BAA")
p.add_step("BBB")
p.add_step("BBB")
p.add_step("AAA")

p.execute()
