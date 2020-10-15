import argparse

parser = argparse.ArgumentParser(description="Controller unit for the path trackers##")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--cli", help="Launches the command line interface", action="store_true")
group.add_argument("--gui", help="Launches the graphical interface", action="store_true")

args = parser.parse_args()

if vars(args)["cli"]:
    import mc_cli
    cli0 = mc_cli.ControlCLI()
    cli0.start()
elif vars(args)["gui"]:
    import mc_gui
    mc_gui.start()
else:
    print("nani")