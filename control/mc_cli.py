import mc_core as Core

class ControlCLI:
    __instance = None
    __log_function = print
    __read_function = input
    __commands = {}
    __current_send_location = "~"
    core = Core.ControlCore.get_instance()

    def __get_location_string__(self):
        if self.__current_send_location == "~":
            return self.__current_send_location
        else:
            return self.__current_send_location.name

    def set_log_function(self, func):
        __log_function = func

    def set_read_function(self, func):
        __read_function = func
    
    def set_send_location(self, where_to):
        # If it was invoked by a CLI command, the where_to looks like 'sw device_name'
        # And only the 'device_name' is needed
        if " " in where_to:
            where_to = where_to.split(" ")[-1]
        if where_to == "~":
            self.__current_send_location = "~"
        else:
            srvr = self.core.get_server_by_name(where_to)
            if srvr is None:
                self.__log_function("Invalid name for switching")
            else:
                self.__current_send_location = srvr

    def start(self):
        # Setting up commands
        self.__commands["sw"] = self.set_send_location
        self.__commands["listen"] = self.core.listen_to_login
        while True:
            line = self.__read_function(self.__get_location_string__() + "/>").strip()
            cmd = line.split(" ")[0]
            self_command = (self.__get_location_string__() == "~") or cmd.startswith(":")
            if(self_command):
                if cmd.startswith(":"):
                    cmd = cmd[1:]
                if cmd == "exit":
                    break
                elif cmd in self.__commands:
                    try:
                        self.__commands[cmd](line)
                    except Exception as e:
                        self.__log_function(f"Error during executing the command '{line}'\nCause: " + str(e))
                else:
                    self.__log_function("Command not found.")
            else:
                if cmd.startswith("!"):
                    self.core.send_to_all(line)
                else:
                    self.core.send_to(self.__current_send_location, line)

def greet(cmd):
    print("Greetings!")
