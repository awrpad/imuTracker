import argparse
import time
import logging

# Lambda for getting current time in milliseconds
# Copied from: https://stackoverflow.com/questions/5998245/get-current-time-in-milliseconds-in-python
timestamp = lambda: str(int(round(time.time() * 1000)))
start_timestamp = timestamp()

logging.basicConfig(filename="vis_main-" + start_timestamp + ".log", encoding="utf-8", level=logging.DEBUG, format="%(asctime)s -> %(levelname)s (%(name)s): %(message)s")
logging.info("Visualizer core started, starting timestamp: " + start_timestamp)

parser = argparse.ArgumentParser(description="Data manipulation and visualisation tool.")
parser.add_argument("--cli", help="Launches the command line interface instead of the GUI", action="store_true")

args = parser.parse_args()
logging.info("Command line arguments: '" + str(args) + "'.")

def log_to_file(msg, loglevel):
    try:
        if loglevel == 0:
            logging.debug(msg)
        elif loglevel == 1:
            logging.info(msg)
        elif loglevel == 2:
            logging.warning(msg)
        elif loglevel == 3:
            logging.error(msg)
        elif loglevel == 4:
            logging.critical(msg)
        else:
            logging.warning("Invalid loglevel: '" + str(loglevel) + "'. The message was: '" + msg + "'.")
    except Exception as e:
        logging.error("Error during logging: " + str(e))

def read(msg = ""):
    return input("~> " + msg)

try:
    if vars(args)["cli"]:
        # Launch Command Line interface
        def log(msg, loglevel = 1):
            if loglevel > 0:
                print(timestamp() + ": <- " + msg)
            log_to_file(msg, loglevel)
        log("Started in CLI mode", 0)
        print("+-------------------------------------------------------------------+")
        print("|                                                                   |")
        print("| Data manipulation and visualisation tool - Command Line Interface |")
        print("|                                                                   |")
        print("+-------------------------------------------------------------------+")
        
        log("Starting...")
        from visualizer_core import *
        core = VisualizerCore(read, log)
        pipelinename = "Pipeline" + start_timestamp
        core.add_pipeline(pipelinename)
        log("Ready.")
        core.mainloop("asd")
    else:
        # Launch GUI
        def log(msg, loglevel = 1):
            log_to_file(msg, loglevel)
        log("Started in GUI mode", 0)
        from gui_main import AppWindow
        aw = AppWindow()
        aw.start()

except Exception as e:
    print("\n\nCRITICAL ERROR, application shuts down.\n\n")
    logging.critical("Critical error during main application part. Cause:")
    logging.exception(e)


logging.info("Visualizer closed.")


