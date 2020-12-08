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
                self.__log_function(f"Invalid name for switching: '{where_to}'")
            else:
                self.__current_send_location = srvr
    
    def save_lastrep_to_file(self, filename):
        if(self.__last_response is None):
            self.__log_function("There is no response yet.")
            return
        
        #save to file
        f = open(filename, "w")
        f.write(self.__last_response)
        f.close()
    
    def add_server(self, line):
        self.core.add_server(line=line)

    def start(self):
        # Setting up commands
        self.__commands["sw"] = self.set_send_location
        self.__commands["listen"] = self.core.listen_to_login
        self.__commands["saveresp"] = self.save_lastrep_to_file
        self.__commands["addsrv"] = self.add_server
        while True:
            line = self.__read_function(self.__get_location_string__() + "/>").strip()
            cmd = line.split(" ")[0]
            is_self_command = (self.__get_location_string__() == "~") or cmd.startswith(":")

            if cmd.startswith("!"):
                    self.core.send_to_all(line)
                    continue
            if(is_self_command):
                if cmd.startswith(":"):
                    cmd = cmd[1:]
                if cmd == "exit":
                    break
                elif cmd in self.__commands:
                    try:
                        args = line.replace(cmd, "").strip()
                        if args.startswith(":"):
                            args = args[1:]
                        self.__commands[cmd](args)
                    except Exception as e:
                        self.__log_function(f"Error during executing the command '{line}'\nCause: " + str(e))
                else:
                    self.__log_function("Self command not found.")
            else:
                self.__last_response = self.core.send_to(self.__current_send_location, line)
                self.__log_function(self.__last_response)

def greet(cmd):
    print("Greetings!")
